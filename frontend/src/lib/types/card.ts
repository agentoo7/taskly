/**
 * Card type definitions matching backend Pydantic schemas
 */

export type Priority = 'none' | 'low' | 'medium' | 'high' | 'urgent'

export interface Card {
  id: string
  board_id: string
  column_id: string
  title: string
  description: string | null
  priority: Priority
  due_date: string | null // ISO date string
  story_points: number | null
  position: number
  created_by: string | null
  created_at: string // ISO datetime string
  updated_at: string // ISO datetime string
}

export interface CardCreate {
  title: string
  column_id: string
  board_id: string
}

export interface CardUpdate {
  title?: string
  description?: string | null
  priority?: Priority
  due_date?: string | null // ISO date string
  story_points?: number | null
}
