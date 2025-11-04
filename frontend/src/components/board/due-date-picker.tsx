/**
 * Due date picker component for card due dates
 */

'use client'

import { useState } from 'react'
import { format, addDays, startOfToday, startOfTomorrow } from 'date-fns'
import { Calendar as CalendarIcon, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { cn } from '@/lib/utils'

interface DueDatePickerProps {
  value: string | null // ISO date string
  onChange: (date: string | null) => void
  disabled?: boolean
}

export function DueDatePicker({ value, onChange, disabled }: DueDatePickerProps) {
  const [open, setOpen] = useState(false)
  const selectedDate = value ? new Date(value) : undefined

  const handleSelectDate = (date: Date | undefined) => {
    if (date) {
      // Convert to ISO date string (YYYY-MM-DD)
      const isoDate = format(date, 'yyyy-MM-dd')
      onChange(isoDate)
      setOpen(false)
    }
  }

  const handleQuickSelect = (date: Date) => {
    const isoDate = format(date, 'yyyy-MM-dd')
    onChange(isoDate)
    setOpen(false)
  }

  const handleClear = () => {
    onChange(null)
    setOpen(false)
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            'w-full justify-start text-left font-normal',
            !value && 'text-muted-foreground'
          )}
          disabled={disabled}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {value ? format(new Date(value), 'PPP') : 'Set due date'}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <div className="p-3 border-b space-y-2">
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start"
            onClick={() => handleQuickSelect(startOfToday())}
          >
            Today
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start"
            onClick={() => handleQuickSelect(startOfTomorrow())}
          >
            Tomorrow
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start"
            onClick={() => handleQuickSelect(addDays(startOfToday(), 7))}
          >
            Next Week
          </Button>
          {value && (
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start text-destructive hover:text-destructive"
              onClick={handleClear}
            >
              <X className="mr-2 h-4 w-4" />
              Clear
            </Button>
          )}
        </div>
        <Calendar
          mode="single"
          selected={selectedDate}
          onSelect={handleSelectDate}
          initialFocus
        />
      </PopoverContent>
    </Popover>
  )
}
