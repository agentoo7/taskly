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
import { Trash2, Loader2 } from 'lucide-react'
import { Card as CardType, CardUpdate } from '@/lib/types/card'
import { PrioritySelector } from './priority-selector'
import { DueDatePicker } from './due-date-picker'
import { MarkdownEditor } from './markdown-editor'
import { toast } from 'sonner'

interface CardDetailModalProps {
  card: CardType
  open: boolean
  onOpenChange: (open: boolean) => void
  boardId: string
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

export function CardDetailModal({ card, open, onOpenChange, boardId }: CardDetailModalProps) {
  const [title, setTitle] = useState(card.title)
  const [description, setDescription] = useState(card.description || '')
  const [storyPoints, setStoryPoints] = useState<string>(
    card.story_points !== null && card.story_points !== undefined ? String(card.story_points) : ''
  )
  const queryClient = useQueryClient()

  // Reset state when card changes
  useEffect(() => {
    setTitle(card.title)
    setDescription(card.description || '')
    setStoryPoints(
      card.story_points !== null && card.story_points !== undefined ? String(card.story_points) : ''
    )
  }, [card])

  const updateMutation = useMutation({
    mutationFn: (updates: CardUpdate) => api.patch(`/api/cards/${card.id}`, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', boardId] })
      queryClient.invalidateQueries({ queryKey: ['cards', card.id] })
    },
    onError: (error: Error) => {
      toast.error(`Failed to update card: ${error.message}`)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => api.delete(`/api/cards/${card.id}`),
    onSuccess: () => {
      toast.success('Card deleted')
      queryClient.invalidateQueries({ queryKey: ['boards', boardId] })
      onOpenChange(false)
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete card: ${error.message}`)
    },
  })

  const handleFieldUpdate = (field: keyof CardUpdate, value: any) => {
    updateMutation.mutate({ [field]: value })
  }

  const handleTitleBlur = () => {
    if (title.trim() && title !== card.title) {
      handleFieldUpdate('title', title.trim())
    } else {
      setTitle(card.title)
    }
  }

  const handleDescriptionBlur = () => {
    if (description !== card.description) {
      handleFieldUpdate('description', description || null)
    }
  }

  const handleStoryPointsBlur = () => {
    const points = parseInt(storyPoints)
    if (!isNaN(points) && points >= 0 && points <= 99) {
      if (points !== card.story_points) {
        handleFieldUpdate('story_points', points)
      }
    } else if (storyPoints === '') {
      if (card.story_points !== null) {
        handleFieldUpdate('story_points', null)
      }
    } else {
      // Invalid input, reset
      setStoryPoints(
        card.story_points !== null && card.story_points !== undefined ? String(card.story_points) : ''
      )
      toast.error('Story points must be between 0 and 99')
    }
  }

  const handleDelete = () => {
    if (confirm('Delete this card? This action cannot be undone.')) {
      deleteMutation.mutate()
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="sr-only">Card Details</DialogTitle>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={handleTitleBlur}
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
              onBlur={handleDescriptionBlur}
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
              <PrioritySelector
                value={card.priority}
                onChange={(priority) => handleFieldUpdate('priority', priority)}
              />
            </div>

            <div>
              <Label htmlFor="due-date" className="mb-2 block">
                Due Date
              </Label>
              <DueDatePicker
                value={card.due_date}
                onChange={(date) => handleFieldUpdate('due_date', date)}
              />
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
                onBlur={handleStoryPointsBlur}
                placeholder="0-99"
              />
            </div>
          </div>
        </div>

        <DialogFooter className="flex items-center justify-between">
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
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

          <div className="text-xs text-muted-foreground">
            {updateMutation.isPending && 'Saving...'}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
