# Multi-Select Card Drag & Drop - Testing Guide

**Date:** 2025-11-03
**Issue:** Cannot drag multiple selected cards simultaneously
**Status:** ✅ Fixed with debug logging

---

## Changes Made

### 1. Fixed BoardCard Component
**File:** `frontend/src/components/board/board-card.tsx`

**Changes:**
- Added `disabled: isArchived` to `useSortable` hook
- Added `handleCardClick` to prevent modal opening during drag
- Prevents click handler interference with drag operation

```typescript
const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
  id: `card-${card.id}`,
  disabled: isArchived, // Disable sorting for archived boards
})

const handleCardClick = (e: React.MouseEvent) => {
  // Don't open modal if clicking during drag
  if (isDragging) return
  onClick()
}
```

### 2. Added Debug Logging
**File:** `frontend/src/app/(dashboard)/workspaces/[workspaceId]/boards/[boardId]/page.tsx`

**Added console logs to track:**
- Drag start events
- Selection state
- Bulk vs single drag mode
- Mutation calls

---

## How to Test Multi-Select Drag

### Step 1: Open Application
1. Navigate to http://localhost:3000
2. Login and open a board with multiple cards

### Step 2: Select Multiple Cards
1. Hover over a card - checkbox appears in top-right corner
2. Click checkbox to select the card (card gets blue ring)
3. Select 2-3 more cards
4. Cards should all have blue ring and "X selected" indicator appears in header

### Step 3: Drag Selected Cards
1. **Click and hold** on any selected card
2. Start dragging (should see stacked preview with count badge)
3. Drag to target column
4. Release mouse

### Step 4: Check Browser Console
Open browser DevTools (F12) and check console for:

```
🔍 Drag Start: {
  cardId: "...",
  isSelected: true,
  selectionSize: 3,
  selectedCards: ["card1-id", "card2-id", "card3-id"]
}
✅ Bulk drag mode activated
```

When dropping:
```
🚀 Bulk move mutation: {
  cardIds: ["card1-id", "card2-id", "card3-id"],
  targetColumnId: "column-id",
  targetPosition: 0
}
```

---

## Expected Behavior

### ✅ Working Correctly:
- Can select multiple cards via checkbox
- Selection persists during drag
- Drag shows stacked preview with count badge
- All selected cards move together to target column
- Cards maintain their relative order

### ❌ If Not Working:
- Check console logs - is `isSelected: false`?
- Check if `selectionSize` is correct
- Verify `bulkMoveCardsMutation` is called (not `moveCardMutation`)

---

## Common Issues & Solutions

### Issue 1: Selection Clears When Dragging
**Symptom:** Cards deselect when you start dragging
**Debug:** Check console - `isSelected: false` even though you selected cards
**Solution:** Selection state not persisting - check Zustand store

### Issue 2: Single Card Moves Instead of Bulk
**Symptom:** Only the dragged card moves, not all selected
**Debug:** Console shows `✅ Single card drag mode` instead of bulk
**Possible causes:**
- `selectedCards.has(cardId)` returns false
- `selectedCards.size <= 1`
**Solution:** Verify selection store is tracking cards correctly

### Issue 3: Drag Preview Shows Single Card
**Symptom:** No stacked preview with count badge
**Debug:** Check `DragOverlay` rendering logic
**Solution:** Verify `selectedCards.size > 1` condition

### Issue 4: Cards Move But API Fails
**Symptom:** Console shows mutation call but backend errors
**Debug:** Check network tab for API response
**Possible causes:**
- Backend `bulkMoveCardsMutation` not defined
- API endpoint returns 500 error
**Solution:** Check backend logs

---

## Debug Commands

### Check Selection Store State
```javascript
// In browser console
window.__REACT_DEVTOOLS_GLOBAL_HOOK__.renderers.forEach(renderer => {
  const fiber = renderer.getFiberRoots().values().next().value
  // Navigate to CardSelectionStore
})
```

### Monitor Network Requests
```bash
# In DevTools Network tab, filter for:
POST /api/cards/bulk-move
```

### Check Backend Logs
```bash
docker-compose logs -f backend | grep "bulk"
```

---

## Technical Details

### Selection Flow:
1. User clicks checkbox → `useCardSelectionStore.toggleCard(cardId)`
2. Store adds/removes card from `Set<string>`
3. Card component re-renders with `selected={isSelected(card.id)}`
4. Card shows blue ring if selected

### Drag Flow (Multi-Select):
1. User starts drag on selected card
2. `handleDragStart` checks if `selectedCards.has(cardId) && size > 1`
3. If true, activates bulk mode
4. `DragOverlay` shows stacked preview
5. `handleDragEnd` calls `bulkMoveCardsMutation` with all card IDs

### Bulk Move API:
```typescript
bulkMoveCardsMutation.mutate({
  cardIds: ["uuid1", "uuid2", "uuid3"],
  columnId: "target-column-uuid",
  position: 0
})
```

Backend should:
- Move all cards to target column
- Set positions sequentially (0, 1, 2, ...)
- Broadcast WebSocket events
- Log activity for each card

---

## Next Steps

1. **Test in browser** with the steps above
2. **Check console logs** - do you see bulk mode activated?
3. **Verify API calls** - is `bulkMoveCardsMutation` being called?
4. **Report results** - does multi-select drag work now?

If still not working, provide:
- Screenshot of console logs
- Screenshot of Network tab (API requests)
- Description of exact steps taken

---

**Expected Result:** All selected cards should move together to the target column with a single drag operation.

**Application URL:** http://localhost:3000
**Backend Logs:** `docker-compose logs -f backend`
