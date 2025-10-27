'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Mail, Shield, User, Clock, AlertCircle, CheckCircle2 } from 'lucide-react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { api } from '@/lib/api/client'
import { useToast } from '@/hooks/use-toast'
import { format } from 'date-fns'

interface InvitationDetails {
  id: string
  workspace_id: string
  workspace_name: string | null
  email: string
  role: 'admin' | 'member'
  inviter_name: string | null
  inviter_avatar: string | null
  created_at: string
  expires_at: string
  is_expired: boolean
  is_accepted: boolean
}

interface AcceptInvitationResponse {
  workspace_id: string
}

interface User {
  id: string
  email: string
  username: string
}

export default function InvitationAcceptancePage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const token = params.token as string

  const [emailMismatchError, setEmailMismatchError] = useState<{
    invitationEmail: string
    userEmail: string
  } | null>(null)

  // Fetch invitation details (public endpoint)
  const {
    data: invitation,
    isLoading,
    error,
  } = useQuery<InvitationDetails>({
    queryKey: ['invitation', token],
    queryFn: async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await fetch(`${apiUrl}/api/invitations/${token}`)
      if (!res.ok) {
        throw new Error('Invitation not found')
      }
      return res.json()
    },
    retry: false,
  })

  // Fetch current user (optional)
  const { data: currentUser } = useQuery<User | null>({
    queryKey: ['user'],
    queryFn: async () => {
      try {
        return await api.get<User>('/api/me')
      } catch {
        return null // User not authenticated
      }
    },
  })

  // Accept invitation mutation
  const { mutate: acceptInvitation, isPending: isAccepting } = useMutation<AcceptInvitationResponse>({
    mutationFn: async () => {
      return await api.post<AcceptInvitationResponse>(`/api/invitations/${token}/accept`)
    },
    onError: (error: any) => {
      console.error('Accept invitation error:', error)

      // Handle email mismatch (AC 14)
      if (error.detail?.type === 'email_mismatch') {
        setEmailMismatchError({
          invitationEmail: error.detail.invitation_email,
          userEmail: error.detail.user_email,
        })
        return
      }

      // Display error message
      toast({
        variant: 'destructive',
        title: 'Failed to accept invitation',
        description: error.message || 'An error occurred',
      })
    },
    onSuccess: (data) => {
      toast({
        title: 'Welcome aboard! 🎉',
        description: "You've successfully joined the workspace",
      })

      // Invalidate queries
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })

      // Redirect to workspace
      router.push(`/workspaces/${data.workspace_id}`)
    },
  })

  const handleSignInRedirect = () => {
    // Redirect to GitHub OAuth with return URL
    window.location.href = `/auth/github?redirect=/invitations/${token}`
  }

  const handleSignOut = async () => {
    try {
      await api.post('/auth/logout')
      setEmailMismatchError(null)
      queryClient.invalidateQueries({ queryKey: ['user'] })
      api.logout()
      toast({
        title: 'Signed out',
        description: 'Please sign in with the correct account',
      })
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Sign out failed',
        description: 'Please try again',
      })
    }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto max-w-2xl px-4 py-16">
        <Card>
          <CardContent className="pb-12 pt-12">
            <div className="text-center">
              <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="mt-4 text-muted-foreground">Loading invitation...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error || !invitation) {
    return (
      <div className="container mx-auto max-w-2xl px-4 py-16">
        <Card>
          <CardContent className="pb-12 pt-12">
            <div className="text-center">
              <AlertCircle className="mx-auto mb-4 h-12 w-12 text-destructive" />
              <h2 className="mb-2 text-2xl font-bold">Invitation Not Found</h2>
              <p className="mb-6 text-muted-foreground">
                This invitation link is invalid or has expired.
              </p>
              <Button asChild>
                <Link href="/workspaces">Go to Workspaces</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (invitation.is_accepted) {
    return (
      <div className="container mx-auto max-w-2xl px-4 py-16">
        <Card>
          <CardContent className="pb-12 pt-12">
            <div className="text-center">
              <CheckCircle2 className="mx-auto mb-4 h-12 w-12 text-green-500" />
              <h2 className="mb-2 text-2xl font-bold">Already Accepted</h2>
              <p className="mb-6 text-muted-foreground">
                This invitation has already been accepted.
              </p>
              <Button asChild>
                <Link href={`/workspaces/${invitation.workspace_id}`}>Go to Workspace</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (invitation.is_expired) {
    return (
      <div className="container mx-auto max-w-2xl px-4 py-16">
        <Card>
          <CardContent className="pb-12 pt-12">
            <div className="text-center">
              <Clock className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
              <h2 className="mb-2 text-2xl font-bold">Invitation Expired</h2>
              <p className="mb-6 text-muted-foreground">
                This invitation expired on {format(new Date(invitation.expires_at), 'MMMM d, yyyy')}
                . Please request a new invitation from the workspace admin.
              </p>
              <Button asChild>
                <Link href="/workspaces">Go to Workspaces</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Email mismatch error (AC 14)
  if (emailMismatchError) {
    return (
      <div className="container mx-auto max-w-2xl px-4 py-16">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <CardTitle>Email Address Mismatch</CardTitle>
            </div>
            <CardDescription>
              This invitation cannot be accepted with your current account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Account Mismatch</AlertTitle>
              <AlertDescription>
                This invitation was sent to <strong>{emailMismatchError.invitationEmail}</strong>,
                but you&apos;re signed in as <strong>{emailMismatchError.userEmail}</strong>.
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                To accept this invitation, you need to:
              </p>
              <ul className="ml-4 list-inside list-disc space-y-1 text-sm text-muted-foreground">
                <li>Sign out of your current account</li>
                <li>Sign in with the email address that received the invitation</li>
                <li>Return to this page and accept the invitation</li>
              </ul>
            </div>

            <div className="flex gap-2 pt-4">
              <Button onClick={handleSignOut} className="flex-1">
                Sign Out and Switch Accounts
              </Button>
              <Button variant="outline" asChild className="flex-1">
                <Link href="/workspaces">Cancel</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-2xl px-4 py-16">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <Mail className="h-8 w-8 text-primary" />
            <Badge variant={invitation.role === 'admin' ? 'default' : 'secondary'}>
              {invitation.role === 'admin' ? (
                <Shield className="mr-1 h-3 w-3" />
              ) : (
                <User className="mr-1 h-3 w-3" />
              )}
              {invitation.role.charAt(0).toUpperCase() + invitation.role.slice(1)}
            </Badge>
          </div>
          <CardTitle className="mt-4 text-2xl">
            You&apos;ve been invited to join a workspace
          </CardTitle>
          <CardDescription>
            {invitation.inviter_name || 'A team member'} has invited you to collaborate
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Workspace Info */}
          <div className="space-y-2 rounded-lg border p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">
                  {invitation.workspace_name || 'Workspace'}
                </h3>
                <p className="text-sm text-muted-foreground">
                  Invited {format(new Date(invitation.created_at), 'MMMM d, yyyy')}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              <span>Expires {format(new Date(invitation.expires_at), 'MMMM d, yyyy')}</span>
            </div>
          </div>

          {/* Email Info */}
          <div className="text-sm text-muted-foreground">
            This invitation was sent to <strong>{invitation.email}</strong>
          </div>

          {/* Actions */}
          {currentUser ? (
            <div className="space-y-3">
              <Button
                onClick={() => acceptInvitation()}
                disabled={isAccepting}
                className="w-full"
                size="lg"
              >
                {isAccepting ? 'Accepting...' : 'Accept Invitation'}
              </Button>
              <p className="text-center text-xs text-muted-foreground">
                Signed in as {currentUser.email}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <Button onClick={handleSignInRedirect} className="w-full" size="lg">
                Sign in with GitHub to Accept
              </Button>
              <p className="text-center text-xs text-muted-foreground">
                You need to sign in to accept this invitation
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
