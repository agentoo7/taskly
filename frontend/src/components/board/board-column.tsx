/**
 * Board column component displaying cards in a column.
 */

'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Plus, GripVertical, MoreVertical, Pencil, Trash2, Loader2 } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useSortable } from '@dnd-kit/sortable'
import { useDroppable } from '@dnd-kit/core'
import { CSS } from '@dnd-kit/utilities'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { DeleteColumnDialog } from './delete-column-dialog'
import { BoardCard } from './board-card'
import { CardDetailModal } from './card-detail-modal'
import { Card as CardType } from '@/lib/types/card'
import { toast } from 'sonner'

interface Column {
  id: string
  name: string
  position: number
}

interface BoardColumnProps {
  column: Column
  cards: CardType[]
  boardId: string
  workspaceId: string
  otherColumns: Column[]
  onRename: (columnId: string, newName: string) => void
  onDelete: (columnId: string, action: 'delete-cards' | 'move-cards', targetColumnId?: string) => void
  isArchived?: boolean
}

// Mock API client - will be replaced with actual implementation
const api = {
  post: async (url: string, data: any) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error('Failed to create card')
    return response.json()
  },
}

export function BoardColumn({ column, cards, boardId, workspaceId, otherColumns, onRename, onDelete, isArchived = false }: BoardColumnProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showQuickCreate, setShowQuickCreate] = useState(false)
  const [quickCreateTitle, setQuickCreateTitle] = useState('')
  const [selectedCard, setSelectedCard] = useState<CardType | null>(null)
  const [name, setName] = useState(column.name)
  const queryClient = useQueryClient()

  const createCardMutation = useMutation({
    mutationFn: (title: string) =>
      api.post(`/api/boards/${boardId}/cards`, {
        title,
        column_id: column.id,
        board_id: boardId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })
      setQuickCreateTitle('')
      setShowQuickCreate(false)
      toast.success('Card created')
    },
    onError: (error: Error) => {
      toast.error(`Failed to create card: ${error.message}`)
    },
  })

  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: column.id,
  })

  const { setNodeRef: setDroppableNodeRef, isOver } = useDroppable({
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

  const handleDeleteConfirm = (action: 'delete-cards' | 'move-cards', targetColumnId?: string) => {
    onDelete(column.id, action, targetColumnId)
  }

  const handleQuickCreate = () => {
    if (quickCreateTitle.trim()) {
      createCardMutation.mutate(quickCreateTitle.trim())
    }
  }

  const handleQuickCreateKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleQuickCreate()
    } else if (e.key === 'Escape') {
      setShowQuickCreate(false)
      setQuickCreateTitle('')
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
              <span className="ml-2 text-xs text-muted-foreground">{cards.length}</span>
            </button>
          )}
        </div>

        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0"
            onClick={() => setShowQuickCreate(true)}
            disabled={showQuickCreate}
          >
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
              <DropdownMenuItem onClick={() => setShowDeleteDialog(true)} className="text-destructive">
                <Trash2 className="mr-2 h-4 w-4" />
                Delete Column
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Quick Create Input */}
      {showQuickCreate && (
        <div className="mb-2">
          <Input
            value={quickCreateTitle}
            onChange={(e) => setQuickCreateTitle(e.target.value)}
            onKeyDown={handleQuickCreateKeyDown}
            onBlur={() => {
              if (!quickCreateTitle.trim()) {
                setShowQuickCreate(false)
              }
            }}
            placeholder="Card title..."
            // eslint-disable-next-line jsx-a11y/no-autofocus
            autoFocus
            disabled={createCardMutation.isPending}
            className="text-sm"
          />
          {createCardMutation.isPending && (
            <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
              <Loader2 className="h-3 w-3 animate-spin" />
              Creating card...
            </div>
          )}
        </div>
      )}

      {/* Cards Container */}
      <div
        ref={setDroppableNodeRef}
        className={`space-y-2 flex-1 overflow-y-auto min-h-[200px] rounded-md transition-colors ${
          isOver ? 'bg-primary/5 ring-2 ring-primary/20' : ''
        }`}
      >
        <SortableContext items={cards.map((card) => `card-${card.id}`)} strategy={verticalListSortingStrategy}>
          {cards.length > 0 ? (
            cards.map((card) => (
              <BoardCard key={card.id} card={card} onClick={() => setSelectedCard(card)} isArchived={isArchived} />
            ))
          ) : (
            <p className="text-sm text-muted-foreground text-center py-8">
              {isArchived ? 'No cards in this column' : 'Drag cards here or click + to add'}
            </p>
          )}
        </SortableContext>
      </div>

      {/* Card Detail Modal */}
      {selectedCard && (
        <CardDetailModal
          card={selectedCard}
          open={!!selectedCard}
          onOpenChange={(open) => !open && setSelectedCard(null)}
          boardId={boardId}
          workspaceId={workspaceId}
        />
      )}

      {/* Delete Column Dialog */}
      <DeleteColumnDialog
        open={showDeleteDialog}
        onOpenChange={setShowDeleteDialog}
        column={column}
        cardCount={cards.length}
        otherColumns={otherColumns}
        onConfirmDelete={handleDeleteConfirm}
      />
    </div>
  )
}
