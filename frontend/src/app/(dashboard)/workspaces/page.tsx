/**
 * Workspaces landing page for authenticated users.
 */

'use client'

import { useAuth } from '@/lib/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Plus } from 'lucide-react'

export default function WorkspacesPage() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <WorkspacesPageSkeleton />
  }

  return (
    <div className="container mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Welcome, {user?.username}!</h1>
        <p className="mt-2 text-muted-foreground">
          Manage your workspaces and start collaborating on projects.
        </p>
      </div>

      {/* Empty State */}
      <Card className="flex flex-col items-center justify-center p-12 text-center">
        <div className="mb-4 rounded-full bg-muted p-6">
          <svg
            className="h-12 w-12 text-muted-foreground"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold">No workspaces yet</h3>
        <p className="mt-2 max-w-sm text-sm text-muted-foreground">
          Get started by creating your first workspace to organize your boards and collaborate with
          your team.
        </p>
        <Button className="mt-6" size="lg">
          <Plus className="mr-2 h-4 w-4" />
          Create Workspace
        </Button>
      </Card>
    </div>
  )
}

function WorkspacesPageSkeleton() {
  return (
    <div className="container mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <div className="h-10 w-64 animate-pulse rounded bg-muted" />
        <div className="mt-2 h-6 w-96 animate-pulse rounded bg-muted" />
      </div>
      <div className="h-64 animate-pulse rounded bg-muted" />
    </div>
  )
}
