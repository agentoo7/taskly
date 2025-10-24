/**
 * useAuth hook for managing authentication state.
 */

'use client'

import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'

import { api } from '@/lib/api/client'

interface User {
  id: string
  username: string
  email: string
  avatar_url: string | null
  github_id: number
}

export function useAuth() {
  const router = useRouter()
  const queryClient = useQueryClient()

  // Fetch current user if tokens exist
  const {
    data: user,
    isLoading,
    error,
  } = useQuery<User | null>({
    queryKey: ['current-user'],
    queryFn: async () => {
      // Check if tokens exist
      if (typeof window === 'undefined') return null

      const accessToken = localStorage.getItem('access_token')
      if (!accessToken) return null

      try {
        return await api.get<User>('/api/me')
      } catch (err) {
        // If /api/me fails (e.g., invalid token), return null
        // The api client will handle refresh attempts automatically
        console.error('Failed to fetch current user:', err)
        return null
      }
    },
    retry: false,
    staleTime: 1000 * 60 * 5, // Consider data fresh for 5 minutes
  })

  /**
   * Navigate to login page.
   */
  const login = () => {
    router.push('/login')
  }

  /**
   * Logout user by revoking refresh token and clearing state.
   */
  const logout = async () => {
    const refreshToken =
      typeof window !== 'undefined'
        ? localStorage.getItem('refresh_token')
        : null

    // Call logout endpoint to revoke refresh token
    if (refreshToken) {
      try {
        await api.post(
          '/auth/logout',
          { refresh_token: refreshToken },
          { skipAuth: true }
        )
      } catch (err) {
        // Log error but continue with client-side logout
        console.error('Logout endpoint error:', err)
      }
    }

    // Clear tokens and cache
    api.logout()
    queryClient.clear()

    // Redirect to login
    router.push('/login')
  }

  return {
    user: user ?? null,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    logout,
  }
}
