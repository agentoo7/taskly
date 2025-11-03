/**
 * Board card component for displaying cards in collapsed view
 */

'use client'

import { Card as CardType, Priority } from '@/lib/types/card'
import { Badge } from '@/components/ui/badge'
import { Calendar, AlertCircle } from 'lucide-react'
import { format, isPast, isToday } from 'date-fns'
import { cn } from '@/lib/utils'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useCardSelectionStore } from '@/store/card-selection-store'
import { Checkbox } from '@/components/ui/checkbox'

interface BoardCardProps {
  card: CardType
  onClick: () => void
  isArchived?: boolean
}

const PRIORITY_COLORS: Record<Priority, string> = {
  none: 'bg-gray-400',
  low: 'bg-blue-500',
  medium: 'bg-yellow-500',
  high: 'bg-orange-500',
  urgent: 'bg-red-500',
}

export function BoardCard({ card, onClick, isArchived = false }: BoardCardProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: `card-${card.id}`,
    disabled: isArchived, // Disable sorting for archived boards
  })

  const { isSelected, toggleCard } = useCardSelectionStore()
  const selected = isSelected(card.id)

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const handleCheckboxClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    toggleCard(card.id)
  }

  const handleCardClick = (e: React.MouseEvent) => {
    // Don't open modal if clicking during drag or if card is selected
    if (isDragging) return
    onClick()
  }

  // Check if card is overdue (past due date and not in "Done" column)
  // Note: We'll need to pass column name or check column_id against known "Done" column IDs
  const isOverdue = card.due_date && isPast(new Date(card.due_date))
  const isDueToday = card.due_date && isToday(new Date(card.due_date))

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...(isArchived ? {} : { ...attributes, ...listeners })}
      className={cn(
        'rounded-lg border bg-card text-card-foreground shadow-sm p-3 transition-all group relative',
        !isArchived && 'cursor-pointer hover:shadow-md',
        isArchived && 'cursor-not-allowed opacity-75',
        isDragging && 'opacity-50',
        selected && 'ring-2 ring-primary bg-primary/5'
      )}
      onClick={!isArchived ? handleCardClick : undefined}
      tabIndex={0}
      onKeyDown={(e) => {
        if (!isArchived && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault()
          onClick()
        }
      }}
      role="button"
      aria-label={`Card: ${card.title}${isArchived ? ' (archived, read-only)' : ''}`}
      title={isArchived ? 'Cards cannot be moved in archived boards' : undefined}
    >
      {/* Selection Checkbox */}
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
        <Checkbox
          checked={selected}
          aria-label={selected ? 'Deselect card' : 'Select card'}
          onCheckedChange={(checked) => {
            // Stop propagation to prevent card click
            toggleCard(card.id)
          }}
          onClick={(e: React.MouseEvent) => e.stopPropagation()}
        />
      </div>

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
    </div>
  )
}
