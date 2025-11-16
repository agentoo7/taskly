/**
 * Notification bell icon with unread count badge
 */

'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bell } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { formatDistanceToNow } from 'date-fns'
import { toast } from 'sonner'

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
  patch: async (url: string) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${url}`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    })
    if (!response.ok) throw new Error('Failed to update')
  },
}

export function NotificationBell() {
  const [open, setOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => api.get('/api/notifications'),
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  const markAllReadMutation = useMutation({
    mutationFn: () => api.patch('/api/notifications/read-all'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      toast.success('All notifications marked as read')
    },
  })

  const markReadMutation = useMutation({
    mutationFn: (notificationId: string) => api.patch(`/api/notifications/${notificationId}/read`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })

  const unreadCount = notifications?.unread_count || 0
  const items = notifications?.items || []

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel className="flex items-center justify-between">
          <span>Notifications</span>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 text-xs"
              onClick={() => markAllReadMutation.mutate()}
            >
              Mark all read
            </Button>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <div className="max-h-96 overflow-y-auto">
          {items.length === 0 ? (
            <div className="py-6 text-center text-sm text-muted-foreground">
              No notifications
            </div>
          ) : (
            items.map((notification: any) => (
              <DropdownMenuItem
                key={notification.id}
                className="flex flex-col items-start gap-1 p-3 cursor-pointer"
                onClick={() => {
                  if (!notification.read_at) {
                    markReadMutation.mutate(notification.id)
                  }
                  setOpen(false)
                  // Navigate to card would go here
                }}
              >
                <div className="flex w-full items-start justify-between gap-2">
                  <div className="font-medium text-sm">{notification.title}</div>
                  {!notification.read_at && (
                    <div className="h-2 w-2 rounded-full bg-blue-500 flex-shrink-0 mt-1" />
                  )}
                </div>
                <div className="text-xs text-muted-foreground line-clamp-2">
                  {notification.message}
                </div>
                <div className="text-xs text-muted-foreground">
                  {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                </div>
              </DropdownMenuItem>
            ))
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
