/**
 * Card detail modal for viewing and editing card details
 */

'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Trash2, Loader2, Save } from 'lucide-react'
import { Card as CardType, CardUpdate, Priority } from '@/lib/types/card'
import { PrioritySelector } from './priority-selector'
import { DueDatePicker } from './due-date-picker'
import { MarkdownEditor } from './markdown-editor'
import { AssigneeSelector } from './assignee-selector'
import { LabelSelector } from './label-selector'
import { toast } from 'sonner'

interface CardDetailModalProps {
  card: CardType
  open: boolean
  onOpenChange: (open: boolean) => void
  boardId: string
  workspaceId: string
}

// Mock API client - will be replaced with actual implementation
const api = {
  patch: async (url: string, data: any) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${url}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error('Failed to update card')
    return response.json()
  },
  delete: async (url: string) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${url}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    })
    if (!response.ok) throw new Error('Failed to delete card')
  },
}

export function CardDetailModal({ card, open, onOpenChange, boardId, workspaceId }: CardDetailModalProps) {
  const [title, setTitle] = useState(card.title)
  const [description, setDescription] = useState(card.description || '')
  const [priority, setPriority] = useState<Priority>(card.priority)
  const [dueDate, setDueDate] = useState<string | null>(card.due_date)
  const [storyPoints, setStoryPoints] = useState<string>(
    card.story_points !== null && card.story_points !== undefined ? String(card.story_points) : ''
  )
  const [hasChanges, setHasChanges] = useState(false)
  const queryClient = useQueryClient()

  // Reset state when card changes or modal opens
  useEffect(() => {
    if (open) {
      setTitle(card.title)
      setDescription(card.description || '')
      setPriority(card.priority)
      setDueDate(card.due_date)
      setStoryPoints(
        card.story_points !== null && card.story_points !== undefined ? String(card.story_points) : ''
      )
      setHasChanges(false)
    }
  }, [card, open])

  const updateMutation = useMutation({
    mutationFn: (updates: CardUpdate) => api.patch(`/api/cards/${card.id}`, updates),
    onMutate: async (updates: CardUpdate) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['boards', boardId, 'cards'] })

      // Snapshot previous value
      const previousCards = queryClient.getQueryData(['boards', boardId, 'cards'])

      // Optimistically update cards cache
      queryClient.setQueryData(['boards', boardId, 'cards'], (old: CardType[] | undefined) => {
        if (!old) return old
        return old.map((c) => (c.id === card.id ? { ...c, ...updates } : c))
      })

      return { previousCards }
    },
    onSuccess: (data) => {
      // Update the cache with the actual server response
      queryClient.setQueryData(['boards', boardId, 'cards'], (old: CardType[] | undefined) => {
        if (!old) return old
        return old.map((c) => (c.id === card.id ? data : c))
      })

      // Force refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })
      queryClient.invalidateQueries({ queryKey: ['cards', card.id] })

      toast.success('Card updated successfully')
      setHasChanges(false)

      // Close modal after successful save
      onOpenChange(false)
    },
    onError: (error: Error, _variables, context) => {
      // Rollback on error
      if (context?.previousCards) {
        queryClient.setQueryData(['boards', boardId, 'cards'], context.previousCards)
      }
      toast.error(`Failed to update card: ${error.message}`)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => api.delete(`/api/cards/${card.id}`),
    onSuccess: () => {
      toast.success('Card deleted')
      queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })
      onOpenChange(false)
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete card: ${error.message}`)
    },
  })

  const handleSave = () => {
    // Validate title
    if (!title.trim()) {
      toast.error('Card title is required')
      return
    }

    // Validate story points
    const points = storyPoints === '' ? null : parseInt(storyPoints)
    if (points !== null && (isNaN(points) || points < 0 || points > 99)) {
      toast.error('Story points must be between 0 and 99')
      return
    }

    // Build updates object
    const updates: CardUpdate = {}

    if (title.trim() !== card.title) {
      updates.title = title.trim()
    }

    if (description !== (card.description || '')) {
      updates.description = description || null
    }

    if (priority !== card.priority) {
      updates.priority = priority
    }

    if (dueDate !== card.due_date) {
      updates.due_date = dueDate
    }

    if (points !== card.story_points) {
      updates.story_points = points
    }

    // Only save if there are actual changes
    if (Object.keys(updates).length === 0) {
      toast.info('No changes to save')
      onOpenChange(false)
      return
    }

    updateMutation.mutate(updates)
  }

  const handleDelete = () => {
    if (confirm('Delete this card? This action cannot be undone.')) {
      deleteMutation.mutate()
    }
  }

  // Track changes
  useEffect(() => {
    const hasChange =
      title.trim() !== card.title ||
      description !== (card.description || '') ||
      priority !== card.priority ||
      dueDate !== card.due_date ||
      storyPoints !==
        (card.story_points !== null && card.story_points !== undefined ? String(card.story_points) : '')

    setHasChanges(hasChange)
  }, [title, description, priority, dueDate, storyPoints, card])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="sr-only">Card Details</DialogTitle>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="text-2xl font-bold border-none px-0 focus-visible:ring-0 shadow-none"
            placeholder="Card title"
          />
        </DialogHeader>

        <div className="grid gap-6">
          {/* Description with Markdown */}
          <div>
            <Label htmlFor="description" className="mb-2 block">
              Description
            </Label>
            <MarkdownEditor
              value={description}
              onChange={setDescription}
              placeholder="Add a description..."
              autoSaveKey={`card-${card.id}-description`}
            />
          </div>

          {/* Metadata Grid */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label htmlFor="priority" className="mb-2 block">
                Priority
              </Label>
              <PrioritySelector value={priority} onChange={setPriority} />
            </div>

            <div>
              <Label htmlFor="due-date" className="mb-2 block">
                Due Date
              </Label>
              <DueDatePicker value={dueDate} onChange={setDueDate} />
            </div>

            <div>
              <Label htmlFor="story-points" className="mb-2 block">
                Story Points
              </Label>
              <Input
                id="story-points"
                type="number"
                min="0"
                max="99"
                value={storyPoints}
                onChange={(e) => setStoryPoints(e.target.value)}
                placeholder="0-99"
              />
            </div>
          </div>

          {/* Assignees Section */}
          <div>
            <Label className="mb-2 block">Assignees</Label>
            <AssigneeSelector
              cardId={card.id}
              workspaceId={workspaceId}
              assignees={card.assignees || []}
              boardId={boardId}
            />
          </div>

          {/* Labels Section */}
          <div>
            <Label className="mb-2 block">Labels</Label>
            <LabelSelector
              cardId={card.id}
              workspaceId={workspaceId}
              labels={card.labels || []}
              boardId={boardId}
            />
          </div>
        </div>

        <DialogFooter className="flex items-center justify-between sm:justify-between">
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={deleteMutation.isPending || updateMutation.isPending}
          >
            {deleteMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Deleting...
              </>
            ) : (
              <>
                <Trash2 className="mr-2 h-4 w-4" />
                Delete Card
              </>
            )}
          </Button>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={updateMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={!hasChanges || updateMutation.isPending}
            >
              {updateMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save & Close
                </>
              )}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
