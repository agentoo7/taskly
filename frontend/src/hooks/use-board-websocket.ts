/**
 * WebSocket hook for real-time board updates (card movements, etc.).
 * Automatically connects/disconnects based on board ID.
 */

import { useEffect, useRef, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

interface CardMovedData {
  event_type: 'card_moved'
  card_id: string
  board_id: string
  old_column_id: string
  new_column_id: string
  old_column_name: string
  new_column_name: string
  old_position: number
  new_position: number
  moved_by: string
  timestamp: string
}

interface CardCreatedData {
  event_type: 'card_created'
  card_id: string
  board_id: string
  column_id: string
  title: string
  position: number
  user_id: string
  timestamp: string
}

interface CardUpdatedData {
  event_type: 'card_updated'
  card_id: string
  board_id: string
  column_id: string
  updates: Record<string, unknown>
  user_id: string
  timestamp: string
}

interface CardDeletedData {
  event_type: 'card_deleted'
  card_id: string
  board_id: string
  column_id: string
  user_id: string
  timestamp: string
}

type WebSocketMessage = CardMovedData | CardCreatedData | CardUpdatedData | CardDeletedData

export function useBoardWebSocket(boardId: string | undefined) {
  const wsRef = useRef<WebSocket | null>(null)
  const queryClient = useQueryClient()
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5
  const currentUserIdRef = useRef<string | null>(null)

  // Get current user ID from localStorage or auth context
  useEffect(() => {
    // This is a simple way to track the current user
    // In a real app, you might get this from an auth context
    const userId = localStorage.getItem('user_id')
    currentUserIdRef.current = userId
  }, [])

  const handleMessage = useCallback(
    (message: WebSocketMessage) => {
      console.log('Board WebSocket message received:', message)

      // Don't show notifications for actions performed by current user
      const isCurrentUser =
        'moved_by' in message
          ? message.moved_by === currentUserIdRef.current
          : 'user_id' in message
            ? message.user_id === currentUserIdRef.current
            : false

      switch (message.event_type) {
        case 'card_moved': {
          // Invalidate board cards query to refetch
          queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })

          // Show toast notification for other users' moves
          if (!isCurrentUser) {
            const sameColumn = message.old_column_id === message.new_column_id
            const description = sameColumn
              ? `Card moved within ${message.new_column_name}`
              : `Card moved from ${message.old_column_name} to ${message.new_column_name}`

            toast.info('Card moved', {
              description,
              duration: 3000,
            })
          }
          break
        }

        case 'card_created': {
          // Invalidate board cards query to refetch
          queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })

          // Show toast notification
          if (!isCurrentUser) {
            toast.success('New card created', {
              description: message.title,
              duration: 3000,
            })
          }
          break
        }

        case 'card_updated': {
          // Invalidate board cards query to refetch
          queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })

          // Show toast notification for significant updates
          if (!isCurrentUser) {
            toast.info('Card updated', {
              duration: 2000,
            })
          }
          break
        }

        case 'card_deleted': {
          // Invalidate board cards query to refetch
          queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })

          // Show toast notification
          if (!isCurrentUser) {
            toast.info('Card deleted', {
              duration: 2000,
            })
          }
          break
        }

        default:
          console.warn('Unknown board WebSocket event:', message)
      }
    },
    [queryClient, boardId]
  )

  const connect = useCallback(() => {
    if (!boardId) return

    const accessToken = localStorage.getItem('access_token')
    if (!accessToken) {
      console.warn('No access token available for WebSocket connection')
      return
    }

    // Determine WebSocket URL based on environment
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost =
      process.env.NEXT_PUBLIC_WS_URL || window.location.host.replace(':3000', ':8000')
    const wsUrl = `${wsProtocol}//${wsHost}/ws/boards/${boardId}?token=${accessToken}`

    try {
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log(`WebSocket connected to board: ${boardId}`)
        reconnectAttemptsRef.current = 0 // Reset reconnect attempts on successful connection
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('Board WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log(`WebSocket disconnected from board: ${boardId}`)

        // Attempt to reconnect with exponential backoff
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
          console.log(`Attempting to reconnect in ${delay}ms...`)

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current += 1
            connect()
          }, delay)
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }, [boardId, handleMessage])

  useEffect(() => {
    connect()

    return () => {
      // Cleanup on unmount
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [connect])

  return {
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
  }
}
