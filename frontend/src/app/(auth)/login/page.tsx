'use client'

import { Github } from 'lucide-react'
import { useSearchParams } from 'next/navigation'
import { useState, Suspense } from 'react'

import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export const dynamic = 'force-dynamic'

function LoginContent() {
  const searchParams = useSearchParams()
  const error = searchParams.get('error')
  const [isLoading, setIsLoading] = useState(false)

  const handleGitHubLogin = () => {
    setIsLoading(true)
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    window.location.href = `${apiUrl}/auth/github/login`
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <Card className="w-full max-w-md p-8 shadow-lg">
        <div className="mb-8 text-center">
          <h1 className="mb-2 text-4xl font-bold text-slate-900">Taskly</h1>
          <p className="text-lg text-slate-600">Move a Card, Ship the Code</p>
        </div>

        {error && (
          <div className="mb-6 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800">
            {error === 'auth_failed' && (
              <>
                <strong>Authentication failed.</strong> Please try again or contact support if the
                problem persists.
              </>
            )}
            {error === 'missing_code' && (
              <>
                <strong>Missing authorization code.</strong> Please try signing in again.
              </>
            )}
            {error !== 'auth_failed' && error !== 'missing_code' && (
              <>
                <strong>An error occurred.</strong> {error}
              </>
            )}
          </div>
        )}

        <Button
          onClick={handleGitHubLogin}
          disabled={isLoading}
          className="w-full bg-slate-900 text-white hover:bg-slate-800"
          size="lg"
        >
          {isLoading ? (
            <>
              <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Redirecting...
            </>
          ) : (
            <>
              <Github className="mr-2 h-5 w-5" />
              Sign in with GitHub
            </>
          )}
        </Button>

        <p className="mt-6 text-center text-xs text-slate-500">
          By signing in, you agree to our{' '}
          <button type="button" className="underline hover:text-slate-700">
            Terms of Service
          </button>{' '}
          and{' '}
          <button type="button" className="underline hover:text-slate-700">
            Privacy Policy
          </button>
          .
        </p>

        <div className="mt-8 border-t border-slate-200 pt-6">
          <p className="text-center text-sm text-slate-600">
            Taskly uses GitHub OAuth for secure authentication.
            <br />
            We only access your basic profile information.
          </p>
        </div>
      </Card>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <Card className="w-full max-w-md p-8 shadow-lg">
          <div className="text-center">
            <h1 className="mb-2 text-4xl font-bold text-slate-900">Taskly</h1>
            <p className="text-lg text-slate-600">Loading...</p>
          </div>
        </Card>
      </div>
    }>
      <LoginContent />
    </Suspense>
  )
}
