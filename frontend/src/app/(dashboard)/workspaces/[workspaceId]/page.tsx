/**
 * Workspace dashboard page showing boards and workspace details.
 */

'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Plus, Settings as SettingsIcon, Calendar, Users } from 'lucide-react'
import { api } from '@/lib/api/client'
import { useWorkspaceWebSocket } from '@/hooks/use-workspace-websocket'
import { CreateBoardModal } from '@/components/board/create-board-modal'
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

interface Board {
  id: string
  workspace_id: string
  name: string
  columns: Array<{ id: string; name: string; position: number }>
  archived: boolean
  created_at: string
  updated_at: string
}

export default function WorkspaceDashboardPage() {
  const params = useParams()
  const router = useRouter()
  const workspaceId = params.workspaceId as string
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

  // Connect to WebSocket for real-time updates
  useWorkspaceWebSocket(workspaceId)

  const { data: workspace, isLoading: isLoadingWorkspace } = useQuery({
    queryKey: ['workspaces', workspaceId],
    queryFn: () => api.get<WorkspaceDetail>(`/api/workspaces/${workspaceId}`),
  })

  const { data: boards = [], isLoading: isLoadingBoards } = useQuery({
    queryKey: ['workspaces', workspaceId, 'boards'],
    queryFn: () => api.get<Board[]>(`/api/workspaces/${workspaceId}/boards`),
    enabled: !!workspaceId,
  })

  const isLoading = isLoadingWorkspace || isLoadingBoards

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

  const activeBoards = boards.filter((board) => !board.archived)
  const hasBoards = activeBoards.length > 0

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))

    if (diffInHours < 24) {
      if (diffInHours < 1) return 'Just now'
      return `${diffInHours}h ago`
    }
    const diffInDays = Math.floor(diffInHours / 24)
    if (diffInDays < 7) return `${diffInDays}d ago`
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  return (
    <>
      <div className="container mx-auto max-w-7xl px-4 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{workspace.name}</h1>
            <p className="mt-2 text-muted-foreground">
              {activeBoards.length} boards • {workspace.members.length} members
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" asChild>
              <Link href={`/workspaces/${workspaceId}/settings`}>
                <SettingsIcon className="mr-2 h-4 w-4" />
                Settings
              </Link>
            </Button>
            <Button onClick={() => setIsCreateModalOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Board
            </Button>
          </div>
        </div>

        {hasBoards ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {activeBoards.map((board) => (
              <Card
                key={board.id}
                className="group cursor-pointer transition-all hover:shadow-md hover:border-primary/50"
                onClick={() => router.push(`/workspaces/${workspaceId}/boards/${board.id}`)}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between">
                    <h3 className="text-lg font-semibold group-hover:text-primary transition-colors">
                      {board.name}
                    </h3>
                  </div>

                  <div className="mt-4 space-y-2 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>Updated {formatDate(board.updated_at)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <svg
                        className="h-4 w-4"
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
                      <span>{board.columns.length} columns</span>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
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
            <Button className="mt-6" size="lg" onClick={() => setIsCreateModalOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Board
            </Button>
          </Card>
        )}
      </div>

      <CreateBoardModal
        workspaceId={workspaceId}
        open={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
      />
    </>
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
