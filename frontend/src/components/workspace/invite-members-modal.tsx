'use client'

import { useState } from 'react'
import { X } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { api } from '@/lib/api/client'

const inviteSchema = z.object({
  emails: z
    .array(z.string().email())
    .min(1, 'At least one email required')
    .max(10, 'Maximum 10 emails allowed'),
  role: z.enum(['member', 'admin']),
})

type InviteFormData = z.infer<typeof inviteSchema>

interface InviteMembersModalProps {
  workspaceId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function InviteMembersModal({ workspaceId, open, onOpenChange }: InviteMembersModalProps) {
  const [emailInput, setEmailInput] = useState('')
  const [emails, setEmails] = useState<string[]>([])
  const [role, setRole] = useState<'member' | 'admin'>('member')
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { mutate: inviteMembers, isPending } = useMutation({
    mutationFn: async (data: InviteFormData) => {
      return api.post(`/api/workspaces/${workspaceId}/invitations`, {
        emails: data.emails,
        role: data.role,
      })
    },
    onSuccess: (data) => {
      toast({
        title: 'Invitations sent',
        description: `Successfully sent invitations to ${emails.length} member${emails.length > 1 ? 's' : ''}`,
      })

      // Reset form
      setEmails([])
      setEmailInput('')
      setRole('member')
      onOpenChange(false)

      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: ['workspace', workspaceId, 'invitations'] })
    },
    onError: (error: Error) => {
      toast({
        variant: 'destructive',
        title: 'Failed to send invitations',
        description: error.message,
      })
    },
  })

  const handleAddEmail = () => {
    const trimmed = emailInput.trim()
    if (!trimmed) return

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(trimmed)) {
      toast({
        variant: 'destructive',
        title: 'Invalid email',
        description: 'Please enter a valid email address',
      })
      return
    }

    // Check for duplicates
    if (emails.includes(trimmed)) {
      toast({
        variant: 'destructive',
        title: 'Duplicate email',
        description: 'This email has already been added',
      })
      return
    }

    // Check max limit
    if (emails.length >= 10) {
      toast({
        variant: 'destructive',
        title: 'Maximum limit reached',
        description: 'You can only invite up to 10 members at once',
      })
      return
    }

    setEmails([...emails, trimmed])
    setEmailInput('')
  }

  const handleRemoveEmail = (email: string) => {
    setEmails(emails.filter((e) => e !== email))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddEmail()
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (emails.length === 0) {
      toast({
        variant: 'destructive',
        title: 'No emails added',
        description: 'Please add at least one email address',
      })
      return
    }

    inviteMembers({ emails, role })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Invite members to workspace</DialogTitle>
          <DialogDescription>
            Invite team members by email. They&apos;ll receive an invitation link.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email Input */}
          <div className="space-y-2">
            <Label htmlFor="email">Email addresses</Label>
            <div className="flex gap-2">
              <Input
                id="email"
                type="email"
                placeholder="colleague@example.com"
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isPending || emails.length >= 10}
              />
              <Button
                type="button"
                onClick={handleAddEmail}
                disabled={!emailInput.trim() || isPending || emails.length >= 10}
              >
                Add
              </Button>
            </div>
            <p className="text-sm text-muted-foreground">
              Press Enter or click Add to include email. Max 10 emails.
            </p>
          </div>

          {/* Email Tags */}
          {emails.length > 0 && (
            <div className="flex min-h-[60px] flex-wrap gap-2 rounded-md border p-3">
              {emails.map((email) => (
                <Badge
                  key={email}
                  variant="secondary"
                  className="flex items-center gap-1 px-2 py-1"
                >
                  <span>{email}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveEmail(email)}
                    className="ml-1 hover:text-destructive"
                    disabled={isPending}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          )}

          {/* Role Selector */}
          <div className="space-y-2">
            <Label htmlFor="role">Role</Label>
            <Select value={role} onValueChange={(value: 'member' | 'admin') => setRole(value)}>
              <SelectTrigger id="role">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="member">Member - Can view and edit</SelectItem>
                <SelectItem value="admin">Admin - Full access including settings</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isPending || emails.length === 0}>
              {isPending
                ? 'Sending...'
                : `Send ${emails.length} invitation${emails.length !== 1 ? 's' : ''}`}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
