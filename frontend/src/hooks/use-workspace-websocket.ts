/**
 * WebSocket hook for real-time workspace updates.
 * Automatically connects/disconnects based on workspace ID.
 */

import { useEffect, useRef, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useToast } from '@/hooks/use-toast'

interface WorkspaceUpdateData {
  workspace_id: string
  name: string
  updated_by: string
}

interface WorkspaceDeletedData {
  workspace_id: string
  deleted_by: string
}

interface MemberJoinedData {
  user_id: string
  username: string
  email: string
  avatar_url: string | null
  role: string
}

interface MemberRoleChangedData {
  user_id: string
  username: string
  old_role: string
  new_role: string
}

interface MemberRemovedData {
  user_id: string
  username: string
  removed_by: string
  removed_by_username: string
}

interface WebSocketMessage {
  type: string
  data: WorkspaceUpdateData | WorkspaceDeletedData | MemberJoinedData | MemberRoleChangedData | MemberRemovedData | Record<string, unknown>
  timestamp?: string
}

export function useWorkspaceWebSocket(workspaceId: string | undefined) {
  const wsRef = useRef<WebSocket | null>(null)
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5

  const handleMessage = useCallback((message: WebSocketMessage) => {
    console.log('WebSocket message received:', message)

    switch (message.type) {
      case 'connected':
        // Welcome message, no action needed
        break

      case 'workspace_updated': {
        const data = message.data as WorkspaceUpdateData
        // Invalidate workspace queries to refetch data
        queryClient.invalidateQueries({ queryKey: ['workspaces', data.workspace_id] })
        queryClient.invalidateQueries({ queryKey: ['workspaces'] })

        // Show toast notification
        toast({
          title: 'Workspace updated',
          description: `Workspace name changed to "${data.name}"`,
        })
        break
      }

      case 'workspace_deleted': {
        const data = message.data as WorkspaceDeletedData
        // Invalidate queries
        queryClient.invalidateQueries({ queryKey: ['workspaces'] })

        // Show toast notification
        toast({
          title: 'Workspace deleted',
          description: 'This workspace has been deleted by an admin.',
          variant: 'destructive',
        })

        // Redirect to workspaces list
        window.location.href = '/workspaces'
        break
      }

      case 'member_joined': {
        const data = message.data as MemberJoinedData
        // Invalidate members query to refetch list
        queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId, 'members'] })

        // Show toast notification (AC 19)
        toast({
          title: 'New member joined',
          description: `${data.username} has joined the workspace`,
        })
        break
      }

      case 'member_role_changed': {
        const data = message.data as MemberRoleChangedData
        // Invalidate members query to refetch list
        queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId, 'members'] })

        // Show toast notification
        toast({
          title: 'Member role updated',
          description: `${data.username}'s role changed from ${data.old_role} to ${data.new_role}`,
        })
        break
      }

      case 'member_removed': {
        const data = message.data as MemberRemovedData
        // Invalidate members query to refetch list
        queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId, 'members'] })

        // Show toast notification
        toast({
          title: 'Member removed',
          description: `${data.username} was removed from the workspace`,
        })
        break
      }

      default:
        console.warn('Unknown WebSocket event:', message.type)
    }
  }, [queryClient, toast, workspaceId])

  const connect = useCallback(() => {
    if (!workspaceId) return

    const accessToken = localStorage.getItem('access_token')
    if (!accessToken) {
      console.warn('No access token available for WebSocket connection')
      return
    }

    // Determine WebSocket URL based on environment
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = process.env.NEXT_PUBLIC_WS_URL || window.location.host.replace(':3000', ':8000')
    const wsUrl = `${wsProtocol}//${wsHost}/ws/workspaces/${workspaceId}?token=${accessToken}`

    try {
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log(`WebSocket connected to workspace: ${workspaceId}`)
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
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log(`WebSocket disconnected from workspace: ${workspaceId}`)

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
  }, [workspaceId, handleMessage])

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
