/**
 * Board settings page for archiving and other board configuration.
 */

'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { api } from '@/lib/api/client'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { ArrowLeft, Archive, Trash2 } from 'lucide-react'
import Link from 'next/link'

interface Board {
  id: string
  workspace_id: string
  name: string
  columns: Array<{ id: string; name: string; position: number }>
  archived: boolean
  created_at: string
  updated_at: string
}

export default function BoardSettingsPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const boardId = params.boardId as string
  const workspaceId = params.workspaceId as string

  const [boardName, setBoardName] = useState('')
  const [showArchiveDialog, setShowArchiveDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const { data: board, isLoading } = useQuery({
    queryKey: ['boards', boardId],
    queryFn: async () => {
      const data = await api.get<Board>(`/api/boards/${boardId}`)
      setBoardName(data.name)
      return data
    },
  })

  const updateBoardMutation = useMutation({
    mutationFn: (data: Partial<Board>) => api.patch<Board>(`/api/boards/${boardId}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', boardId] })
      queryClient.invalidateQueries({ queryKey: ['workspaces', workspaceId, 'boards'] })
    },
  })

  const archiveBoardMutation = useMutation({
    mutationFn: () => api.patch<Board>(`/api/boards/${boardId}`, { archived: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces', workspaceId, 'boards'] })
      router.push(`/workspaces/${workspaceId}`)
    },
  })

  const deleteBoardMutation = useMutation({
    mutationFn: () => api.delete(`/api/boards/${boardId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces', workspaceId, 'boards'] })
      router.push(`/workspaces/${workspaceId}`)
    },
  })

  const handleUpdateName = async () => {
    if (!boardName.trim() || boardName === board?.name) return
    await updateBoardMutation.mutateAsync({ name: boardName.trim() })
  }

  const handleArchive = async () => {
    await archiveBoardMutation.mutateAsync()
    setShowArchiveDialog(false)
  }

  const handleDelete = async () => {
    await deleteBoardMutation.mutateAsync()
    setShowDeleteDialog(false)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-muted-foreground">Loading settings...</p>
      </div>
    )
  }

  if (!board) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-destructive">Board not found</p>
      </div>
    )
  }

  return (
    <>
      <div className="container mx-auto max-w-3xl px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button variant="ghost" size="sm" asChild className="mb-4">
            <Link href={`/workspaces/${workspaceId}/boards/${boardId}`}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Board
            </Link>
          </Button>
          <h1 className="text-3xl font-bold">Board Settings</h1>
          <p className="mt-2 text-muted-foreground">
            Manage your board configuration and preferences
          </p>
        </div>

        {/* General Settings */}
        <Card className="p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">General</h2>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="board-name">Board Name</Label>
              <div className="flex gap-2">
                <Input
                  id="board-name"
                  value={boardName}
                  onChange={(e) => setBoardName(e.target.value)}
                  placeholder="Enter board name"
                  maxLength={100}
                />
                <Button
                  onClick={handleUpdateName}
                  disabled={!boardName.trim() || boardName === board.name || updateBoardMutation.isPending}
                >
                  {updateBoardMutation.isPending ? 'Saving...' : 'Save'}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">{boardName.length}/100 characters</p>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label>Board Information</Label>
              <div className="space-y-1 text-sm text-muted-foreground">
                <p>Created: {new Date(board.created_at).toLocaleString()}</p>
                <p>Last updated: {new Date(board.updated_at).toLocaleString()}</p>
                <p>Columns: {board.columns.length}</p>
                <p>Status: {board.archived ? 'Archived' : 'Active'}</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Danger Zone */}
        <Card className="p-6 border-destructive/50">
          <h2 className="text-xl font-semibold mb-4 text-destructive">Danger Zone</h2>
          <div className="space-y-4">
            {/* Archive Board */}
            {!board.archived && (
              <div className="flex items-start justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Archive className="h-4 w-4" />
                    <h3 className="font-medium">Archive Board</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Hide this board from the workspace. You can restore it later from archived boards.
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => setShowArchiveDialog(true)}
                  disabled={archiveBoardMutation.isPending}
                >
                  Archive
                </Button>
              </div>
            )}

            {/* Delete Board */}
            <div className="flex items-start justify-between p-4 border border-destructive/50 rounded-lg">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Trash2 className="h-4 w-4 text-destructive" />
                  <h3 className="font-medium text-destructive">Delete Board</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  Permanently delete this board and all its data. This action cannot be undone.
                </p>
              </div>
              <Button
                variant="destructive"
                onClick={() => setShowDeleteDialog(true)}
                disabled={deleteBoardMutation.isPending}
              >
                Delete
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Archive Confirmation Dialog */}
      <AlertDialog open={showArchiveDialog} onOpenChange={setShowArchiveDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Archive Board?</AlertDialogTitle>
            <AlertDialogDescription>
              This will hide &quot;{board.name}&quot; from your workspace. You can restore it later from the
              archived boards section.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleArchive} disabled={archiveBoardMutation.isPending}>
              {archiveBoardMutation.isPending ? 'Archiving...' : 'Archive Board'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Board Permanently?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete &quot;{board.name}&quot; and all its columns and cards. This
              action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleteBoardMutation.isPending}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteBoardMutation.isPending ? 'Deleting...' : 'Delete Permanently'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
