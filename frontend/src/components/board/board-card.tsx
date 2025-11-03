/**
 * Board card component for displaying cards in collapsed view
 */

'use client'

import { Card as CardType, Priority } from '@/lib/types/card'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Calendar, AlertCircle } from 'lucide-react'
import { format, isPast, isToday } from 'date-fns'
import { cn } from '@/lib/utils'

interface BoardCardProps {
  card: CardType
  onClick: () => void
}

const PRIORITY_COLORS: Record<Priority, string> = {
  none: 'bg-gray-400',
  low: 'bg-blue-500',
  medium: 'bg-yellow-500',
  high: 'bg-orange-500',
  urgent: 'bg-red-500',
}

export function BoardCard({ card, onClick }: BoardCardProps) {
  // Check if card is overdue (past due date and not in "Done" column)
  // Note: We'll need to pass column name or check column_id against known "Done" column IDs
  const isOverdue = card.due_date && isPast(new Date(card.due_date))
  const isDueToday = card.due_date && isToday(new Date(card.due_date))

  return (
    <Card
      className="p-3 cursor-pointer hover:shadow-md transition-shadow bg-card"
      onClick={onClick}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick()
        }
      }}
      role="button"
      aria-label={`Card: ${card.title}`}
    >
      {/* Priority Indicator */}
      {card.priority !== 'none' && (
        <div className="flex items-center gap-2 mb-2">
          <div
            className={cn('w-2 h-2 rounded-full', PRIORITY_COLORS[card.priority])}
            aria-label={`Priority: ${card.priority}`}
          />
        </div>
      )}

      {/* Title */}
      <h4 className="text-sm font-medium line-clamp-2 mb-2">{card.title}</h4>

      {/* Metadata Badges */}
      <div className="flex items-center gap-2 flex-wrap">
        {card.due_date && (
          <Badge
            variant="outline"
            className={cn(
              'text-xs',
              isOverdue && 'border-red-500 text-red-600 bg-red-50 dark:bg-red-950',
              isDueToday && 'border-yellow-500 text-yellow-600 bg-yellow-50 dark:bg-yellow-950',
              !isOverdue && !isDueToday && 'border-green-500 text-green-600 bg-green-50 dark:bg-green-950'
            )}
          >
            {isOverdue && <AlertCircle className="mr-1 h-3 w-3" />}
            <Calendar className="mr-1 h-3 w-3" />
            Due: {format(new Date(card.due_date), 'MMM dd')}
          </Badge>
        )}

        {card.story_points !== null && card.story_points !== undefined && (
          <Badge variant="secondary" className="text-xs">
            {card.story_points} pts
          </Badge>
        )}
      </div>
    </Card>
  )
}
