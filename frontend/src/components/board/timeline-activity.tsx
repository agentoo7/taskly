/**
 * Timeline activity item showing card changes
 */

'use client'

import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import { formatDistanceToNow } from 'date-fns'

export function TimelineActivity({ activity }: any) {
  return (
    <div className="flex gap-3">
      <Avatar className="h-8 w-8">
        <AvatarImage src={activity.user?.avatar_url} />
        <AvatarFallback>{activity.user?.username?.[0]?.toUpperCase() || '?'}</AvatarFallback>
      </Avatar>

      <div className="flex-1">
        <div className="text-sm text-muted-foreground">
          <span className="font-medium text-foreground">
            {activity.user?.username || 'Someone'}
          </span>
          {' '}
          {activity.description}
          {' '}
          <span className="text-xs">
            {formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })}
          </span>
        </div>
      </div>
    </div>
  )
}
