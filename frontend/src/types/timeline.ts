/**
 * TypeScript types for timeline (comments + activities)
 */

export interface User {
  id: string
  username: string
  email?: string
  avatar_url?: string | null
}

export interface TimelineComment {
  type: 'comment'
  id: string
  card_id: string
  author: User
  text: string
  created_at: string
  updated_at: string
}

export interface TimelineActivity {
  type: 'activity'
  id: string
  card_id: string
  user: User
  action: string
  description: string
  created_at: string
}

export type TimelineItem = TimelineComment | TimelineActivity

export interface TimelineResponse {
  items: TimelineItem[]
  total: number
  offset: number
  limit: number
}

export interface CommentCreateRequest {
  text: string
}

export interface CommentUpdateRequest {
  text: string
}
