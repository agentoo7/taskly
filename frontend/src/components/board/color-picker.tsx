/**
 * Color picker component for selecting label colors
 */

'use client'

import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

const PRESET_COLORS = [
  { name: 'Red', value: '#EF4444' },
  { name: 'Orange', value: '#F97316' },
  { name: 'Yellow', value: '#EAB308' },
  { name: 'Green', value: '#22C55E' },
  { name: 'Teal', value: '#14B8A6' },
  { name: 'Blue', value: '#3B82F6' },
  { name: 'Indigo', value: '#6366F1' },
  { name: 'Purple', value: '#A855F7' },
  { name: 'Pink', value: '#EC4899' },
  { name: 'Brown', value: '#92400E' },
  { name: 'Gray', value: '#6B7280' },
  { name: 'Black', value: '#1F2937' },
]

interface ColorPickerProps {
  value: string
  onChange: (color: string) => void
}

export function ColorPicker({ value, onChange }: ColorPickerProps) {
  return (
    <div className="grid grid-cols-6 gap-2">
      {PRESET_COLORS.map((color) => (
        <button
          key={color.value}
          type="button"
          className={cn(
            'w-10 h-10 rounded-md border-2 flex items-center justify-center transition-transform hover:scale-110',
            value === color.value ? 'border-foreground' : 'border-transparent'
          )}
          style={{ backgroundColor: color.value }}
          onClick={() => onChange(color.value)}
          title={color.name}
        >
          {value === color.value && <Check className="h-5 w-5 text-white" />}
        </button>
      ))}
    </div>
  )
}
