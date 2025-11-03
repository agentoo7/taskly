/**
 * Board view page displaying columns and cards.
 */

'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import { api } from '@/lib/api/client'
import { BoardColumn } from '@/components/board/board-column'
import { Button } from '@/components/ui/button'
import { Plus, Settings } from 'lucide-react'
import { useState } from 'react'
import Link from 'next/link'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  horizontalListSortingStrategy,
} from '@dnd-kit/sortable'
import { v4 as uuidv4 } from 'uuid'

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
  const queryClient = useQueryClient()
  const [editingName, setEditingName] = useState(false)

  const { data: board, isLoading } = useQuery({
    queryKey: ['boards', boardId],
    queryFn: () => api.get<Board>(`/api/boards/${boardId}`),
  })

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

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

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id || !board) return

    const oldIndex = board.columns.findIndex((col) => col.id === active.id)
    const newIndex = board.columns.findIndex((col) => col.id === over.id)

    const reorderedColumns = arrayMove(board.columns, oldIndex, newIndex).map((col, index) => ({
      ...col,
      position: index,
    }))

    updateBoardMutation.mutate({ columns: reorderedColumns })
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
      {/* Header */}
      <div className="border-b p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
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

      {/* Board Content */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden p-4">
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
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
                  cardCount={0} // TODO: Update with actual card count when cards implemented in Story 2.4
                  otherColumns={board.columns.filter((col) => col.id !== column.id)}
                  onRename={handleRenameColumn}
                  onDelete={handleDeleteColumn}
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
        </DndContext>
      </div>
    </div>
  )
}
