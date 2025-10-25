/**
 * Modal for deleting a workspace with confirmation.
 */

'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { api } from '@/lib/api/client'

interface DeleteWorkspaceModalProps {
  workspace: { id: string; name: string }
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function DeleteWorkspaceModal({
  workspace,
  open,
  onOpenChange,
}: DeleteWorkspaceModalProps) {
  const [confirmName, setConfirmName] = useState('')
  const router = useRouter()
  const queryClient = useQueryClient()

  const deleteMutation = useMutation({
    mutationFn: () => api.delete(`/api/workspaces/${workspace.id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      onOpenChange(false)
      router.push('/workspaces')
    },
    onError: (error) => {
      console.error('Failed to delete workspace:', error)
    },
  })

  const handleDelete = () => {
    if (confirmName === workspace.name) {
      deleteMutation.mutate()
    }
  }

  const handleOpenChange = (newOpen: boolean) => {
    // Reset confirmation name when closing
    if (!newOpen) {
      setConfirmName('')
    }
    onOpenChange(newOpen)
  }

  return (
    <AlertDialog open={open} onOpenChange={handleOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete Workspace?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone. This will permanently delete the workspace and all
            boards, cards, and data within it.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="confirm-name">
              Type <span className="font-bold">{workspace.name}</span> to confirm
            </Label>
            <Input
              id="confirm-name"
              value={confirmName}
              onChange={(e) => setConfirmName(e.target.value)}
              placeholder={workspace.name}
            />
          </div>
        </div>
        <AlertDialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={confirmName !== workspace.name || deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete Workspace'}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
