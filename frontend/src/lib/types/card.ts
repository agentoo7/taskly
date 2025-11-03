/**
 * Card type definitions matching backend Pydantic schemas
 */

import { User } from './user'
import { Label } from './label'

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
  assignees: User[]
  labels: Label[]
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
