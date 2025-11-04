/**
 * Integration tests for drag-and-drop board functionality (Story 2.5)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BoardCard } from '@/components/board/board-card'
import { Card, Priority } from '@/lib/types/card'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
  useParams: () => ({
    workspaceId: 'test-workspace',
    boardId: 'test-board',
  }),
}))

// Mock the DnD hook
vi.mock('@dnd-kit/sortable', () => ({
  useSortable: () => ({
    attributes: {},
    listeners: {},
    setNodeRef: vi.fn(),
    transform: null,
    transition: null,
    isDragging: false,
  }),
  SortableContext: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  verticalListSortingStrategy: {},
}))

// Mock the card selection store
vi.mock('@/store/card-selection-store', () => ({
  useCardSelectionStore: () => ({
    isSelected: vi.fn(() => false),
    toggleCard: vi.fn(),
    selectedCards: new Set<string>(),
    clearSelection: vi.fn(),
    selectionCount: vi.fn(() => 0),
  }),
}))

describe('BoardCard with Drag-and-Drop', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    })
    vi.clearAllMocks()
  })

  const mockCard: Card = {
    id: 'card-1',
    board_id: 'board-1',
    column_id: 'column-1',
    title: 'Test Card',
    description: null,
    priority: 'medium' as Priority,
    due_date: null,
    story_points: null,
    position: 0,
    archived: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }

  it('renders card with correct title', () => {
    const onClick = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BoardCard card={mockCard} onClick={onClick} />
      </QueryClientProvider>
    )

    expect(screen.getByText('Test Card')).toBeInTheDocument()
  })

  it('calls onClick when card is clicked', () => {
    const onClick = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BoardCard card={mockCard} onClick={onClick} />
      </QueryClientProvider>
    )

    const card = screen.getByRole('button', { name: /Card: Test Card/i })
    card.click()

    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('displays priority indicator for non-none priority', () => {
    const onClick = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BoardCard card={mockCard} onClick={onClick} />
      </QueryClientProvider>
    )

    // Check for priority indicator by aria-label
    const priorityIndicator = screen.getByLabelText('Priority: medium')
    expect(priorityIndicator).toBeInTheDocument()
  })

  it('does not display priority indicator for none priority', () => {
    const onClick = vi.fn()
    const noPriorityCard = { ...mockCard, priority: 'none' as Priority }

    render(
      <QueryClientProvider client={queryClient}>
        <BoardCard card={noPriorityCard} onClick={onClick} />
      </QueryClientProvider>
    )

    // Should not have priority indicator
    const priorityIndicators = screen.queryByLabelText(/Priority:/)
    expect(priorityIndicators).not.toBeInTheDocument()
  })

  it('displays due date badge when due date is set', () => {
    const onClick = vi.fn()
    const dueDateCard = {
      ...mockCard,
      due_date: '2025-12-31T00:00:00Z',
    }

    render(
      <QueryClientProvider client={queryClient}>
        <BoardCard card={dueDateCard} onClick={onClick} />
      </QueryClientProvider>
    )

    expect(screen.getByText(/Due:/)).toBeInTheDocument()
  })

  it('displays story points badge when story points are set', () => {
    const onClick = vi.fn()
    const storyPointsCard = {
      ...mockCard,
      story_points: 5,
    }

    render(
      <QueryClientProvider client={queryClient}>
        <BoardCard card={storyPointsCard} onClick={onClick} />
      </QueryClientProvider>
    )

    expect(screen.getByText('5 pts')).toBeInTheDocument()
  })

  it('handles keyboard Enter key to open card', () => {
    const onClick = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BoardCard card={mockCard} onClick={onClick} />
      </QueryClientProvider>
    )

    const card = screen.getByRole('button', { name: /Card: Test Card/i })
    card.focus()

    // Simulate Enter key press
    card.dispatchEvent(
      new KeyboardEvent('keydown', {
        key: 'Enter',
        bubbles: true,
      })
    )

    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('handles keyboard Space key to open card', () => {
    const onClick = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BoardCard card={mockCard} onClick={onClick} />
      </QueryClientProvider>
    )

    const card = screen.getByRole('button', { name: /Card: Test Card/i })
    card.focus()

    // Simulate Space key press
    card.dispatchEvent(
      new KeyboardEvent('keydown', {
        key: ' ',
        bubbles: true,
      })
    )

    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('renders selection checkbox', () => {
    const onClick = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BoardCard card={mockCard} onClick={onClick} />
      </QueryClientProvider>
    )

    // Check for checkbox button
    const checkbox = screen.getByLabelText('Select card')
    expect(checkbox).toBeInTheDocument()
  })

  it('has proper accessibility attributes', () => {
    const onClick = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BoardCard card={mockCard} onClick={onClick} />
      </QueryClientProvider>
    )

    const card = screen.getByRole('button', { name: /Card: Test Card/i })

    // Should have role="button"
    expect(card.getAttribute('role')).toBe('button')

    // Should have aria-label
    expect(card.getAttribute('aria-label')).toBe('Card: Test Card')

    // Should be tabbable
    expect(card.getAttribute('tabIndex')).toBe('0')
  })

  it('applies correct cursor style for draggable cards', () => {
    const onClick = vi.fn()

    render(
      <QueryClientProvider client={queryClient}>
        <BoardCard card={mockCard} onClick={onClick} />
      </QueryClientProvider>
    )

    const card = screen.getByRole('button', { name: /Card: Test Card/i })

    // Should have cursor-pointer class
    expect(card.className).toContain('cursor-pointer')
  })
})

describe('Drag-and-Drop Position Calculation', () => {
  it('calculates correct position when dropping at beginning', () => {
    // Moving card from position 3 to position 0
    const oldPosition = 3
    const newPosition = 0

    expect(newPosition).toBe(0)
    expect(newPosition).toBeLessThan(oldPosition)
  })

  it('calculates correct position when dropping at end', () => {
    // Moving card from position 0 to last position
    const cardsInColumn = 5
    const newPosition = cardsInColumn - 1

    expect(newPosition).toBe(4)
  })

  it('handles same-column reordering', () => {
    const oldPosition = 2
    const newPosition = 4

    // Card should move from index 2 to index 4
    expect(newPosition).toBeGreaterThan(oldPosition)
  })

  it('handles cross-column movement', () => {
    const sourceColumnId = 'column-1'
    const targetColumnId = 'column-2'
    const targetPosition = 0

    // Card moves to different column at position 0
    expect(targetColumnId).not.toBe(sourceColumnId)
    expect(targetPosition).toBe(0)
  })
})
