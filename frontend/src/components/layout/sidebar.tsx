/**
 * Sidebar component with workspace switcher.
 * Displays user's workspaces and allows quick navigation between them.
 */

'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { ChevronLeft, ChevronRight, Plus, Briefcase } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api/client'
import { cn } from '@/lib/utils'
import { useSidebarStore } from '@/store/sidebar-store'
import { CreateWorkspaceModal } from '@/components/workspace/create-workspace-modal'

interface Workspace {
  id: string
  name: string
  created_at: string
  updated_at: string
}

export function Sidebar() {
  const params = useParams()
  const router = useRouter()
  const { isCollapsed, toggle } = useSidebarStore()
  const currentWorkspaceId = params.workspaceId as string | undefined
  const [showCreateModal, setShowCreateModal] = useState(false)

  const { data: workspaces, isLoading } = useQuery<Workspace[]>({
    queryKey: ['workspaces'],
    queryFn: () => api.get<Workspace[]>('/api/workspaces'),
  })

  const handleWorkspaceClick = (workspaceId: string) => {
    router.push(`/workspaces/${workspaceId}`)
  }

  const handleCreateWorkspace = () => {
    setShowCreateModal(true)
  }

  if (isCollapsed) {
    return (
      <>
        <aside className="flex h-screen w-16 flex-col border-r bg-muted/40">
          <div className="flex h-14 items-center justify-center border-b px-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggle}
              className="h-8 w-8"
              aria-label="Expand sidebar"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
          <nav className="flex-1 space-y-2 overflow-y-auto p-2">
            {isLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-10 w-10 animate-pulse rounded-lg bg-muted" />
                ))}
              </div>
            ) : (
              workspaces?.map((workspace) => (
                <button
                  key={workspace.id}
                  onClick={() => handleWorkspaceClick(workspace.id)}
                  className={cn(
                    'flex h-10 w-10 items-center justify-center rounded-lg text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground',
                    currentWorkspaceId === workspace.id
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  )}
                  title={workspace.name}
                >
                  <Briefcase className="h-4 w-4" />
                </button>
              ))
            )}
          </nav>
          <div className="border-t p-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleCreateWorkspace}
              className="h-10 w-10"
              title="Create workspace"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </aside>
        <CreateWorkspaceModal open={showCreateModal} onOpenChange={setShowCreateModal} />
      </>
    )
  }

  return (
    <>
      <aside className="flex h-screen w-64 flex-col border-r bg-muted/40">
        {/* Header */}
        <div className="flex h-14 items-center justify-between border-b px-4">
          <h2 className="text-sm font-semibold">Workspaces</h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggle}
            className="h-8 w-8"
            aria-label="Collapse sidebar"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>

        {/* Workspace List */}
        <nav className="flex-1 space-y-1 overflow-y-auto p-3">
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-10 animate-pulse rounded-lg bg-muted" />
              ))}
            </div>
          ) : workspaces && workspaces.length > 0 ? (
            workspaces.map((workspace) => (
              <button
                key={workspace.id}
                onClick={() => handleWorkspaceClick(workspace.id)}
                className={cn(
                  'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground',
                  currentWorkspaceId === workspace.id
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground'
                )}
              >
                <Briefcase className="h-4 w-4 shrink-0" />
                <span className="truncate">{workspace.name}</span>
                {currentWorkspaceId === workspace.id && (
                  <div className="ml-auto h-2 w-2 rounded-full bg-primary-foreground" />
                )}
              </button>
            ))
          ) : (
            <div className="flex flex-col items-center justify-center py-8 text-center text-sm text-muted-foreground">
              <Briefcase className="mb-2 h-8 w-8 opacity-50" />
              <p>No workspaces yet</p>
            </div>
          )}
        </nav>

        {/* Footer - Create Workspace Button */}
        <div className="border-t p-3">
          <Button
            variant="outline"
            className="w-full justify-start"
            onClick={handleCreateWorkspace}
          >
            <Plus className="mr-2 h-4 w-4" />
            Create Workspace
          </Button>
        </div>
      </aside>
      <CreateWorkspaceModal open={showCreateModal} onOpenChange={setShowCreateModal} />
    </>
  )
}
