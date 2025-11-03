/**
 * Assignee selector component for assigning users to cards
 */

'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { User } from '@/lib/types/user'
import { Button } from '@/components/ui/button'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { UserPlus, X, Loader2 } from 'lucide-react'
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
  post: async (url: string, data?: any) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: data ? JSON.stringify(data) : undefined,
    })
    if (!response.ok) throw new Error('Failed to assign user')
    return response.json()
  },
  delete: async (url: string) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${url}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    })
    if (!response.ok) throw new Error('Failed to unassign user')
  },
}

interface AssigneeSelectorProps {
  cardId: string
  workspaceId: string
  assignees: User[]
  boardId: string
}

export function AssigneeSelector({ cardId, workspaceId, assignees, boardId }: AssigneeSelectorProps) {
  const [open, setOpen] = useState(false)
  const queryClient = useQueryClient()

  // Fetch workspace members
  const { data: members, isLoading } = useQuery<User[]>({
    queryKey: ['workspace-members', workspaceId],
    queryFn: () => api.get(`/api/workspaces/${workspaceId}/members`),
    enabled: open,
  })

  // Assign user mutation
  const assignMutation = useMutation({
    mutationFn: (userId: string) => api.post(`/api/cards/${cardId}/assignees`, { user_id: userId }),
    onMutate: async (userId: string) => {
      await queryClient.cancelQueries({ queryKey: ['boards', boardId, 'cards'] })
      const previousCards = queryClient.getQueryData(['boards', boardId, 'cards'])

      // Find user from members list
      const userToAdd = members?.find((m) => m.id === userId)

      // Optimistically add assignee
      queryClient.setQueryData(['boards', boardId, 'cards'], (old: any[]) => {
        if (!old || !userToAdd) return old
        return old.map((c) =>
          c.id === cardId ? { ...c, assignees: [...(c.assignees || []), userToAdd] } : c
        )
      })

      return { previousCards }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })
      queryClient.invalidateQueries({ queryKey: ['cards', cardId] })
      toast.success('User assigned')
    },
    onError: (error: Error, _variables, context) => {
      if (context?.previousCards) {
        queryClient.setQueryData(['boards', boardId, 'cards'], context.previousCards)
      }
      toast.error(`Failed to assign: ${error.message}`)
    },
  })

  // Unassign user mutation
  const unassignMutation = useMutation({
    mutationFn: (userId: string) => api.delete(`/api/cards/${cardId}/assignees/${userId}`),
    onMutate: async (userId: string) => {
      await queryClient.cancelQueries({ queryKey: ['boards', boardId, 'cards'] })
      const previousCards = queryClient.getQueryData(['boards', boardId, 'cards'])

      // Optimistically remove assignee
      queryClient.setQueryData(['boards', boardId, 'cards'], (old: any[]) => {
        if (!old) return old
        return old.map((c) =>
          c.id === cardId
            ? { ...c, assignees: c.assignees?.filter((a: User) => a.id !== userId) || [] }
            : c
        )
      })

      return { previousCards }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })
      queryClient.invalidateQueries({ queryKey: ['cards', cardId] })
      toast.success('User unassigned')
    },
    onError: (error: Error, _variables, context) => {
      if (context?.previousCards) {
        queryClient.setQueryData(['boards', boardId, 'cards'], context.previousCards)
      }
      toast.error(`Failed to unassign: ${error.message}`)
    },
  })

  const handleAssign = (userId: string) => {
    assignMutation.mutate(userId)
  }

  const handleUnassign = (userId: string) => {
    unassignMutation.mutate(userId)
  }

  const isAssigned = (userId: string) => {
    return assignees.some((a) => a.id === userId)
  }

  // Get available members (not already assigned)
  const availableMembers = members?.filter((m) => !isAssigned(m.id)) || []

  return (
    <div className="space-y-2">
      {/* Current assignees */}
      {assignees.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {assignees.map((user) => (
            <div
              key={user.id}
              className="flex items-center gap-2 rounded-md border px-2 py-1 text-sm"
            >
              <Avatar className="h-6 w-6">
                <AvatarImage src={user.avatar_url || undefined} alt={user.username} />
                <AvatarFallback>{user.username.slice(0, 2).toUpperCase()}</AvatarFallback>
              </Avatar>
              <span>{user.username}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-5 w-5 p-0"
                onClick={() => handleUnassign(user.id)}
                disabled={unassignMutation.isPending}
              >
                {unassignMutation.isPending ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <X className="h-3 w-3" />
                )}
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Assign button */}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" size="sm" className="w-full">
            <UserPlus className="mr-2 h-4 w-4" />
            Assign
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-80 p-0" align="start">
          <div className="border-b p-3">
            <p className="text-sm font-medium">Assign to</p>
          </div>
          <div className="max-h-64 overflow-y-auto p-2">
            {isLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-5 w-5 animate-spin" />
              </div>
            ) : availableMembers.length === 0 ? (
              <div className="py-4 text-center text-sm text-muted-foreground">
                All members are already assigned
              </div>
            ) : (
              <div className="space-y-1">
                {availableMembers.map((member) => (
                  <button
                    key={member.id}
                    className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-accent"
                    onClick={() => {
                      handleAssign(member.id)
                      setOpen(false)
                    }}
                    disabled={assignMutation.isPending}
                  >
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={member.avatar_url || undefined} alt={member.username} />
                      <AvatarFallback>{member.username.slice(0, 2).toUpperCase()}</AvatarFallback>
                    </Avatar>
                    <div className="flex flex-col items-start">
                      <span className="font-medium">{member.username}</span>
                      <span className="text-xs text-muted-foreground">{member.email}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </PopoverContent>
      </Popover>
    </div>
  )
}
