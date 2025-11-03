/**
 * Filter bar component for filtering cards by assignee, label, and priority
 */

'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Filter, X, Users, Tag, AlertCircle } from 'lucide-react'
import { Label } from '@/lib/types/label'
import { User } from '@/lib/types/user'
import { Priority } from '@/lib/types/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'

interface FilterBarProps {
  workspaceMembers: User[]
  workspaceLabels: Label[]
  selectedAssignees: string[]
  selectedLabels: string[]
  selectedPriorities: Priority[]
  onAssigneeChange: (assigneeIds: string[]) => void
  onLabelChange: (labelIds: string[]) => void
  onPriorityChange: (priorities: Priority[]) => void
  onClearFilters: () => void
}

const PRIORITY_OPTIONS: { value: Priority; label: string; color: string }[] = [
  { value: 'none', label: 'None', color: 'bg-gray-400' },
  { value: 'low', label: 'Low', color: 'bg-blue-500' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-500' },
  { value: 'high', label: 'High', color: 'bg-orange-500' },
  { value: 'urgent', label: 'Urgent', color: 'bg-red-500' },
]

// Helper to determine text color for labels
function getContrastColor(hexColor: string): string {
  const r = parseInt(hexColor.slice(1, 3), 16)
  const g = parseInt(hexColor.slice(3, 5), 16)
  const b = parseInt(hexColor.slice(5, 7), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? '#000000' : '#FFFFFF'
}

export function FilterBar({
  workspaceMembers,
  workspaceLabels,
  selectedAssignees,
  selectedLabels,
  selectedPriorities,
  onAssigneeChange,
  onLabelChange,
  onPriorityChange,
  onClearFilters,
}: FilterBarProps) {
  const [assigneePopoverOpen, setAssigneePopoverOpen] = useState(false)
  const [labelPopoverOpen, setLabelPopoverOpen] = useState(false)
  const [priorityPopoverOpen, setPriorityPopoverOpen] = useState(false)

  const hasFilters =
    selectedAssignees.length > 0 || selectedLabels.length > 0 || selectedPriorities.length > 0

  const toggleAssignee = (assigneeId: string) => {
    if (selectedAssignees.includes(assigneeId)) {
      onAssigneeChange(selectedAssignees.filter((id) => id !== assigneeId))
    } else {
      onAssigneeChange([...selectedAssignees, assigneeId])
    }
  }

  const toggleLabel = (labelId: string) => {
    if (selectedLabels.includes(labelId)) {
      onLabelChange(selectedLabels.filter((id) => id !== labelId))
    } else {
      onLabelChange([...selectedLabels, labelId])
    }
  }

  const togglePriority = (priority: Priority) => {
    if (selectedPriorities.includes(priority)) {
      onPriorityChange(selectedPriorities.filter((p) => p !== priority))
    } else {
      onPriorityChange([...selectedPriorities, priority])
    }
  }

  const removeAssignee = (assigneeId: string) => {
    onAssigneeChange(selectedAssignees.filter((id) => id !== assigneeId))
  }

  const removeLabel = (labelId: string) => {
    onLabelChange(selectedLabels.filter((id) => id !== labelId))
  }

  const removePriority = (priority: Priority) => {
    onPriorityChange(selectedPriorities.filter((p) => p !== priority))
  }

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {/* Filter Popovers */}
      <div className="flex items-center gap-2">
        {/* Assignee Filter */}
        <Popover open={assigneePopoverOpen} onOpenChange={setAssigneePopoverOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className={cn(
                'gap-2',
                selectedAssignees.length > 0 && 'border-primary bg-primary/5'
              )}
            >
              <Users className="h-4 w-4" />
              Assignee
              {selectedAssignees.length > 0 && (
                <Badge variant="secondary" className="ml-1 h-5 px-1.5">
                  {selectedAssignees.length}
                </Badge>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-64 p-0" align="start">
            <div className="border-b p-3">
              <p className="text-sm font-medium">Filter by Assignee</p>
            </div>
            <div className="max-h-64 overflow-y-auto p-2">
              {workspaceMembers.length === 0 ? (
                <div className="py-4 text-center text-sm text-muted-foreground">
                  No workspace members
                </div>
              ) : (
                <div className="space-y-1">
                  {workspaceMembers.map((member) => (
                    <button
                      key={member.id}
                      className={cn(
                        'flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-accent',
                        selectedAssignees.includes(member.id) && 'bg-accent'
                      )}
                      onClick={() => toggleAssignee(member.id)}
                    >
                      <Avatar className="h-6 w-6">
                        <AvatarImage src={member.avatar_url || undefined} alt={member.username} />
                        <AvatarFallback className="text-xs">
                          {member.username.slice(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <span className="flex-1 text-left">{member.username}</span>
                      {selectedAssignees.includes(member.id) && (
                        <div className="h-4 w-4 rounded-sm bg-primary text-primary-foreground flex items-center justify-center">
                          <span className="text-xs">✓</span>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </PopoverContent>
        </Popover>

        {/* Label Filter */}
        <Popover open={labelPopoverOpen} onOpenChange={setLabelPopoverOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className={cn('gap-2', selectedLabels.length > 0 && 'border-primary bg-primary/5')}
            >
              <Tag className="h-4 w-4" />
              Label
              {selectedLabels.length > 0 && (
                <Badge variant="secondary" className="ml-1 h-5 px-1.5">
                  {selectedLabels.length}
                </Badge>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-64 p-0" align="start">
            <div className="border-b p-3">
              <p className="text-sm font-medium">Filter by Label</p>
            </div>
            <div className="max-h-64 overflow-y-auto p-2">
              {workspaceLabels.length === 0 ? (
                <div className="py-4 text-center text-sm text-muted-foreground">
                  No labels available
                </div>
              ) : (
                <div className="space-y-1">
                  {workspaceLabels.map((label) => (
                    <button
                      key={label.id}
                      className={cn(
                        'flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-accent',
                        selectedLabels.includes(label.id) && 'bg-accent'
                      )}
                      onClick={() => toggleLabel(label.id)}
                    >
                      <div
                        className="h-6 w-6 rounded-md flex-shrink-0"
                        style={{ backgroundColor: label.color }}
                      />
                      <span className="flex-1 text-left">{label.name}</span>
                      {selectedLabels.includes(label.id) && (
                        <div className="h-4 w-4 rounded-sm bg-primary text-primary-foreground flex items-center justify-center">
                          <span className="text-xs">✓</span>
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </PopoverContent>
        </Popover>

        {/* Priority Filter */}
        <Popover open={priorityPopoverOpen} onOpenChange={setPriorityPopoverOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className={cn(
                'gap-2',
                selectedPriorities.length > 0 && 'border-primary bg-primary/5'
              )}
            >
              <AlertCircle className="h-4 w-4" />
              Priority
              {selectedPriorities.length > 0 && (
                <Badge variant="secondary" className="ml-1 h-5 px-1.5">
                  {selectedPriorities.length}
                </Badge>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-56 p-0" align="start">
            <div className="border-b p-3">
              <p className="text-sm font-medium">Filter by Priority</p>
            </div>
            <div className="p-2">
              <div className="space-y-1">
                {PRIORITY_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    className={cn(
                      'flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-accent',
                      selectedPriorities.includes(option.value) && 'bg-accent'
                    )}
                    onClick={() => togglePriority(option.value)}
                  >
                    <div className={cn('w-3 h-3 rounded-full', option.color)} />
                    <span className="flex-1 text-left">{option.label}</span>
                    {selectedPriorities.includes(option.value) && (
                      <div className="h-4 w-4 rounded-sm bg-primary text-primary-foreground flex items-center justify-center">
                        <span className="text-xs">✓</span>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </PopoverContent>
        </Popover>
      </div>

      {/* Active Filters */}
      {hasFilters && (
        <>
          <div className="h-6 w-px bg-border" />

          {/* Selected Assignees */}
          {selectedAssignees.map((assigneeId) => {
            const member = workspaceMembers.find((m) => m.id === assigneeId)
            if (!member) return null
            return (
              <Badge key={assigneeId} variant="secondary" className="gap-1.5 pr-1">
                <Avatar className="h-4 w-4">
                  <AvatarImage src={member.avatar_url || undefined} />
                  <AvatarFallback className="text-[10px]">
                    {member.username.slice(0, 2).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <span>{member.username}</span>
                <button
                  onClick={() => removeAssignee(assigneeId)}
                  className="hover:bg-secondary-foreground/20 rounded-sm p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )
          })}

          {/* Selected Labels */}
          {selectedLabels.map((labelId) => {
            const label = workspaceLabels.find((l) => l.id === labelId)
            if (!label) return null
            return (
              <Badge
                key={labelId}
                className="gap-1.5 pr-1"
                style={{
                  backgroundColor: label.color,
                  color: getContrastColor(label.color),
                }}
              >
                <span>{label.name}</span>
                <button
                  onClick={() => removeLabel(labelId)}
                  className="hover:opacity-80 rounded-sm p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )
          })}

          {/* Selected Priorities */}
          {selectedPriorities.map((priority) => {
            const option = PRIORITY_OPTIONS.find((o) => o.value === priority)
            if (!option) return null
            return (
              <Badge key={priority} variant="secondary" className="gap-1.5 pr-1">
                <div className={cn('w-2 h-2 rounded-full', option.color)} />
                <span>{option.label}</span>
                <button
                  onClick={() => removePriority(priority)}
                  className="hover:bg-secondary-foreground/20 rounded-sm p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )
          })}

          {/* Clear All Filters */}
          <Button variant="ghost" size="sm" onClick={onClearFilters} className="h-7 text-xs">
            Clear all
          </Button>
        </>
      )}
    </div>
  )
}
