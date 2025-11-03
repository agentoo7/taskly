/**
 * Label selector component for adding/removing labels to/from cards
 */

'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Label } from '@/lib/types/label'
import { Button } from '@/components/ui/button'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Tag, X, Loader2, Settings } from 'lucide-react'
import { toast } from 'sonner'
import { LabelManager } from './label-manager'

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
    if (!response.ok) throw new Error('Failed to add label')
    return response.json()
  },
  delete: async (url: string) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${url}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    })
    if (!response.ok) throw new Error('Failed to remove label')
  },
}

interface LabelSelectorProps {
  cardId: string
  workspaceId: string
  labels: Label[]
  boardId: string
}

// Helper to determine if text should be light or dark based on background color
function getContrastColor(hexColor: string): string {
  const r = parseInt(hexColor.slice(1, 3), 16)
  const g = parseInt(hexColor.slice(3, 5), 16)
  const b = parseInt(hexColor.slice(5, 7), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? '#000000' : '#FFFFFF'
}

export function LabelSelector({ cardId, workspaceId, labels, boardId }: LabelSelectorProps) {
  const [open, setOpen] = useState(false)
  const [managerOpen, setManagerOpen] = useState(false)
  const queryClient = useQueryClient()

  // Fetch workspace labels
  const { data: workspaceLabels, isLoading } = useQuery<Label[]>({
    queryKey: ['workspace-labels', workspaceId],
    queryFn: () => api.get(`/api/workspaces/${workspaceId}/labels`),
    enabled: open,
  })

  // Add label mutation
  const addMutation = useMutation({
    mutationFn: (labelId: string) => api.post(`/api/cards/${cardId}/labels`, { label_id: labelId }),
    onMutate: async (labelId: string) => {
      await queryClient.cancelQueries({ queryKey: ['boards', boardId, 'cards'] })
      const previousCards = queryClient.getQueryData(['boards', boardId, 'cards'])

      // Find label from workspace labels
      const labelToAdd = workspaceLabels?.find((l) => l.id === labelId)

      // Optimistically add label
      queryClient.setQueryData(['boards', boardId, 'cards'], (old: any[]) => {
        if (!old || !labelToAdd) return old
        return old.map((c) =>
          c.id === cardId ? { ...c, labels: [...(c.labels || []), labelToAdd] } : c
        )
      })

      return { previousCards }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })
      queryClient.invalidateQueries({ queryKey: ['cards', cardId] })
      toast.success('Label added')
    },
    onError: (error: Error, _variables, context) => {
      if (context?.previousCards) {
        queryClient.setQueryData(['boards', boardId, 'cards'], context.previousCards)
      }
      toast.error(`Failed to add label: ${error.message}`)
    },
  })

  // Remove label mutation
  const removeMutation = useMutation({
    mutationFn: (labelId: string) => api.delete(`/api/cards/${cardId}/labels/${labelId}`),
    onMutate: async (labelId: string) => {
      await queryClient.cancelQueries({ queryKey: ['boards', boardId, 'cards'] })
      const previousCards = queryClient.getQueryData(['boards', boardId, 'cards'])

      // Optimistically remove label
      queryClient.setQueryData(['boards', boardId, 'cards'], (old: any[]) => {
        if (!old) return old
        return old.map((c) =>
          c.id === cardId
            ? { ...c, labels: c.labels?.filter((l: Label) => l.id !== labelId) || [] }
            : c
        )
      })

      return { previousCards }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })
      queryClient.invalidateQueries({ queryKey: ['cards', cardId] })
      toast.success('Label removed')
    },
    onError: (error: Error, _variables, context) => {
      if (context?.previousCards) {
        queryClient.setQueryData(['boards', boardId, 'cards'], context.previousCards)
      }
      toast.error(`Failed to remove label: ${error.message}`)
    },
  })

  const handleAdd = (labelId: string) => {
    addMutation.mutate(labelId)
  }

  const handleRemove = (labelId: string) => {
    removeMutation.mutate(labelId)
  }

  const isApplied = (labelId: string) => {
    return labels.some((l) => l.id === labelId)
  }

  // Get available labels (not already applied)
  const availableLabels = workspaceLabels?.filter((l) => !isApplied(l.id)) || []

  return (
    <div className="space-y-2">
      {/* Current labels */}
      {labels.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {labels.map((label) => (
            <div
              key={label.id}
              className="flex items-center gap-2 rounded-md px-3 py-1 text-sm font-medium"
              style={{
                backgroundColor: label.color,
                color: getContrastColor(label.color),
              }}
            >
              <span>{label.name}</span>
              <button
                className="hover:opacity-80"
                onClick={() => handleRemove(label.id)}
                disabled={removeMutation.isPending}
              >
                {removeMutation.isPending ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <X className="h-3 w-3" />
                )}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Add label button */}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" size="sm" className="w-full">
            <Tag className="mr-2 h-4 w-4" />
            Add Label
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-80 p-0" align="start">
          <div className="border-b p-3 flex items-center justify-between">
            <p className="text-sm font-medium">Labels</p>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setOpen(false)
                setManagerOpen(true)
              }}
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>
          <div className="max-h-64 overflow-y-auto p-2">
            {isLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-5 w-5 animate-spin" />
              </div>
            ) : availableLabels.length === 0 ? (
              <div className="py-4 text-center text-sm text-muted-foreground">
                {workspaceLabels && workspaceLabels.length > 0
                  ? 'All labels are already applied'
                  : 'No labels yet. Create labels in settings.'}
              </div>
            ) : (
              <div className="space-y-1">
                {availableLabels.map((label) => (
                  <button
                    key={label.id}
                    className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-accent"
                    onClick={() => {
                      handleAdd(label.id)
                      setOpen(false)
                    }}
                    disabled={addMutation.isPending}
                  >
                    <div
                      className="h-6 w-6 rounded-md"
                      style={{ backgroundColor: label.color }}
                    />
                    <span className="font-medium">{label.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </PopoverContent>
      </Popover>

      {/* Label Manager Dialog */}
      <LabelManager
        workspaceId={workspaceId}
        open={managerOpen}
        onOpenChange={setManagerOpen}
      />
    </div>
  )
}
