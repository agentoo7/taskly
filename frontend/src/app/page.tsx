import { HomeContent } from '@/components/home-content'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between text-center">
        <h1 className="mb-4 text-4xl font-bold">Welcome to Taskly</h1>
        <p className="mb-8 text-lg text-slate-600">Task Management with GitHub Integration</p>
        <HomeContent />
      </div>
    </main>
  )
}
