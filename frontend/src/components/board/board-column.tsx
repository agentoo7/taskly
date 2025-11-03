/**
 * Board column component displaying cards in a column.
 */

'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Plus, GripVertical, MoreVertical, Pencil, Trash2 } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

interface Column {
  id: string
  name: string
  position: number
}

interface BoardColumnProps {
  column: Column
  onRename: (columnId: string, newName: string) => void
  onDelete: (columnId: string) => void
}

export function BoardColumn({ column, onRename, onDelete }: BoardColumnProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [name, setName] = useState(column.name)

  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: column.id,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  const handleRename = () => {
    if (name.trim() && name !== column.name) {
      onRename(column.id, name.trim())
    } else {
      setName(column.name)
    }
    setIsEditing(false)
  }

  const handleDelete = () => {
    if (confirm(`Delete "${column.name}" column?`)) {
      onDelete(column.id)
    }
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="flex-shrink-0 w-80 bg-muted/50 rounded-lg p-4 flex flex-col h-full max-h-[calc(100vh-12rem)]"
    >
      {/* Column Header */}
      <div className="flex items-center justify-between mb-4 group">
        <div className="flex items-center gap-2 flex-1">
          <button
            className="cursor-grab opacity-0 group-hover:opacity-100 transition-opacity"
            {...attributes}
            {...listeners}
          >
            <GripVertical className="h-4 w-4 text-muted-foreground" />
          </button>

          {isEditing ? (
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              onBlur={handleRename}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleRename()
                if (e.key === 'Escape') {
                  setName(column.name)
                  setIsEditing(false)
                }
              }}
              className="h-7 text-sm font-semibold"
            />
          ) : (
            <button
              type="button"
              className="text-sm font-semibold cursor-pointer hover:text-foreground/80 bg-transparent border-none p-0"
              onClick={() => setIsEditing(true)}
            >
              {column.name}
              <span className="ml-2 text-xs text-muted-foreground">0</span>
            </button>
          )}
        </div>

        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
            <Plus className="h-4 w-4" />
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setIsEditing(true)}>
                <Pencil className="mr-2 h-4 w-4" />
                Rename Column
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleDelete} className="text-destructive">
                <Trash2 className="mr-2 h-4 w-4" />
                Delete Column
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Cards Container */}
      <div className="space-y-2 flex-1 overflow-y-auto min-h-[200px]">
        <p className="text-sm text-muted-foreground text-center py-8">
          Drag cards here or click + to add
        </p>
      </div>
    </div>
  )
}
