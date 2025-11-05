/**
 * Timeline comment item with edit/delete actions
 */

'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Pencil, Trash2, Loader2 } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import ReactMarkdown from 'react-markdown'
import { toast } from 'sonner'
import type { TimelineComment as TimelineCommentType, CommentUpdateRequest } from '@/types/timeline'
import { apiClient } from '@/lib/api/client'

interface TimelineCommentProps {
  comment: TimelineCommentType
  cardId: string
}

export function TimelineComment({ comment, cardId }: TimelineCommentProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editText, setEditText] = useState(comment.text)
  const queryClient = useQueryClient()

  // Check if current user is author (simplified - would need auth context)
  const currentUserId = localStorage.getItem('user_id')
  const isAuthor = currentUserId === comment.author?.id

  const updateMutation = useMutation({
    mutationFn: (text: string) =>
      apiClient.patch<TimelineCommentType>(`/api/comments/${comment.id}`, { text } as CommentUpdateRequest),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['card-timeline', cardId] })
      setIsEditing(false)
      toast.success('Comment updated')
    },
    onError: () => {
      toast.error('Failed to update comment')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => apiClient.delete(`/api/comments/${comment.id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['card-timeline', cardId] })
      toast.success('Comment deleted')
    },
    onError: () => {
      toast.error('Failed to delete comment')
    },
  })

  const handleDelete = () => {
    if (confirm('Delete this comment?')) {
      deleteMutation.mutate()
    }
  }

  return (
    <div className="flex gap-3">
      <Avatar className="h-8 w-8">
        <AvatarImage src={comment.author?.avatar_url || undefined} />
        <AvatarFallback>{comment.author?.username?.[0]?.toUpperCase() || '?'}</AvatarFallback>
      </Avatar>

      <div className="flex-1 space-y-1">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm">{comment.author?.username || 'Unknown'}</span>
          <span className="text-xs text-muted-foreground">
            {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
          </span>
          {comment.updated_at !== comment.created_at && (
            <span className="text-xs text-muted-foreground">(edited)</span>
          )}
        </div>

        {isEditing ? (
          <div className="space-y-2">
            <Textarea
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              rows={3}
              className="resize-none"
            />
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={() => updateMutation.mutate(editText)}
                disabled={updateMutation.isPending || !editText.trim()}
              >
                {updateMutation.isPending && <Loader2 className="mr-2 h-3 w-3 animate-spin" />}
                Save
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setIsEditing(false)
                  setEditText(comment.text)
                }}
                disabled={updateMutation.isPending}
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <ReactMarkdown>{comment.text}</ReactMarkdown>
            </div>
            {isAuthor && (
              <div className="flex gap-2 pt-1">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() => setIsEditing(true)}
                >
                  <Pencil className="mr-1 h-3 w-3" />
                  Edit
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs text-destructive hover:text-destructive"
                  onClick={handleDelete}
                  disabled={deleteMutation.isPending}
                >
                  {deleteMutation.isPending ? (
                    <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                  ) : (
                    <Trash2 className="mr-1 h-3 w-3" />
                  )}
                  Delete
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
