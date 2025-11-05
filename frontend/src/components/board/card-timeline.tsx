/**
 * Card timeline component showing comments and activities
 */

'use client'

import { useState } from 'react'
import { useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { TimelineComment } from './timeline-comment'
import { TimelineActivity } from './timeline-activity'
import { useCardWebSocket } from '@/hooks/use-card-websocket'
import { MentionInput } from './mention-input'
import { apiClient } from '@/lib/api/client'
import type { TimelineResponse, TimelineComment as TimelineCommentType, CommentCreateRequest } from '@/types/timeline'

interface CardTimelineProps {
  cardId: string
}

export function CardTimeline({ cardId }: CardTimelineProps) {
  const [commentText, setCommentText] = useState('')
  const queryClient = useQueryClient()

  // WebSocket real-time updates
  useCardWebSocket({
    cardId,
    onCommentCreated: (comment) => {
      // Invalidate timeline to fetch new comment
      queryClient.invalidateQueries({ queryKey: ['card-timeline', cardId] })
      toast.info(`${comment.author.username} commented on this card`)
    },
    onActivityCreated: (activity) => {
      // Invalidate timeline to fetch new activity
      queryClient.invalidateQueries({ queryKey: ['card-timeline', cardId] })
    },
  })

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteQuery({
    queryKey: ['card-timeline', cardId],
    queryFn: ({ pageParam = 0 }) =>
      apiClient.get<TimelineResponse>(`/api/cards/${cardId}/timeline?offset=${pageParam}&limit=20`),
    getNextPageParam: (lastPage) => {
      const loaded = lastPage.offset + lastPage.items.length
      return loaded < lastPage.total ? loaded : undefined
    },
    initialPageParam: 0,
  })

  const postCommentMutation = useMutation({
    mutationFn: (text: string) =>
      apiClient.post<TimelineCommentType>(`/api/cards/${cardId}/comments`, { text } as CommentCreateRequest),
    onSuccess: () => {
      toast.success('Comment posted')
      queryClient.invalidateQueries({ queryKey: ['card-timeline', cardId] })
      setCommentText('')
    },
    onError: () => {
      toast.error('Failed to post comment')
    },
  })

  const handlePostComment = () => {
    if (!commentText.trim()) return
    postCommentMutation.mutate(commentText)
  }

  const timelineItems = data?.pages.flatMap((page) => page.items) || []

  return (
    <div className="space-y-4">
      {/* Comment Input with @mention support */}
      <div className="space-y-2">
        <MentionInput
          value={commentText}
          onChange={setCommentText}
          placeholder="Add a comment... (Markdown supported, use @ to mention)"
          rows={3}
        />
        <Button
          onClick={handlePostComment}
          disabled={postCommentMutation.isPending || !commentText.trim()}
          size="sm"
        >
          {postCommentMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Add Comment
        </Button>
      </div>

      {/* Timeline */}
      {isLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      ) : (
        <div className="space-y-4">
          {timelineItems.map((item: any) => {
            if (item.type === 'comment') {
              return <TimelineComment key={item.id} comment={item} cardId={cardId} />
            } else {
              return <TimelineActivity key={item.id} activity={item} />
            }
          })}

          {hasNextPage && (
            <Button
              variant="outline"
              onClick={() => fetchNextPage()}
              disabled={isFetchingNextPage}
              className="w-full"
            >
              {isFetchingNextPage ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Loading...
                </>
              ) : (
                'Load More'
              )}
            </Button>
          )}

          {timelineItems.length === 0 && (
            <p className="text-center text-sm text-muted-foreground py-8">
              No comments or activity yet
            </p>
          )}
        </div>
      )}
    </div>
  )
}
