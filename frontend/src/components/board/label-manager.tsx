/**
 * Label manager component for managing workspace labels
 */

'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label as UILabel } from '@/components/ui/label'
import { ColorPicker } from './color-picker'
import { Pencil, Trash2, Plus, Loader2 } from 'lucide-react'
import { Label } from '@/lib/types/label'
import { toast } from 'sonner'

// API helper
const api = {
  get: async (url: string) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${url}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    })
    if (!response.ok) throw new Error('Failed to fetch')
    return response.json()
  },
  post: async (url: string, data: any) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error('Failed to create label')
    return response.json()
  },
  patch: async (url: string, data: any) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${url}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error('Failed to update label')
    return response.json()
  },
  delete: async (url: string) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${url}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    })
    if (!response.ok) throw new Error('Failed to delete label')
    return response.json()
  },
}

interface LabelManagerProps {
  workspaceId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function LabelManager({ workspaceId, open, onOpenChange }: LabelManagerProps) {
  const [isCreating, setIsCreating] = useState(false)
  const [editingLabel, setEditingLabel] = useState<Label | null>(null)
  const [name, setName] = useState('')
  const [color, setColor] = useState('#3B82F6')
  const queryClient = useQueryClient()

  const { data: labels, isLoading } = useQuery<Label[]>({
    queryKey: ['workspace-labels', workspaceId],
    queryFn: () => api.get(`/api/workspaces/${workspaceId}/labels`),
    enabled: open,
  })

  const createMutation = useMutation({
    mutationFn: (data: { name: string; color: string }) =>
      api.post(`/api/workspaces/${workspaceId}/labels`, data),
    onSuccess: () => {
      toast.success('Label created')
      queryClient.invalidateQueries({ queryKey: ['workspace-labels', workspaceId] })
      queryClient.invalidateQueries({ queryKey: ['boards'] })
      setIsCreating(false)
      setName('')
      setColor('#3B82F6')
    },
    onError: (error: Error) => {
      toast.error(`Failed to create label: ${error.message}`)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => api.patch(`/api/labels/${id}`, data),
    onSuccess: () => {
      toast.success('Label updated')
      queryClient.invalidateQueries({ queryKey: ['workspace-labels', workspaceId] })
      queryClient.invalidateQueries({ queryKey: ['boards'] })
      setEditingLabel(null)
      setName('')
      setColor('#3B82F6')
    },
    onError: (error: Error) => {
      toast.error(`Failed to update label: ${error.message}`)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/labels/${id}`),
    onSuccess: () => {
      toast.success('Label deleted')
      queryClient.invalidateQueries({ queryKey: ['workspace-labels', workspaceId] })
      queryClient.invalidateQueries({ queryKey: ['boards'] })
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete label: ${error.message}`)
    },
  })

  const handleCreate = () => {
    if (!name.trim()) {
      toast.error('Label name is required')
      return
    }
    createMutation.mutate({ name: name.trim(), color })
  }

  const handleUpdate = () => {
    if (!editingLabel) return
    if (!name.trim()) {
      toast.error('Label name is required')
      return
    }
    updateMutation.mutate({ id: editingLabel.id, data: { name: name.trim(), color } })
  }

  const handleDelete = (label: Label) => {
    if (confirm(`Delete "${label.name}"? This will remove it from all cards.`)) {
      deleteMutation.mutate(label.id)
    }
  }

  const openCreateDialog = () => {
    setName('')
    setColor('#3B82F6')
    setIsCreating(true)
  }

  const openEditDialog = (label: Label) => {
    setName(label.name)
    setColor(label.color)
    setEditingLabel(label)
  }

  const closeDialog = () => {
    setIsCreating(false)
    setEditingLabel(null)
    setName('')
    setColor('#3B82F6')
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Manage Labels</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Create and manage labels for your workspace
              </p>
              <Button size="sm" onClick={openCreateDialog}>
                <Plus className="mr-2 h-4 w-4" />
                Create Label
              </Button>
            </div>

            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : labels && labels.length > 0 ? (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {labels.map((label) => (
                  <div
                    key={label.id}
                    className="flex items-center justify-between p-3 rounded-md border"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className="w-8 h-8 rounded-md"
                        style={{ backgroundColor: label.color }}
                      />
                      <span className="font-medium">{label.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEditDialog(label)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(label)}
                        disabled={deleteMutation.isPending}
                      >
                        {deleteMutation.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-sm text-muted-foreground">
                No labels yet. Create your first label to get started.
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Create/Edit Label Dialog */}
      <Dialog open={isCreating || editingLabel !== null} onOpenChange={closeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingLabel ? 'Edit Label' : 'Create Label'}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4">
            <div>
              <UILabel>Name</UILabel>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Label name"
                maxLength={50}
                className="mt-2"
              />
            </div>
            <div>
              <UILabel>Color</UILabel>
              <div className="mt-2">
                <ColorPicker value={color} onChange={setColor} />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog}>
              Cancel
            </Button>
            <Button
              onClick={editingLabel ? handleUpdate : handleCreate}
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {(createMutation.isPending || updateMutation.isPending) && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              {editingLabel ? 'Update' : 'Create'} Label
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
