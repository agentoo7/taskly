/**
 * API client with automatic token management and refresh logic.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface RequestOptions extends RequestInit {
  skipAuth?: boolean
}

class ApiClient {
  private baseUrl: string
  private refreshPromise: Promise<void> | null = null

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  /**
   * Get access token from localStorage.
   */
  private getAccessToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('access_token')
  }

  /**
   * Get refresh token from localStorage.
   */
  private getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('refresh_token')
  }

  /**
   * Store tokens in localStorage and cookies.
   */
  private setTokens(accessToken: string, refreshToken?: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem('access_token', accessToken)
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken)
    }

    // Set cookies for middleware
    document.cookie = `access_token=${accessToken}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`
    if (refreshToken) {
      document.cookie = `refresh_token=${refreshToken}; path=/; max-age=${60 * 60 * 24 * 30}; SameSite=Lax`
    }
  }

  /**
   * Clear tokens from localStorage and cookies.
   */
  private clearTokens(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')

    // Clear cookies
    document.cookie = 'access_token=; path=/; max-age=0'
    document.cookie = 'refresh_token=; path=/; max-age=0'
  }

  /**
   * Refresh access token using refresh token.
   */
  private async refreshAccessToken(): Promise<void> {
    // If a refresh is already in progress, wait for it
    if (this.refreshPromise) {
      return this.refreshPromise
    }

    this.refreshPromise = (async () => {
      try {
        const refreshToken = this.getRefreshToken()

        if (!refreshToken) {
          throw new Error('No refresh token available')
        }

        const response = await fetch(`${this.baseUrl}/auth/refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        })

        if (!response.ok) {
          throw new Error('Token refresh failed')
        }

        const data = await response.json()
        this.setTokens(data.access_token)
      } catch (error) {
        // If refresh fails, clear tokens and redirect to login
        this.clearTokens()
        if (typeof window !== 'undefined') {
          window.location.href = '/login?error=session_expired'
        }
        throw error
      } finally {
        this.refreshPromise = null
      }
    })()

    return this.refreshPromise
  }

  /**
   * Make an API request with automatic token injection and refresh logic.
   */
  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { skipAuth = false, headers = {}, ...restOptions } = options

    const url = `${this.baseUrl}${endpoint}`

    // Build headers
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(headers as Record<string, string>),
    }

    // Add Authorization header if not skipping auth
    if (!skipAuth) {
      const accessToken = this.getAccessToken()
      if (accessToken) {
        requestHeaders['Authorization'] = `Bearer ${accessToken}`
      }
    }

    // Make the request
    let response = await fetch(url, {
      ...restOptions,
      headers: requestHeaders,
    })

    // If 401 (Unauthorized), try to refresh token and retry once
    if (response.status === 401 && !skipAuth) {
      try {
        await this.refreshAccessToken()

        // Retry the original request with new token
        const newAccessToken = this.getAccessToken()
        if (newAccessToken) {
          requestHeaders['Authorization'] = `Bearer ${newAccessToken}`
        }

        response = await fetch(url, {
          ...restOptions,
          headers: requestHeaders,
        })
      } catch (refreshError) {
        // If refresh fails, the refreshAccessToken method handles redirect
        throw refreshError
      }
    }

    // Handle non-OK responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Request failed with status ${response.status}`)
    }

    // Handle 204 No Content (e.g., DELETE requests)
    if (response.status === 204) {
      return undefined as T
    }

    // Parse and return response
    return response.json()
  }

  /**
   * GET request.
   */
  async get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  /**
   * POST request.
   */
  async post<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  /**
   * PUT request.
   */
  async put<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  /**
   * PATCH request.
   */
  async patch<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  /**
   * DELETE request.
   */
  async delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }

  /**
   * Logout - clear tokens.
   */
  logout(): void {
    this.clearTokens()
  }
}

// Export singleton instance
export const api = new ApiClient(API_BASE_URL)
