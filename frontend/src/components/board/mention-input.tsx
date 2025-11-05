/**
 * Simplified mention input with basic @mention support
 * Note: Full implementation would use libraries like @tiptap/suggestion
 */

'use client'

import { useState, useRef, useEffect } from 'react'
import { Textarea } from '@/components/ui/textarea'

interface MentionInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  rows?: number
}

interface WorkspaceMember {
  id: string
  username: string
  avatar_url?: string | null
}

export function MentionInput({ value, onChange, placeholder, rows = 3 }: MentionInputProps) {
  const [showMentions, setShowMentions] = useState(false)
  const [mentionSearch, setMentionSearch] = useState('')
  const [mentionPosition, setMentionPosition] = useState(0)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Mock workspace members - in production, fetch from API
  const workspaceMembers: WorkspaceMember[] = [
    { id: '1', username: 'alice', avatar_url: null },
    { id: '2', username: 'bob', avatar_url: null },
    { id: '3', username: 'charlie', avatar_url: null },
  ]

  const filteredMembers = workspaceMembers.filter((member) =>
    member.username.toLowerCase().includes(mentionSearch.toLowerCase())
  )

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value
    onChange(newValue)

    // Check if user typed @
    const cursorPos = e.target.selectionStart
    const textBeforeCursor = newValue.slice(0, cursorPos)
    const lastAtSymbol = textBeforeCursor.lastIndexOf('@')

    if (lastAtSymbol !== -1) {
      const textAfterAt = textBeforeCursor.slice(lastAtSymbol + 1)
      // Only show mentions if @ is followed by word characters
      if (/^\w*$/.test(textAfterAt)) {
        setMentionSearch(textAfterAt)
        setMentionPosition(lastAtSymbol)
        setShowMentions(true)
        return
      }
    }

    setShowMentions(false)
  }

  const insertMention = (username: string) => {
    const beforeMention = value.slice(0, mentionPosition)
    const afterCursor = value.slice(textareaRef.current?.selectionStart || value.length)
    const newValue = `${beforeMention}@${username} ${afterCursor}`

    onChange(newValue)
    setShowMentions(false)
    setMentionSearch('')

    // Focus textarea
    textareaRef.current?.focus()
  }

  return (
    <div className="relative">
      <Textarea
        ref={textareaRef}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        rows={rows}
        className="resize-none"
      />

      {showMentions && filteredMembers.length > 0 && (
        <div className="absolute z-10 mt-1 w-48 rounded-md border bg-popover p-1 shadow-md">
          <div className="text-xs text-muted-foreground px-2 py-1">Mention someone</div>
          {filteredMembers.map((member) => (
            <button
              key={member.id}
              onClick={() => insertMention(member.username)}
              className="w-full text-left px-2 py-1.5 text-sm rounded hover:bg-accent transition-colors"
            >
              @{member.username}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
