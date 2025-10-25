'use client'

import { useState } from 'react'
import { MoreVertical, Shield, User, Trash2 } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
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
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Input } from '@/components/ui/input'
import { useToast } from '@/hooks/use-toast'

interface Member {
  user_id: string
  username: string
  email: string
  avatar_url: string | null
  role: 'admin' | 'member'
  joined_at: string
}

interface MemberListProps {
  workspaceId: string
  currentUserId: string
  currentUserRole: 'admin' | 'member'
}

export function MemberList({ workspaceId, currentUserId, currentUserRole }: MemberListProps) {
  const [search, setSearch] = useState('')
  const [memberToRemove, setMemberToRemove] = useState<Member | null>(null)
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Fetch members
  const { data: members = [], isLoading } = useQuery<Member[]>({
    queryKey: ['workspace', workspaceId, 'members', search],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (search) params.append('search', search)

      const res = await fetch(`/api/workspaces/${workspaceId}/members?${params}`, {
        credentials: 'include',
      })

      if (!res.ok) {
        throw new Error('Failed to fetch members')
      }

      return res.json()
    },
  })

  // Update role mutation
  const { mutate: updateRole, isPending: isUpdatingRole } = useMutation({
    mutationFn: async ({ userId, newRole }: { userId: string; newRole: 'admin' | 'member' }) => {
      const res = await fetch(`/api/workspaces/${workspaceId}/members/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole }),
        credentials: 'include',
      })

      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Failed to update role')
      }

      return res.json()
    },
    onSuccess: (_, variables) => {
      toast({
        title: 'Role updated',
        description: `Member role changed to ${variables.newRole}`,
      })
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId, 'members'] })
    },
    onError: (error: Error) => {
      toast({
        variant: 'destructive',
        title: 'Failed to update role',
        description: error.message,
      })
    },
  })

  // Remove member mutation
  const { mutate: removeMember, isPending: isRemoving } = useMutation({
    mutationFn: async (userId: string) => {
      const res = await fetch(`/api/workspaces/${workspaceId}/members/${userId}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Failed to remove member')
      }
    },
    onSuccess: () => {
      toast({
        title: 'Member removed',
        description: 'Member has been removed from the workspace',
      })
      setMemberToRemove(null)
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId, 'members'] })
    },
    onError: (error: Error) => {
      toast({
        variant: 'destructive',
        title: 'Failed to remove member',
        description: error.message,
      })
      setMemberToRemove(null)
    },
  })

  const handleRoleToggle = (member: Member) => {
    const newRole = member.role === 'admin' ? 'member' : 'admin'
    updateRole({ userId: member.user_id, newRole })
  }

  const isCurrentUser = (userId: string) => userId === currentUserId
  const isAdmin = currentUserRole === 'admin'

  if (isLoading) {
    return <div className="py-8 text-center text-muted-foreground">Loading members...</div>
  }

  return (
    <>
      <div className="space-y-4">
        {/* Search */}
        <div>
          <Input
            type="search"
            placeholder="Search members by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="max-w-sm"
          />
        </div>

        {/* Members Table */}
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Member</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Joined</TableHead>
                {isAdmin && <TableHead className="text-right">Actions</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {members.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={isAdmin ? 4 : 3}
                    className="py-8 text-center text-muted-foreground"
                  >
                    {search ? 'No members found' : 'No members yet'}
                  </TableCell>
                </TableRow>
              ) : (
                members.map((member) => (
                  <TableRow key={member.user_id}>
                    {/* Member Info */}
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarImage src={member.avatar_url || undefined} alt={member.username} />
                          <AvatarFallback>
                            {member.username.slice(0, 2).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="flex items-center gap-2 font-medium">
                            {member.username}
                            {isCurrentUser(member.user_id) && (
                              <Badge variant="outline" className="text-xs">
                                You
                              </Badge>
                            )}
                          </div>
                          <div className="text-sm text-muted-foreground">{member.email}</div>
                        </div>
                      </div>
                    </TableCell>

                    {/* Role */}
                    <TableCell>
                      <Badge variant={member.role === 'admin' ? 'default' : 'secondary'}>
                        {member.role === 'admin' ? (
                          <Shield className="mr-1 h-3 w-3" />
                        ) : (
                          <User className="mr-1 h-3 w-3" />
                        )}
                        {member.role.charAt(0).toUpperCase() + member.role.slice(1)}
                      </Badge>
                    </TableCell>

                    {/* Joined Date */}
                    <TableCell className="text-muted-foreground">
                      {format(new Date(member.joined_at), 'MMM d, yyyy')}
                    </TableCell>

                    {/* Actions (Admin Only) */}
                    {isAdmin && (
                      <TableCell className="text-right">
                        {!isCurrentUser(member.user_id) && (
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                disabled={isUpdatingRole || isRemoving}
                              >
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onClick={() => handleRoleToggle(member)}>
                                {member.role === 'admin' ? (
                                  <>
                                    <User className="mr-2 h-4 w-4" />
                                    Change to Member
                                  </>
                                ) : (
                                  <>
                                    <Shield className="mr-2 h-4 w-4" />
                                    Promote to Admin
                                  </>
                                )}
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                onClick={() => setMemberToRemove(member)}
                                className="text-destructive focus:text-destructive"
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Remove from workspace
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        )}
                      </TableCell>
                    )}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        <div className="text-sm text-muted-foreground">
          {members.length} member{members.length !== 1 ? 's' : ''} in workspace
        </div>
      </div>

      {/* Remove Confirmation Dialog */}
      <AlertDialog open={!!memberToRemove} onOpenChange={() => setMemberToRemove(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove member?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove <strong>{memberToRemove?.username}</strong> from this
              workspace? They will lose access to all boards and cards.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isRemoving}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => memberToRemove && removeMember(memberToRemove.user_id)}
              disabled={isRemoving}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isRemoving ? 'Removing...' : 'Remove member'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
