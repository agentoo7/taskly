/**
 * Markdown editor component with Write/Preview tabs
 */

'use client'

import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Bold, Italic, Link as LinkIcon, List, Code } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/utils'

interface MarkdownEditorProps {
  value: string
  onChange: (value: string) => void
  onBlur?: () => void
  placeholder?: string
  disabled?: boolean
  autoSaveKey?: string // localStorage key for auto-recovery
}

export function MarkdownEditor({
  value,
  onChange,
  onBlur,
  placeholder = 'Add a description...',
  disabled,
  autoSaveKey,
}: MarkdownEditorProps) {
  const [activeTab, setActiveTab] = useState<'write' | 'preview'>('write')

  // Auto-save draft to localStorage
  useEffect(() => {
    if (autoSaveKey && value) {
      localStorage.setItem(autoSaveKey, value)
    }
  }, [value, autoSaveKey])

  // Auto-recover from localStorage on mount
  useEffect(() => {
    if (autoSaveKey && !value) {
      const saved = localStorage.getItem(autoSaveKey)
      if (saved) {
        onChange(saved)
      }
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const insertFormatting = (before: string, after: string = '') => {
    const textarea = document.activeElement as HTMLTextAreaElement
    if (textarea && textarea.tagName === 'TEXTAREA') {
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const selectedText = value.substring(start, end)
      const newValue =
        value.substring(0, start) +
        before +
        selectedText +
        after +
        value.substring(end)

      onChange(newValue)

      // Set cursor position after formatting
      setTimeout(() => {
        textarea.focus()
        textarea.setSelectionRange(
          start + before.length,
          start + before.length + selectedText.length
        )
      }, 0)
    }
  }

  const handleBold = () => insertFormatting('**', '**')
  const handleItalic = () => insertFormatting('*', '*')
  const handleLink = () => insertFormatting('[', '](url)')
  const handleList = () => {
    const lines = value.split('\n')
    const textarea = document.activeElement as HTMLTextAreaElement
    if (textarea) {
      const start = textarea.selectionStart
      const lineIndex = value.substring(0, start).split('\n').length - 1
      lines[lineIndex] = '- ' + lines[lineIndex]
      onChange(lines.join('\n'))
    }
  }
  const handleCode = () => insertFormatting('`', '`')

  return (
    <div className="border rounded-md">
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'write' | 'preview')}>
        <div className="border-b px-3 py-2 flex items-center justify-between">
          <TabsList className="h-8">
            <TabsTrigger value="write" className="text-xs">
              Write
            </TabsTrigger>
            <TabsTrigger value="preview" className="text-xs">
              Preview
            </TabsTrigger>
          </TabsList>

          {activeTab === 'write' && (
            <div className="flex items-center gap-1">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0"
                onClick={handleBold}
                disabled={disabled}
                title="Bold"
              >
                <Bold className="h-3.5 w-3.5" />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0"
                onClick={handleItalic}
                disabled={disabled}
                title="Italic"
              >
                <Italic className="h-3.5 w-3.5" />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0"
                onClick={handleLink}
                disabled={disabled}
                title="Link"
              >
                <LinkIcon className="h-3.5 w-3.5" />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0"
                onClick={handleList}
                disabled={disabled}
                title="List"
              >
                <List className="h-3.5 w-3.5" />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0"
                onClick={handleCode}
                disabled={disabled}
                title="Code"
              >
                <Code className="h-3.5 w-3.5" />
              </Button>
            </div>
          )}
        </div>

        <TabsContent value="write" className="m-0 p-3">
          <Textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onBlur={onBlur}
            placeholder={placeholder}
            disabled={disabled}
            className="min-h-[200px] border-none focus-visible:ring-0 resize-none"
          />
        </TabsContent>

        <TabsContent value="preview" className="m-0 p-4 min-h-[200px]">
          {value ? (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{value}</ReactMarkdown>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">No description</p>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
