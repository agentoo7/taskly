/**
 * Workspace settings page for editing workspace details and managing members.
 */

'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { api } from '@/lib/api/client'
import { DeleteWorkspaceModal } from '@/components/workspace/delete-workspace-modal'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

interface WorkspaceDetail {
  id: string
  name: string
  created_by: string | null
  created_at: string
  updated_at: string
  boards: unknown[]
  members: unknown[]
}

const schema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
})

type FormData = z.infer<typeof schema>

export default function WorkspaceSettingsPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const workspaceId = params.workspaceId as string
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const { data: workspace, isLoading } = useQuery({
    queryKey: ['workspaces', workspaceId],
    queryFn: () => api.get<WorkspaceDetail>(`/api/workspaces/${workspaceId}`),
  })

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    values: workspace ? { name: workspace.name } : undefined,
  })

  const updateMutation = useMutation<WorkspaceDetail, Error, FormData>({
    mutationFn: (data: FormData) => api.patch<WorkspaceDetail>(`/api/workspaces/${workspaceId}`, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['workspaces', workspaceId] })
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      reset({ name: data.name })
    },
    onError: (error) => {
      console.error('Failed to update workspace:', error)
    },
  })

  const onSubmit = (data: FormData) => {
    updateMutation.mutate(data)
  }

  if (isLoading) {
    return <SettingsPageSkeleton />
  }

  if (!workspace) {
    return (
      <div className="container mx-auto max-w-3xl px-4 py-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold">Workspace not found</h2>
          <Button asChild className="mt-4">
            <Link href="/workspaces">Back to Workspaces</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-3xl px-4 py-8">
      <div className="mb-8">
        <Button variant="ghost" asChild className="mb-4">
          <Link href={`/workspaces/${workspaceId}`}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Workspace
          </Link>
        </Button>
        <h1 className="text-3xl font-bold tracking-tight">Workspace Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Manage workspace details, members, and danger zone actions.
        </p>
      </div>

      <div className="space-y-6">
        {/* Workspace Details */}
        <Card>
          <CardHeader>
            <CardTitle>Workspace Details</CardTitle>
            <CardDescription>Update your workspace name and configuration.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Workspace Name</Label>
                <Input id="name" {...register('name')} />
                {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
              </div>
              <div className="flex gap-2">
                <Button
                  type="submit"
                  disabled={!isDirty || updateMutation.isPending}
                >
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </Button>
                {isDirty && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => reset()}
                    disabled={updateMutation.isPending}
                  >
                    Cancel
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Members - Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle>Members</CardTitle>
            <CardDescription>
              Manage workspace members and their permissions. (Coming in Story 2.2)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Member management will be available soon.</p>
          </CardContent>
        </Card>

        {/* Danger Zone */}
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Danger Zone</CardTitle>
            <CardDescription>
              Irreversible actions that will permanently affect your workspace.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between rounded-lg border border-destructive/50 p-4">
              <div>
                <h4 className="font-semibold">Delete Workspace</h4>
                <p className="text-sm text-muted-foreground">
                  This will delete all boards, cards, and memberships.
                </p>
              </div>
              <Button variant="destructive" onClick={() => setShowDeleteModal(true)}>
                Delete Workspace
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <DeleteWorkspaceModal
        workspace={{ id: workspace.id, name: workspace.name }}
        open={showDeleteModal}
        onOpenChange={setShowDeleteModal}
      />
    </div>
  )
}

function SettingsPageSkeleton() {
  return (
    <div className="container mx-auto max-w-3xl px-4 py-8">
      <div className="mb-8">
        <div className="mb-4 h-10 w-48 animate-pulse rounded bg-muted" />
        <div className="h-10 w-64 animate-pulse rounded bg-muted" />
        <div className="mt-2 h-6 w-96 animate-pulse rounded bg-muted" />
      </div>
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-64 animate-pulse rounded-lg bg-muted" />
        ))}
      </div>
    </div>
  )
}
