/**
 * Board view page displaying columns and cards.
 */

'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { api } from '@/lib/api/client'
import { BoardColumn } from '@/components/board/board-column'
import { Button } from '@/components/ui/button'
import { Plus, Settings, MoveRight } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  DndContext,
  closestCenter,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  TouchSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragStartEvent,
  DragOverlay,
  DragOverEvent,
  pointerWithin,
  rectIntersection,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  horizontalListSortingStrategy,
} from '@dnd-kit/sortable'
import { BoardCard as BoardCardComponent } from '@/components/board/board-card'
import { FilterBar } from '@/components/board/filter-bar'
import { v4 as uuidv4 } from 'uuid'
import { Card, Priority } from '@/lib/types/card'
import { Label } from '@/lib/types/label'
import { User } from '@/lib/types/user'
import { useBoardWebSocket } from '@/hooks/use-board-websocket'
import { useCardSelectionStore } from '@/store/card-selection-store'
import { X } from 'lucide-react'

interface Column {
  id: string
  name: string
  position: number
}

interface Board {
  id: string
  workspace_id: string
  name: string
  columns: Column[]
  archived: boolean
  created_at: string
  updated_at: string
}

export default function BoardPage() {
  const params = useParams()
  const boardId = params.boardId as string
  const workspaceId = params.workspaceId as string
  const router = useRouter()
  const searchParams = useSearchParams()
  const queryClient = useQueryClient()
  const [editingName, setEditingName] = useState(false)
  const [activeCard, setActiveCard] = useState<Card | null>(null)
  const [activeColumn, setActiveColumn] = useState<string | null>(null)
  const [lastMove, setLastMove] = useState<{
    cardId: string
    oldColumnId: string
    oldPosition: number
  } | null>(null)
  const undoTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Initialize filter state from URL query params
  const getInitialFilters = () => {
    const assignees = searchParams.get('assignees')?.split(',').filter(Boolean) || []
    const labels = searchParams.get('labels')?.split(',').filter(Boolean) || []
    const priorities = searchParams.get('priorities')?.split(',').filter(Boolean) as Priority[] || []
    return { assignees, labels, priorities }
  }

  const initialFilters = getInitialFilters()
  const [selectedAssignees, setSelectedAssignees] = useState<string[]>(initialFilters.assignees)
  const [selectedLabels, setSelectedLabels] = useState<string[]>(initialFilters.labels)
  const [selectedPriorities, setSelectedPriorities] = useState<Priority[]>(initialFilters.priorities)

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams()

    if (selectedAssignees.length > 0) {
      params.set('assignees', selectedAssignees.join(','))
    }

    if (selectedLabels.length > 0) {
      params.set('labels', selectedLabels.join(','))
    }

    if (selectedPriorities.length > 0) {
      params.set('priorities', selectedPriorities.join(','))
    }

    const queryString = params.toString()
    const newUrl = queryString
      ? `/workspaces/${workspaceId}/boards/${boardId}?${queryString}`
      : `/workspaces/${workspaceId}/boards/${boardId}`

    router.replace(newUrl, { scroll: false })
  }, [selectedAssignees, selectedLabels, selectedPriorities, workspaceId, boardId, router])

  // Cleanup undo timeout on unmount
  useEffect(() => {
    return () => {
      if (undoTimeoutRef.current) {
        clearTimeout(undoTimeoutRef.current)
      }
    }
  }, [])

  const { data: board, isLoading } = useQuery({
    queryKey: ['boards', boardId],
    queryFn: () => api.get<Board>(`/api/boards/${boardId}`),
  })

  // Fetch cards for the board
  const { data: cards = [] } = useQuery({
    queryKey: ['boards', boardId, 'cards'],
    queryFn: () => api.get<Card[]>(`/api/boards/${boardId}/cards`),
    enabled: !!boardId,
  })

  // Fetch workspace members for filter
  const { data: workspaceMembers = [] } = useQuery({
    queryKey: ['workspaces', workspaceId, 'members'],
    queryFn: () => api.get<User[]>(`/api/workspaces/${workspaceId}/members`),
    enabled: !!workspaceId,
  })

  // Fetch workspace labels for filter
  const { data: workspaceLabels = [] } = useQuery({
    queryKey: ['workspace-labels', workspaceId],
    queryFn: () => api.get<Label[]>(`/api/workspaces/${workspaceId}/labels`),
    enabled: !!workspaceId,
  })

  // Apply filters to cards
  const filteredCards = cards.filter((card) => {
    // Filter by assignees
    if (selectedAssignees.length > 0) {
      const cardAssigneeIds = card.assignees?.map((a) => a.id) || []
      const hasSelectedAssignee = selectedAssignees.some((id) => cardAssigneeIds.includes(id))
      if (!hasSelectedAssignee) return false
    }

    // Filter by labels
    if (selectedLabels.length > 0) {
      const cardLabelIds = card.labels?.map((l) => l.id) || []
      const hasSelectedLabel = selectedLabels.some((id) => cardLabelIds.includes(id))
      if (!hasSelectedLabel) return false
    }

    // Filter by priorities
    if (selectedPriorities.length > 0) {
      if (!selectedPriorities.includes(card.priority)) return false
    }

    return true
  })

  const clearFilters = () => {
    setSelectedAssignees([])
    setSelectedLabels([])
    setSelectedPriorities([])
  }

  // Real-time WebSocket connection for board updates
  useBoardWebSocket(boardId)

  // Card selection state
  const { selectedCards, clearSelection, selectionCount } = useCardSelectionStore()
  const hasSelection = selectionCount() > 0

  // Disable drag sensors when board is archived
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px movement required to start drag
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 250, // 250ms long press for mobile
        tolerance: 5,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  // Determine if drag-and-drop should be enabled
  const isDragEnabled = board ? !board.archived : true

  const updateBoardMutation = useMutation({
    mutationFn: (data: Partial<Board>) => api.patch<Board>(`/api/boards/${boardId}`, data),
    onMutate: async (newData) => {
      await queryClient.cancelQueries({ queryKey: ['boards', boardId] })
      const previous = queryClient.getQueryData(['boards', boardId])
      queryClient.setQueryData(['boards', boardId], (old: any) => ({
        ...old,
        ...newData,
      }))
      return { previous }
    },
    onError: (err, variables, context) => {
      queryClient.setQueryData(['boards', boardId], context?.previous)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', boardId] })
    },
  })

  const handleUndo = () => {
    if (!lastMove) return

    // Clear timeout immediately when undo is clicked
    if (undoTimeoutRef.current) {
      clearTimeout(undoTimeoutRef.current)
      undoTimeoutRef.current = null
    }

    // Move card back to original position
    moveCardMutation.mutate({
      cardId: lastMove.cardId,
      columnId: lastMove.oldColumnId,
      position: lastMove.oldPosition,
    })

    setLastMove(null)
  }

  const moveCardMutation = useMutation({
    mutationFn: ({ cardId, columnId, position }: { cardId: string; columnId: string; position: number }) =>
      api.patch(`/api/cards/${cardId}/move`, { column_id: columnId, position }),
    onMutate: async ({ cardId, columnId, position }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['boards', boardId, 'cards'] })

      // Snapshot previous value
      const previousCards = queryClient.getQueryData<Card[]>(['boards', boardId, 'cards'])

      // Store previous position for undo
      const card = previousCards?.find((c) => c.id === cardId)
      if (card) {
        setLastMove({
          cardId: card.id,
          oldColumnId: card.column_id,
          oldPosition: card.position,
        })

        // Clear existing timeout and set new one (5 seconds)
        if (undoTimeoutRef.current) {
          clearTimeout(undoTimeoutRef.current)
        }
        undoTimeoutRef.current = setTimeout(() => {
          setLastMove(null)
          undoTimeoutRef.current = null
        }, 5000)
      }

      // Optimistically update cards
      queryClient.setQueryData(['boards', boardId, 'cards'], (old: Card[] | undefined) => {
        if (!old) return old

        return old.map((c) =>
          c.id === cardId ? { ...c, column_id: columnId, position } : c
        )
      })

      return { previousCards }
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previousCards) {
        queryClient.setQueryData(['boards', boardId, 'cards'], context.previousCards)
      }
      // Clear undo state and timeout on error
      setLastMove(null)
      if (undoTimeoutRef.current) {
        clearTimeout(undoTimeoutRef.current)
        undoTimeoutRef.current = null
      }
      import('sonner').then(({ toast }) => {
        toast.error('Failed to move card. Changes reverted.')
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })

      // Show success with undo option
      import('sonner').then(({ toast }) => {
        toast.success('Card moved', {
          action: lastMove
            ? {
                label: 'Undo',
                onClick: handleUndo,
              }
            : undefined,
          duration: 5000,
        })
      })
    },
  })

  const bulkMoveCardsMutation = useMutation({
    mutationFn: ({ cardIds, columnId, position }: { cardIds: string[]; columnId: string; position: number }) =>
      api.patch<Card[]>('/api/cards/bulk-move', { card_ids: cardIds, column_id: columnId, position }),
    onMutate: async ({ cardIds, columnId, position }) => {
      await queryClient.cancelQueries({ queryKey: ['boards', boardId, 'cards'] })
      const previousCards = queryClient.getQueryData<Card[]>(['boards', boardId, 'cards'])

      // Optimistically update cards
      queryClient.setQueryData(['boards', boardId, 'cards'], (old: Card[] | undefined) => {
        if (!old) return old

        // Separate cards into moving and staying
        const movingCards = old.filter((c) => cardIds.includes(c.id))
        const stayingCards = old.filter((c) => !cardIds.includes(c.id))

        // Update moving cards with new column and position
        const updatedMovingCards = movingCards.map((c, index) => ({
          ...c,
          column_id: columnId,
          position: position + index,
        }))

        // Combine and sort by position within columns
        return [...stayingCards, ...updatedMovingCards]
      })

      return { previousCards }
    },
    onError: (err, variables, context) => {
      if (context?.previousCards) {
        queryClient.setQueryData(['boards', boardId, 'cards'], context.previousCards)
      }
      import('sonner').then(({ toast }) => {
        toast.error('Failed to move cards. Changes reverted.')
      })
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['boards', boardId, 'cards'] })
      clearSelection()
      import('sonner').then(({ toast }) => {
        toast.success(`${variables.cardIds.length} cards moved successfully`)
      })
    },
  })

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event

    // Haptic feedback on drag start (mobile devices)
    if ('vibrate' in navigator) {
      try {
        navigator.vibrate(50) // 50ms haptic pulse
      } catch (e) {
        // Silently fail if vibration not supported
      }
    }

    // Check if dragging a card
    if (typeof active.id === 'string' && active.id.includes('card-')) {
      const cardId = active.id.replace('card-', '')
      const card = cards.find((c) => c.id === cardId)

      // Debug logging
      console.log('🔍 Drag Start:', {
        cardId,
        isSelected: selectedCards.has(cardId),
        selectionSize: selectedCards.size,
        selectedCards: Array.from(selectedCards),
      })

      // If dragging a selected card and there are multiple selections,
      // we're doing a bulk drag operation
      if (card && selectedCards.has(cardId) && selectedCards.size > 1) {
        // Store all selected cards for bulk drag preview
        setActiveCard(card) // Primary card being dragged
        console.log('✅ Bulk drag mode activated')
      } else {
        setActiveCard(card || null)
        console.log('✅ Single card drag mode')
      }
    } else {
      // Dragging a column
      setActiveColumn(active.id as string)
    }
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    setActiveCard(null)
    setActiveColumn(null)

    // Haptic feedback on drop (mobile devices)
    if (over && 'vibrate' in navigator) {
      try {
        navigator.vibrate(25) // 25ms lighter pulse on drop
      } catch (e) {
        // Silently fail if vibration not supported
      }
    }

    if (!over || active.id === over.id || !board) return

    // Check if dragging a card
    if (typeof active.id === 'string' && active.id.includes('card-')) {
      const cardId = active.id.replace('card-', '')
      const card = cards.find((c) => c.id === cardId)
      if (!card) return

      // Determine target column and position
      let targetColumnId: string
      let targetPosition: number

      // Check if dropped over a column
      const overColumnId = over.id as string
      if (board.columns.some((col) => col.id === overColumnId)) {
        // Dropped over empty column space
        targetColumnId = overColumnId
        const cardsInTargetColumn = cards.filter((c) => c.column_id === targetColumnId)
        targetPosition = cardsInTargetColumn.length
      } else if (typeof over.id === 'string' && over.id.includes('card-')) {
        // Dropped over another card
        const overCardId = over.id.replace('card-', '')
        const overCard = cards.find((c) => c.id === overCardId)
        if (!overCard) return

        targetColumnId = overCard.column_id
        targetPosition = overCard.position
      } else {
        return
      }

      // Check if this is a bulk move operation
      if (selectedCards.has(cardId) && selectedCards.size > 1) {
        // Bulk move: drag all selected cards
        const cardIds = Array.from(selectedCards)
        console.log('🚀 Bulk move mutation:', { cardIds, targetColumnId, targetPosition })
        bulkMoveCardsMutation.mutate({
          cardIds,
          columnId: targetColumnId,
          position: targetPosition,
        })
      } else {
        // Single card move
        console.log('🚀 Single move mutation:', { cardId, targetColumnId, targetPosition })
        moveCardMutation.mutate({
          cardId,
          columnId: targetColumnId,
          position: targetPosition,
        })
      }
    } else {
      // Dragging a column
      const oldIndex = board.columns.findIndex((col) => col.id === active.id)
      const newIndex = board.columns.findIndex((col) => col.id === over.id)

      if (oldIndex === -1 || newIndex === -1) return

      const reorderedColumns = arrayMove(board.columns, oldIndex, newIndex).map((col, index) => ({
        ...col,
        position: index,
      }))

      updateBoardMutation.mutate({ columns: reorderedColumns })
    }
  }

  const handleAddColumn = () => {
    if (!board) return
    const newColumn = {
      id: uuidv4(),
      name: 'New Column',
      position: board.columns.length,
    }
    updateBoardMutation.mutate({ columns: [...board.columns, newColumn] })
  }

  const handleRenameColumn = (columnId: string, newName: string) => {
    if (!board) return
    const updatedColumns = board.columns.map((col) =>
      col.id === columnId ? { ...col, name: newName } : col
    )
    updateBoardMutation.mutate({ columns: updatedColumns })
  }

  const handleDeleteColumn = (
    columnId: string,
    action: 'delete-cards' | 'move-cards',
    targetColumnId?: string
  ) => {
    if (!board) return

    // TODO: When cards are implemented in Story 2.4, handle card migration here
    // if (action === 'move-cards' && targetColumnId) {
    //   1. Fetch all cards in the column being deleted
    //   2. Update their column_id to targetColumnId
    //   3. Recalculate positions in target column
    //   4. Save card updates via API
    // }
    // Note: For now (Story 2.3), we only delete the column structure
    // Card migration logic will be added in Story 2.4 when card CRUD is implemented

    const updatedColumns = board.columns.filter((col) => col.id !== columnId)
    updateBoardMutation.mutate({ columns: updatedColumns })
  }

  const handleRenamBoard = (newName: string) => {
    if (!newName.trim()) return
    updateBoardMutation.mutate({ name: newName.trim() })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">Loading board...</p>
      </div>
    )
  }

  if (!board) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-destructive">Board not found</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Archived Board Banner */}
      {board?.archived && (
        <div className="bg-yellow-50 dark:bg-yellow-950 border-b border-yellow-200 dark:border-yellow-800 px-4 py-2">
          <p className="text-sm text-yellow-800 dark:text-yellow-200 font-medium">
            📦 This board is archived and read-only. Cards cannot be moved or edited.
          </p>
        </div>
      )}

      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-4">
          {/* Selection Indicator */}
          {hasSelection && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-md">
              <span className="text-sm font-medium">{selectionCount()} selected</span>

              {/* Bulk Move Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-7 gap-1">
                    <MoveRight className="h-4 w-4" />
                    Move to
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                  {board.columns.map((column) => (
                    <DropdownMenuItem
                      key={column.id}
                      onClick={() => {
                        const cardIds = Array.from(selectedCards)
                        bulkMoveCardsMutation.mutate({
                          cardIds,
                          columnId: column.id,
                          position: 0, // Insert at the beginning of the column
                        })
                      }}
                    >
                      {column.name}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>

              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={clearSelection}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}

          {editingName ? (
            <input
              type="text"
              defaultValue={board.name}
              className="text-2xl font-bold border-none outline-none bg-transparent"
              onBlur={(e) => {
                const newName = e.target.value.trim()
                if (newName && newName !== board.name) {
                  handleRenamBoard(newName)
                }
                setEditingName(false)
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const newName = e.currentTarget.value.trim()
                  if (newName && newName !== board.name) {
                    handleRenamBoard(newName)
                  }
                  setEditingName(false)
                }
                if (e.key === 'Escape') {
                  setEditingName(false)
                }
              }}
            />
          ) : (
            <button
              type="button"
              className="text-2xl font-bold cursor-pointer hover:text-muted-foreground bg-transparent border-none p-0"
              onClick={() => setEditingName(true)}
            >
              {board.name}
            </button>
          )}
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/workspaces/${workspaceId}/boards/${boardId}/settings`}>
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Link>
          </Button>
        </div>

        {/* Filter Bar */}
        <FilterBar
          workspaceMembers={workspaceMembers}
          workspaceLabels={workspaceLabels}
          selectedAssignees={selectedAssignees}
          selectedLabels={selectedLabels}
          selectedPriorities={selectedPriorities}
          onAssigneeChange={setSelectedAssignees}
          onLabelChange={setSelectedLabels}
          onPriorityChange={setSelectedPriorities}
          onClearFilters={clearFilters}
        />
      </div>

      {/* Board Content */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden p-4">
        <DndContext
          sensors={isDragEnabled ? sensors : []}
          collisionDetection={closestCorners}
          onDragStart={isDragEnabled ? handleDragStart : undefined}
          onDragEnd={isDragEnabled ? handleDragEnd : undefined}
        >
          <div className="flex gap-4 h-full">
            <SortableContext
              items={board.columns.map((col) => col.id)}
              strategy={horizontalListSortingStrategy}
            >
              {/* Columns */}
              {board.columns.map((column) => (
                <BoardColumn
                  key={column.id}
                  column={column}
                  cards={filteredCards.filter((card) => card.column_id === column.id)}
                  boardId={boardId}
                  workspaceId={workspaceId}
                  otherColumns={board.columns.filter((col) => col.id !== column.id)}
                  onRename={handleRenameColumn}
                  onDelete={handleDeleteColumn}
                  isArchived={board.archived}
                />
              ))}
            </SortableContext>

            {/* Add Column Button */}
            <Button
              variant="ghost"
              className="flex-shrink-0 w-80 h-fit justify-start"
              onClick={handleAddColumn}
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Column
            </Button>
          </div>

          {/* Drag Overlay */}
          <DragOverlay>
            {activeCard ? (
              <div className="rotate-3 opacity-80">
                {selectedCards.size > 1 && selectedCards.has(activeCard.id) ? (
                  // Bulk drag preview: stacked cards with count badge
                  <div className="relative">
                    {/* Stacked card effect */}
                    <div className="absolute top-1 left-1 rounded-lg border bg-card shadow-sm w-full h-full opacity-40" />
                    <div className="absolute top-0.5 left-0.5 rounded-lg border bg-card shadow-sm w-full h-full opacity-60" />

                    {/* Primary card */}
                    <div className="relative">
                      <BoardCardComponent card={activeCard} onClick={() => {}} />
                      {/* Count badge */}
                      <div className="absolute -top-2 -right-2 bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold shadow-lg">
                        {selectedCards.size}
                      </div>
                    </div>
                  </div>
                ) : (
                  // Single card drag preview
                  <BoardCardComponent card={activeCard} onClick={() => {}} />
                )}
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      </div>
    </div>
  )
}
