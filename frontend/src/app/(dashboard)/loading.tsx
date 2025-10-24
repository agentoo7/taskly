/**
 * Loading state for dashboard pages.
 */

export default function DashboardLoading() {
  return (
    <div className="container py-8">
      <div className="mb-8">
        <div className="h-10 w-64 animate-pulse rounded bg-muted" />
        <div className="mt-2 h-6 w-96 animate-pulse rounded bg-muted" />
      </div>
      <div className="h-64 animate-pulse rounded bg-muted" />
    </div>
  )
}
