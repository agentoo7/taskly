/**
 * Error boundary for dashboard pages.
 */

'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { AlertCircle } from 'lucide-react'

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log error to console in development
    console.error('Dashboard error:', error)
  }, [error])

  return (
    <div className="container flex min-h-[calc(100vh-4rem)] items-center justify-center py-8">
      <Card className="max-w-md p-8 text-center">
        <div className="mb-4 flex justify-center">
          <div className="rounded-full bg-destructive/10 p-3">
            <AlertCircle className="h-8 w-8 text-destructive" />
          </div>
        </div>
        <h2 className="mb-2 text-xl font-semibold">Something went wrong</h2>
        <p className="mb-6 text-sm text-muted-foreground">
          {error.message || 'An unexpected error occurred. Please try again.'}
        </p>
        <div className="flex flex-col gap-2 sm:flex-row sm:justify-center">
          <Button onClick={reset} variant="default">
            Try again
          </Button>
          <Button onClick={() => (window.location.href = '/workspaces')} variant="outline">
            Go to workspaces
          </Button>
        </div>
      </Card>
    </div>
  )
}
