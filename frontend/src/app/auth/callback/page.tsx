'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

export const dynamic = 'force-dynamic'

export default function CallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [error, setError] = useState<string | null>(null)
  const hasProcessed = useRef(false)

  useEffect(() => {
    const code = searchParams.get('code')

    if (!code) {
      router.push('/login?error=missing_code')
      return
    }

    // Prevent double-processing using both ref and localStorage
    const processedKey = `oauth_processed_${code}`
    if (hasProcessed.current || sessionStorage.getItem(processedKey)) {
      return
    }

    hasProcessed.current = true
    sessionStorage.setItem(processedKey, 'true')

    handleCallback(code)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, router])

  async function handleCallback(code: string) {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(
        `${apiUrl}/auth/github/callback?code=${encodeURIComponent(code)}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error('Backend error:', errorData)
        throw new Error(errorData.detail || 'Authentication failed')
      }

      const data = await response.json()

      // Store tokens in localStorage
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)

      // Set tokens in cookies for middleware
      document.cookie = `access_token=${data.access_token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`
      document.cookie = `refresh_token=${data.refresh_token}; path=/; max-age=${60 * 60 * 24 * 30}; SameSite=Lax`

      // Clear the OAuth code from session storage after successful processing
      sessionStorage.removeItem(`oauth_processed_${code}`)

      // Redirect to workspaces (dashboard)
      router.replace('/workspaces')
    } catch (err) {
      console.error('Auth callback failed:', err)
      const errorMessage = err instanceof Error ? err.message : 'Authentication failed'
      setError(errorMessage)
      // Redirect to login with error after 2 seconds
      setTimeout(() => {
        router.push('/login?error=auth_failed')
      }, 2000)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="text-center">
        {error ? (
          <>
            <div className="mb-4 text-lg font-semibold text-red-600">{error}</div>
            <p className="text-slate-600">Redirecting to login page...</p>
          </>
        ) : (
          <>
            <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-slate-300 border-t-slate-900" />
            <p className="text-lg font-medium text-slate-700">Signing you in...</p>
            <p className="mt-2 text-sm text-slate-500">
              Please wait while we complete your authentication
            </p>
          </>
        )}
      </div>
    </div>
  )
}
