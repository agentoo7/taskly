/**
 * Unit tests for card selection store (Story 2.5 - Task 11)
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useCardSelectionStore } from '@/store/card-selection-store'

describe('CardSelectionStore', () => {
  beforeEach(() => {
    // Clear selection before each test
    const { clearSelection } = useCardSelectionStore.getState()
    clearSelection()
  })

  it('initializes with empty selection', () => {
    const { selectedCards, selectionCount } = useCardSelectionStore.getState()

    expect(selectedCards.size).toBe(0)
    expect(selectionCount()).toBe(0)
  })

  it('selects a card', () => {
    const { selectCard, isSelected, selectionCount } = useCardSelectionStore.getState()

    selectCard('card-1')

    expect(isSelected('card-1')).toBe(true)
    expect(selectionCount()).toBe(1)
  })

  it('deselects a card', () => {
    const { selectCard, deselectCard, isSelected, selectionCount } = useCardSelectionStore.getState()

    selectCard('card-1')
    expect(isSelected('card-1')).toBe(true)

    deselectCard('card-1')
    expect(isSelected('card-1')).toBe(false)
    expect(selectionCount()).toBe(0)
  })

  it('toggles card selection', () => {
    const { toggleCard, isSelected, selectionCount } = useCardSelectionStore.getState()

    // Toggle on
    toggleCard('card-1')
    expect(isSelected('card-1')).toBe(true)
    expect(selectionCount()).toBe(1)

    // Toggle off
    toggleCard('card-1')
    expect(isSelected('card-1')).toBe(false)
    expect(selectionCount()).toBe(0)
  })

  it('selects multiple cards', () => {
    const { selectCard, isSelected, selectionCount } = useCardSelectionStore.getState()

    selectCard('card-1')
    selectCard('card-2')
    selectCard('card-3')

    expect(isSelected('card-1')).toBe(true)
    expect(isSelected('card-2')).toBe(true)
    expect(isSelected('card-3')).toBe(true)
    expect(selectionCount()).toBe(3)
  })

  it('clears all selections', () => {
    const { selectCard, clearSelection, selectionCount, isSelected } = useCardSelectionStore.getState()

    // Select multiple cards
    selectCard('card-1')
    selectCard('card-2')
    selectCard('card-3')
    expect(selectionCount()).toBe(3)

    // Clear all
    clearSelection()
    expect(selectionCount()).toBe(0)
    expect(isSelected('card-1')).toBe(false)
    expect(isSelected('card-2')).toBe(false)
    expect(isSelected('card-3')).toBe(false)
  })

  it('handles selecting the same card twice', () => {
    const { selectCard, selectionCount } = useCardSelectionStore.getState()

    selectCard('card-1')
    selectCard('card-1') // Select again

    // Should still only count once
    expect(selectionCount()).toBe(1)
  })

  it('returns false for unselected cards', () => {
    const { isSelected } = useCardSelectionStore.getState()

    expect(isSelected('non-existent-card')).toBe(false)
  })

  it('handles deselecting a card that was never selected', () => {
    const { deselectCard, selectionCount } = useCardSelectionStore.getState()

    // Should not throw error
    deselectCard('non-existent-card')

    expect(selectionCount()).toBe(0)
  })

  it('persists selection state across multiple accesses', () => {
    const { selectCard } = useCardSelectionStore.getState()

    selectCard('card-1')
    selectCard('card-2')

    // Get fresh state reference
    const { isSelected, selectionCount } = useCardSelectionStore.getState()

    expect(isSelected('card-1')).toBe(true)
    expect(isSelected('card-2')).toBe(true)
    expect(selectionCount()).toBe(2)
  })

  it('correctly reports selection count with mixed operations', () => {
    const { selectCard, deselectCard, toggleCard, selectionCount } = useCardSelectionStore.getState()

    selectCard('card-1') // 1
    selectCard('card-2') // 2
    toggleCard('card-3') // 3
    deselectCard('card-1') // 2
    toggleCard('card-3') // 1 (toggle off)

    expect(selectionCount()).toBe(1)
  })
})
