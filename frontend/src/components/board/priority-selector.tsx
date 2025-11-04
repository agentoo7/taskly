/**
 * Priority selector component for card priority selection
 */

'use client'

import { Priority } from '@/lib/types/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { cn } from '@/lib/utils'

interface PrioritySelectorProps {
  value: Priority
  onChange: (priority: Priority) => void
  disabled?: boolean
}

interface PriorityOption {
  value: Priority
  label: string
  color: string
}

const PRIORITY_OPTIONS: PriorityOption[] = [
  { value: 'none', label: 'None', color: 'bg-gray-400' },
  { value: 'low', label: 'Low', color: 'bg-blue-500' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-500' },
  { value: 'high', label: 'High', color: 'bg-orange-500' },
  { value: 'urgent', label: 'Urgent', color: 'bg-red-500' },
]

export function PrioritySelector({ value, onChange, disabled }: PrioritySelectorProps) {
  const currentOption = PRIORITY_OPTIONS.find((opt) => opt.value === value) || PRIORITY_OPTIONS[0]

  return (
    <Select value={value} onValueChange={onChange as (value: string) => void} disabled={disabled}>
      <SelectTrigger className="w-full">
        <SelectValue>
          <div className="flex items-center gap-2">
            <div className={cn('w-2 h-2 rounded-full', currentOption.color)} />
            <span>{currentOption.label}</span>
          </div>
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {PRIORITY_OPTIONS.map((option) => (
          <SelectItem key={option.value} value={option.value}>
            <div className="flex items-center gap-2">
              <div className={cn('w-2 h-2 rounded-full', option.color)} />
              <span>{option.label}</span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
