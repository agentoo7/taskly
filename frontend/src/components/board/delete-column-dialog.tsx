/**
 * Delete column dialog with card migration options.
 * Implements AC 10: "Move cards to another column" or "Delete cards"
 */

'use client'

import { useState } from 'react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'

interface Column {
  id: string
  name: string
  position: number
}

interface DeleteColumnDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  column: Column
  cardCount: number
  otherColumns: Column[]
  onConfirmDelete: (action: 'delete-cards' | 'move-cards', targetColumnId?: string) => void
}

export function DeleteColumnDialog({
  open,
  onOpenChange,
  column,
  cardCount,
  otherColumns,
  onConfirmDelete,
}: DeleteColumnDialogProps) {
  const [deleteAction, setDeleteAction] = useState<'delete-cards' | 'move-cards'>(
    otherColumns.length > 0 ? 'move-cards' : 'delete-cards'
  )
  const [targetColumnId, setTargetColumnId] = useState<string>(
    otherColumns.length > 0 ? otherColumns[0].id : ''
  )

  const handleConfirm = () => {
    if (deleteAction === 'move-cards' && !targetColumnId) {
      // Validation: Must select a target column
      return
    }
    onConfirmDelete(deleteAction, deleteAction === 'move-cards' ? targetColumnId : undefined)
    onOpenChange(false)
  }

  // If no cards, simple delete confirmation
  if (cardCount === 0) {
    return (
      <AlertDialog open={open} onOpenChange={onOpenChange}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Column?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &quot;{column.name}&quot;? This action cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                onConfirmDelete('delete-cards')
                onOpenChange(false)
              }}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete Column
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    )
  }

  // If column has cards, show migration options
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="sm:max-w-[500px]">
        <AlertDialogHeader>
          <AlertDialogTitle>Delete Column and {cardCount} Cards?</AlertDialogTitle>
          <AlertDialogDescription>
            &quot;{column.name}&quot; contains {cardCount} {cardCount === 1 ? 'card' : 'cards'}.
            What would you like to do with {cardCount === 1 ? 'it' : 'them'}?
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="py-4">
          <RadioGroup value={deleteAction} onValueChange={(value) => setDeleteAction(value as any)}>
            {/* Option 1: Move cards to another column */}
            {otherColumns.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <RadioGroupItem value="move-cards" id="move-cards" className="mt-1" />
                  <div className="flex-1 space-y-2">
                    <Label htmlFor="move-cards" className="cursor-pointer font-medium">
                      Move cards to another column
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      All cards will be moved to the selected column before deleting this column.
                    </p>

                    {deleteAction === 'move-cards' && (
                      <div className="mt-3">
                        <Label htmlFor="target-column" className="text-sm">
                          Target Column
                        </Label>
                        <Select value={targetColumnId} onValueChange={setTargetColumnId}>
                          <SelectTrigger id="target-column" className="mt-1">
                            <SelectValue placeholder="Select a column" />
                          </SelectTrigger>
                          <SelectContent>
                            {otherColumns.map((col) => (
                              <SelectItem key={col.id} value={col.id}>
                                {col.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Option 2: Delete all cards */}
            <div className="flex items-start space-x-3 mt-4">
              <RadioGroupItem value="delete-cards" id="delete-cards" className="mt-1" />
              <div className="flex-1">
                <Label htmlFor="delete-cards" className="cursor-pointer font-medium text-destructive">
                  Delete all cards permanently
                </Label>
                <p className="text-sm text-muted-foreground mt-1">
                  All {cardCount} {cardCount === 1 ? 'card' : 'cards'} will be permanently deleted.
                  This action cannot be undone.
                </p>
              </div>
            </div>
          </RadioGroup>
        </div>

        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            disabled={deleteAction === 'move-cards' && !targetColumnId}
          >
            {deleteAction === 'move-cards'
              ? `Move ${cardCount} ${cardCount === 1 ? 'Card' : 'Cards'} & Delete Column`
              : `Delete Column & ${cardCount} ${cardCount === 1 ? 'Card' : 'Cards'}`}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
