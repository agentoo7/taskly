'use client'

import { useAuth } from '@/lib/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { LogOut, User } from 'lucide-react'
import Image from 'next/image'
import { useEffect, useState } from 'react'

export function HomeContent() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  // Prevent hydration mismatch by showing loading state until mounted
  if (!mounted || isLoading) {
    return (
      <div className="text-center">
        <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-slate-300 border-t-slate-900" />
        <p className="text-slate-600">Loading...</p>
      </div>
    )
  }

  return (
    <>
      {isAuthenticated && user ? (
        <Card className="mx-auto max-w-md p-8">
          <div className="mb-6 flex items-center gap-4">
            {user.avatar_url ? (
              <Image
                src={user.avatar_url}
                alt={user.username}
                width={64}
                height={64}
                className="h-16 w-16 rounded-full"
                unoptimized
              />
            ) : (
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-200">
                <User className="h-8 w-8 text-slate-600" />
              </div>
            )}
            <div className="flex-1 text-left">
              <h2 className="text-xl font-semibold">{user.username}</h2>
              <p className="text-sm text-slate-600">{user.email}</p>
            </div>
          </div>

          <Button onClick={logout} variant="outline" className="w-full" size="lg">
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </Card>
      ) : (
        <Card className="mx-auto max-w-md p-8">
          <p className="mb-6 text-slate-600">Sign in with your GitHub account to get started.</p>
          <Button onClick={login} className="w-full" size="lg">
            Sign in with GitHub
          </Button>
        </Card>
      )}

      <div className="mt-12">
        <p className="text-sm text-slate-500">Move a Card, Ship the Code</p>
      </div>
    </>
  )
}
