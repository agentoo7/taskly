/**
 * Label type definitions
 */

export interface Label {
  id: string
  workspace_id: string
  name: string
  color: string // Hex color code
  created_at: string
}

export interface LabelCreate {
  name: string
  color: string
}

export interface LabelUpdate {
  name?: string
  color?: string
}
