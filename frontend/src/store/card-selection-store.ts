/**
 * Zustand store for managing card selection state (bulk operations).
 */

import { create } from 'zustand'

interface CardSelectionState {
  selectedCards: Set<string>
  toggleCard: (cardId: string) => void
  selectCard: (cardId: string) => void
  deselectCard: (cardId: string) => void
  clearSelection: () => void
  isSelected: (cardId: string) => boolean
  selectionCount: () => number
}

export const useCardSelectionStore = create<CardSelectionState>((set, get) => ({
  selectedCards: new Set<string>(),

  toggleCard: (cardId: string) => {
    set((state) => {
      const newSelection = new Set(state.selectedCards)
      if (newSelection.has(cardId)) {
        newSelection.delete(cardId)
      } else {
        newSelection.add(cardId)
      }
      return { selectedCards: newSelection }
    })
  },

  selectCard: (cardId: string) => {
    set((state) => {
      const newSelection = new Set(state.selectedCards)
      newSelection.add(cardId)
      return { selectedCards: newSelection }
    })
  },

  deselectCard: (cardId: string) => {
    set((state) => {
      const newSelection = new Set(state.selectedCards)
      newSelection.delete(cardId)
      return { selectedCards: newSelection }
    })
  },

  clearSelection: () => {
    set({ selectedCards: new Set<string>() })
  },

  isSelected: (cardId: string) => {
    return get().selectedCards.has(cardId)
  },

  selectionCount: () => {
    return get().selectedCards.size
  },
}))
