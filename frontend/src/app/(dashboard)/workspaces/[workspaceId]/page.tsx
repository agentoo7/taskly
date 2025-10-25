/**
 * Workspace dashboard page showing boards and workspace details.
 */

'use client'

import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Plus, Settings as SettingsIcon } from 'lucide-react'
import { api } from '@/lib/api/client'
import { useWorkspaceWebSocket } from '@/hooks/use-workspace-websocket'
import Link from 'next/link'

interface WorkspaceDetail {
  id: string
  name: string
  created_by: string | null
  created_at: string
  updated_at: string
  boards: unknown[]
  members: unknown[]
}

export default function WorkspaceDashboardPage() {
  const params = useParams()
  const workspaceId = params.workspaceId as string

  // Connect to WebSocket for real-time updates
  useWorkspaceWebSocket(workspaceId)

  const { data: workspace, isLoading } = useQuery({
    queryKey: ['workspaces', workspaceId],
    queryFn: () => api.get<WorkspaceDetail>(`/api/workspaces/${workspaceId}`),
  })

  if (isLoading) {
    return <WorkspaceDashboardSkeleton />
  }

  if (!workspace) {
    return (
      <div className="container mx-auto max-w-7xl px-4 py-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold">Workspace not found</h2>
          <p className="mt-2 text-muted-foreground">
            The workspace you&apos;re looking for doesn&apos;t exist or you don&apos;t have access
            to it.
          </p>
          <Button asChild className="mt-4">
            <Link href="/workspaces">Back to Workspaces</Link>
          </Button>
        </div>
      </div>
    )
  }

  const hasBoards = workspace.boards && workspace.boards.length > 0

  return (
    <div className="container mx-auto max-w-7xl px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{workspace.name}</h1>
          <p className="mt-2 text-muted-foreground">
            {workspace.boards.length} boards • {workspace.members.length} members
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link href={`/workspaces/${workspaceId}/settings`}>
              <SettingsIcon className="mr-2 h-4 w-4" />
              Settings
            </Link>
          </Button>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Board
          </Button>
        </div>
      </div>

      {hasBoards ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {/* Placeholder for boards - will be implemented in Story 2.3 */}
          <Card className="p-6">
            <p className="text-muted-foreground">Boards will be displayed here</p>
          </Card>
        </div>
      ) : (
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
                d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold">No boards yet</h3>
          <p className="mt-2 max-w-sm text-sm text-muted-foreground">
            Get started by creating your first board to organize your tasks and collaborate.
          </p>
          <Button className="mt-6" size="lg">
            <Plus className="mr-2 h-4 w-4" />
            Create Board
          </Button>
        </Card>
      )}
    </div>
  )
}

function WorkspaceDashboardSkeleton() {
  return (
    <div className="container mx-auto max-w-7xl px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <div className="h-10 w-64 animate-pulse rounded bg-muted" />
          <div className="mt-2 h-6 w-48 animate-pulse rounded bg-muted" />
        </div>
        <div className="flex gap-2">
          <div className="h-10 w-24 animate-pulse rounded bg-muted" />
          <div className="h-10 w-32 animate-pulse rounded bg-muted" />
        </div>
      </div>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-48 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    </div>
  )
}
