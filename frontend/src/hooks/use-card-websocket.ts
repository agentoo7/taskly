/**
 * WebSocket hook for card real-time updates
 * Simplified version - connects to workspace WebSocket for card events
 */

import { useEffect, useRef } from 'react'

interface CardWebSocketOptions {
  cardId: string
  onCommentCreated?: (comment: any) => void
  onActivityCreated?: (activity: any) => void
}

export function useCardWebSocket({ cardId, onCommentCreated, onActivityCreated }: CardWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Get access token
    const token = localStorage.getItem('access_token')
    if (!token) return

    // Note: In production, this would connect to workspace WebSocket
    // and filter events by card_id. For now, simplified implementation.
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/workspaces/default?token=${token}`

    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected for card:', cardId)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)

          // Filter events for this card
          if (message.event === 'comment_created' && message.data?.card_id === cardId) {
            onCommentCreated?.(message.data)
          } else if (message.event === 'activity_created' && message.data?.card_id === cardId) {
            onActivityCreated?.(message.data)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [cardId, onCommentCreated, onActivityCreated])

  return wsRef
}
