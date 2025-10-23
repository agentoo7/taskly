export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between text-center">
        <h1 className="text-4xl font-bold mb-4">Welcome to Taskly</h1>
        <p className="text-lg text-muted-foreground">
          Task Management with GitHub Integration
        </p>
        <div className="mt-8">
          <p className="text-sm text-muted-foreground">
            Frontend running on port 3000
          </p>
        </div>
      </div>
    </main>
  )
}
