'use client'

import { useState } from 'react'
import { Mail, MoreVertical, RefreshCw, Trash2, Clock } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { format, formatDistanceToNow } from 'date-fns'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useToast } from '@/hooks/use-toast'

interface Invitation {
  id: string
  email: string
  role: 'admin' | 'member'
  invited_by: string
  created_at: string
  expires_at: string
  delivery_status: 'pending' | 'sent' | 'delivered' | 'failed' | 'bounced'
}

interface PendingInvitationsListProps {
  workspaceId: string
  isAdmin: boolean
}

export function PendingInvitationsList({ workspaceId, isAdmin }: PendingInvitationsListProps) {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Fetch pending invitations
  const { data: invitations = [], isLoading } = useQuery<Invitation[]>({
    queryKey: ['workspace', workspaceId, 'invitations'],
    queryFn: async () => {
      const res = await fetch(`/api/workspaces/${workspaceId}/invitations`, {
        credentials: 'include',
      })

      if (!res.ok) {
        throw new Error('Failed to fetch invitations')
      }

      return res.json()
    },
  })

  // Resend invitation mutation
  const { mutate: resendInvitation, isPending: isResending } = useMutation({
    mutationFn: async (invitationId: string) => {
      const res = await fetch(`/api/workspaces/${workspaceId}/invitations/${invitationId}/resend`, {
        method: 'POST',
        credentials: 'include',
      })

      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Failed to resend invitation')
      }

      return res.json()
    },
    onSuccess: () => {
      toast({
        title: 'Invitation resent',
        description: 'A new invitation email has been sent',
      })
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId, 'invitations'] })
    },
    onError: (error: Error) => {
      toast({
        variant: 'destructive',
        title: 'Failed to resend invitation',
        description: error.message,
      })
    },
  })

  // Revoke invitation mutation
  const { mutate: revokeInvitation, isPending: isRevoking } = useMutation({
    mutationFn: async (invitationId: string) => {
      const res = await fetch(`/api/workspaces/${workspaceId}/invitations/${invitationId}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Failed to revoke invitation')
      }
    },
    onSuccess: () => {
      toast({
        title: 'Invitation revoked',
        description: 'The invitation has been cancelled',
      })
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId, 'invitations'] })
    },
    onError: (error: Error) => {
      toast({
        variant: 'destructive',
        title: 'Failed to revoke invitation',
        description: error.message,
      })
    },
  })

  const getExpirationInfo = (expiresAt: string) => {
    const now = new Date()
    const expiration = new Date(expiresAt)
    const isExpired = expiration < now

    if (isExpired) {
      return {
        text: 'Expired',
        variant: 'destructive' as const,
      }
    }

    const distance = formatDistanceToNow(expiration, { addSuffix: true })
    const daysRemaining = Math.ceil((expiration.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

    return {
      text: `Expires ${distance}`,
      variant: daysRemaining <= 2 ? ('secondary' as const) : ('outline' as const),
    }
  }

  const getDeliveryStatusBadge = (status: Invitation['delivery_status']) => {
    const config = {
      pending: { label: 'Pending', variant: 'secondary' as const },
      sent: { label: 'Sent', variant: 'default' as const },
      delivered: { label: 'Delivered', variant: 'default' as const },
      failed: { label: 'Failed', variant: 'destructive' as const },
      bounced: { label: 'Bounced', variant: 'destructive' as const },
    }

    return config[status]
  }

  if (!isAdmin) {
    return null
  }

  if (isLoading) {
    return <div className="py-8 text-center text-muted-foreground">Loading invitations...</div>
  }

  if (invitations.length === 0) {
    return (
      <div className="rounded-lg border py-12 text-center">
        <Mail className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
        <h3 className="mb-2 text-lg font-medium">No pending invitations</h3>
        <p className="text-sm text-muted-foreground">
          Invite members to collaborate on this workspace
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Email</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Invited</TableHead>
              <TableHead>Expiration</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {invitations.map((invitation) => {
              const expiration = getExpirationInfo(invitation.expires_at)
              const deliveryStatus = getDeliveryStatusBadge(invitation.delivery_status)

              return (
                <TableRow key={invitation.id}>
                  {/* Email */}
                  <TableCell className="font-medium">{invitation.email}</TableCell>

                  {/* Role */}
                  <TableCell>
                    <Badge variant={invitation.role === 'admin' ? 'default' : 'secondary'}>
                      {invitation.role.charAt(0).toUpperCase() + invitation.role.slice(1)}
                    </Badge>
                  </TableCell>

                  {/* Delivery Status */}
                  <TableCell>
                    <Badge variant={deliveryStatus.variant}>{deliveryStatus.label}</Badge>
                  </TableCell>

                  {/* Invited At */}
                  <TableCell className="text-muted-foreground">
                    {format(new Date(invitation.created_at), 'MMM d, yyyy')}
                  </TableCell>

                  {/* Expiration */}
                  <TableCell>
                    <Badge variant={expiration.variant} className="font-normal">
                      <Clock className="mr-1 h-3 w-3" />
                      {expiration.text}
                    </Badge>
                  </TableCell>

                  {/* Actions */}
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" disabled={isResending || isRevoking}>
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => resendInvitation(invitation.id)}>
                          <RefreshCw className="mr-2 h-4 w-4" />
                          Resend invitation
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          onClick={() => revokeInvitation(invitation.id)}
                          className="text-destructive focus:text-destructive"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Revoke invitation
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </div>

      <div className="text-sm text-muted-foreground">
        {invitations.length} pending invitation{invitations.length !== 1 ? 's' : ''}
      </div>
    </div>
  )
}
