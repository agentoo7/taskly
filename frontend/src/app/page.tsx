'use client'

import { useAuth } from '@/lib/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { LogOut, User } from 'lucide-react'

export default function Home() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth()

  if (isLoading) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="text-center">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-slate-300 border-t-slate-900 mx-auto" />
          <p className="text-slate-600">Loading...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="z-10 w-full max-w-5xl items-center justify-between text-center">
        <h1 className="text-4xl font-bold mb-4">Welcome to Taskly</h1>
        <p className="text-lg text-slate-600 mb-8">
          Task Management with GitHub Integration
        </p>

        {isAuthenticated && user ? (
          <Card className="p-8 max-w-md mx-auto">
            <div className="flex items-center gap-4 mb-6">
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.username}
                  className="h-16 w-16 rounded-full"
                />
              ) : (
                <div className="h-16 w-16 rounded-full bg-slate-200 flex items-center justify-center">
                  <User className="h-8 w-8 text-slate-600" />
                </div>
              )}
              <div className="text-left flex-1">
                <h2 className="text-xl font-semibold">{user.username}</h2>
                <p className="text-sm text-slate-600">{user.email}</p>
              </div>
            </div>

            <Button
              onClick={logout}
              variant="outline"
              className="w-full"
              size="lg"
            >
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </Card>
        ) : (
          <Card className="p-8 max-w-md mx-auto">
            <p className="text-slate-600 mb-6">
              Sign in with your GitHub account to get started.
            </p>
            <Button onClick={login} className="w-full" size="lg">
              Sign in with GitHub
            </Button>
          </Card>
        )}

        <div className="mt-12">
          <p className="text-sm text-slate-500">
            Move a Card, Ship the Code
          </p>
        </div>
      </div>
    </main>
  )
}
