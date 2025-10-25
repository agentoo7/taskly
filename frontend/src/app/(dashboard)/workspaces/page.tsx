/**
 * Workspaces landing page for authenticated users.
 */

'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/lib/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Plus, Users, Layout } from 'lucide-react'
import { CreateWorkspaceModal } from '@/components/workspace/create-workspace-modal'
import { api } from '@/lib/api/client'
import Link from 'next/link'

interface Workspace {
  id: string
  name: string
  created_by: string
  created_at: string
  updated_at: string
}

export default function WorkspacesPage() {
  const { user, isLoading: isAuthLoading } = useAuth()
  const [showCreateModal, setShowCreateModal] = useState(false)

  const { data: workspaces, isLoading: isWorkspacesLoading } = useQuery({
    queryKey: ['workspaces'],
    queryFn: () => api.get<Workspace[]>('/api/workspaces'),
    enabled: !!user,
  })

  if (isAuthLoading || isWorkspacesLoading) {
    return <WorkspacesPageSkeleton />
  }

  const hasWorkspaces = workspaces && workspaces.length > 0

  return (
    <div className="container mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Welcome, {user?.username}!</h1>
          <p className="mt-2 text-muted-foreground">
            Manage your workspaces and start collaborating on projects.
          </p>
        </div>
        {hasWorkspaces && (
          <Button onClick={() => setShowCreateModal(true)} size="lg">
            <Plus className="mr-2 h-4 w-4" />
            Create Workspace
          </Button>
        )}
      </div>

      {hasWorkspaces ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {workspaces.map((workspace) => (
            <Link key={workspace.id} href={`/workspaces/${workspace.id}`}>
              <Card className="transition-all hover:shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Layout className="h-5 w-5" />
                    {workspace.name}
                  </CardTitle>
                  <CardDescription>
                    Created {new Date(workspace.created_at).toLocaleDateString()}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Layout className="h-4 w-4" />
                      <span>0 boards</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="h-4 w-4" />
                      <span>0 members</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
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
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold">No workspaces yet</h3>
          <p className="mt-2 max-w-sm text-sm text-muted-foreground">
            Get started by creating your first workspace to organize your boards and collaborate
            with your team.
          </p>
          <Button className="mt-6" size="lg" onClick={() => setShowCreateModal(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Create Workspace
          </Button>
        </Card>
      )}

      <CreateWorkspaceModal open={showCreateModal} onOpenChange={setShowCreateModal} />
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
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-48 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    </div>
  )
}
