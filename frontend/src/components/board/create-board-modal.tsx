/**
 * Modal for creating a new board with template selection.
 */

'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { api } from '@/lib/api/client'
import { LayoutGrid, Square } from 'lucide-react'

const schema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
  template: z.enum(['blank', 'kanban']),
})

type FormData = z.infer<typeof schema>

interface CreateBoardModalProps {
  workspaceId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface BoardResponse {
  id: string
  workspace_id: string
  name: string
  columns: Array<{ id: string; name: string; position: number }>
  archived: boolean
  created_at: string
  updated_at: string
}

const TEMPLATES = [
  {
    id: 'blank',
    name: 'Blank Board',
    description: 'Start with an empty board',
    icon: Square,
    preview: 'No columns',
  },
  {
    id: 'kanban',
    name: 'Default Kanban',
    description: 'Pre-configured workflow',
    icon: LayoutGrid,
    preview: 'To Do → In Progress → In Review → Done',
  },
] as const

export function CreateBoardModal({ workspaceId, open, onOpenChange }: CreateBoardModalProps) {
  const router = useRouter()
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
    setValue,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      template: 'blank',
    },
  })

  const selectedTemplate = watch('template')

  const createMutation = useMutation({
    mutationFn: (data: FormData) =>
      api.post<BoardResponse>(`/api/workspaces/${workspaceId}/boards`, data),
    onSuccess: (board) => {
      queryClient.invalidateQueries({ queryKey: ['workspaces', workspaceId, 'boards'] })
      onOpenChange(false)
      reset()
      router.push(`/workspaces/${workspaceId}/boards/${board.id}`)
    },
    onError: (error) => {
      console.error('Failed to create board:', error)
    },
  })

  const onSubmit = (data: FormData) => {
    createMutation.mutate(data)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create Board</DialogTitle>
          <DialogDescription>
            Create a new board to organize your tasks and track progress.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="grid gap-6 py-4">
            {/* Board Name */}
            <div className="grid gap-2">
              <Label htmlFor="name">Board Name</Label>
              <Input id="name" placeholder="Sprint Board" {...register('name')} />
              {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
            </div>

            {/* Template Selection */}
            <div className="grid gap-3">
              <Label>Template</Label>
              <RadioGroup
                value={selectedTemplate}
                onValueChange={(value) => setValue('template', value as 'blank' | 'kanban')}
              >
                {TEMPLATES.map((template) => (
                  <label
                    key={template.id}
                    htmlFor={template.id}
                    className={`flex items-start space-x-3 rounded-lg border p-4 cursor-pointer hover:bg-accent transition-colors ${
                      selectedTemplate === template.id ? 'border-primary bg-accent' : ''
                    }`}
                  >
                    <RadioGroupItem value={template.id} id={template.id} className="mt-1" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <template.icon className="h-4 w-4" />
                        <span className="font-semibold cursor-pointer">
                          {template.name}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">{template.description}</p>
                      <p className="text-xs text-muted-foreground mt-2 font-mono">
                        {template.preview}
                      </p>
                    </div>
                  </label>
                ))}
              </RadioGroup>
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={createMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Board'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
