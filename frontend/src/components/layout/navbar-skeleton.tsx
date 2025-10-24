/**
 * Navbar loading skeleton component.
 */

export function NavbarSkeleton() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background">
      <div className="container mx-auto flex h-14 max-w-7xl items-center px-4 sm:px-6 lg:px-8">
        <div className="h-6 w-24 animate-pulse rounded bg-muted" />
        <div className="ml-auto h-8 w-8 animate-pulse rounded-full bg-muted" />
      </div>
    </header>
  )
}
