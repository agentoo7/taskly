# Taskly Frontend Architecture Document

## Template and Framework Selection

### Starter Template Decision

**Selected Approach:** `create-next-app` (Official Next.js Starter)

**Command:**
```bash
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir --import-alias "@/*"
```

**Setup Steps:**
1. Run `create-next-app` with TypeScript and Tailwind flags
2. Initialize shadcn/ui: `npx shadcn-ui@latest init`
3. Install additional dependencies: Zustand, TanStack Query, @dnd-kit, React Hook Form, Zod
4. Configure monorepo: Add `frontend/` to root `package.json` workspaces

**Rationale:**
- Official Next.js tooling ensures compatibility with App Router features
- TypeScript and Tailwind pre-configured (no manual webpack setup)
- shadcn/ui installation is straightforward (one command)
- Aligns with PRD's "keep it simple for MVP" philosophy
- Supports all required features: SSR, Server Components, streaming, file-based routing

**Post-Setup:**
- Install dependencies: `npm install zustand @tanstack/react-query @tanstack/react-query-devtools @dnd-kit/core @dnd-kit/sortable react-hook-form zod framer-motion lucide-react date-fns`
- Configure shadcn/ui components: `npx shadcn-ui@latest add button card dialog dropdown-menu input`

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-23 | 1.0 | Initial frontend architecture | Winston (Architect Agent) |

---

## Frontend Tech Stack

**⚠️ CRITICAL:** This section MUST remain synchronized with the main backend architecture document.

### Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| **Language** | TypeScript | 5.3.3 | Type-safe development | Catch errors at compile time, better IDE support, mandatory type safety |
| **Runtime** | Node.js | 20.11.0 LTS | JavaScript runtime | Long-term support, stable, Next.js requirement |
| **Framework** | Next.js | 14.1.0 | React framework with SSR | App Router, Server Components, optimized performance, SEO-friendly |
| **UI Library** | React | 18.2.0 | Component-based UI | Industry standard, concurrent features, Server Components support |
| **CSS Framework** | Tailwind CSS | 3.4.1 | Utility-first styling | Rapid UI development, consistent design system, tree-shaking |
| **Component Library** | shadcn/ui | latest | Accessible UI components | Built on Radix UI, customizable, copy-paste (not npm dependency), accessible by default |
| **State Management** | Zustand | 4.5.0 | Client state (UI state, preferences) | Lightweight (3KB), simple API, no boilerplate, TypeScript-first |
| **Server State** | TanStack Query | 5.17.19 | API data caching & sync | Request deduplication, automatic cache invalidation, optimistic updates, background refetching |
| **Drag & Drop** | @dnd-kit | 6.1.0 | Accessible drag-and-drop | Accessible, performant, tree-shaking, keyboard navigation support |
| **Form Handling** | React Hook Form | 7.49.3 | Form validation & state | Minimal re-renders, built-in validation, TypeScript support, integrates with Zod |
| **Schema Validation** | Zod | 3.22.4 | Runtime type validation | Type-safe schemas, API response validation, form validation |
| **HTTP Client** | Fetch API (native) | - | HTTP requests | Built-in, Server Actions support, no additional dependency |
| **Routing** | Next.js App Router | 14.1.0 (built-in) | File-based routing | Server Components, streaming, layouts, loading states |
| **Build Tool** | Turbopack (Next.js) | 14.1.0 (built-in) | Fast bundling | Rust-based, faster than Webpack, incremental compilation |
| **Package Manager** | npm | 10.2.5 | Dependency management | Workspaces support (monorepo), lockfile for consistency |
| **Linter** | ESLint | 8.56.0 | Code quality | Next.js config, TypeScript rules, accessibility checks |
| **Formatter** | Prettier | 3.2.4 | Code formatting | Consistent style, integrates with ESLint, Tailwind plugin |
| **Testing Framework** | Vitest | 1.2.0 | Unit & integration tests | Fast, Vite-powered, Jest-compatible API, native ESM support |
| **Component Testing** | React Testing Library | 14.1.2 | Component tests | User-centric testing, accessibility-focused, best practices |
| **E2E Testing** | Playwright | 1.40.0 | End-to-end tests | Cross-browser, fast, reliable, parallel execution |
| **Animation** | Framer Motion | 11.0.3 | UI animations | Declarative animations, gesture support, layout animations |
| **Icons** | Lucide React | 0.309.0 | Icon library | Tree-shakeable, consistent style, extensive collection |
| **Date Handling** | date-fns | 3.2.0 | Date manipulation | Functional, tree-shakeable, i18n support |
| **Real-time** | WebSocket API (native) | - | Real-time updates | Native browser API, no additional library needed |
| **Dev Tools** | React DevTools | latest | Component inspection | Debug React component tree, props, state |
| **Dev Tools** | TanStack Query DevTools | 5.17.19 | Query state inspection | Debug cache, refetch status, query keys |

---

## Project Structure

```
frontend/
├── public/                              # Static assets
│   ├── favicon.ico
│   ├── logo.svg
│   └── robots.txt
│
├── src/
│   ├── app/                            # Next.js App Router
│   │   ├── (auth)/                     # Route group (public auth pages)
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── callback/
│   │   │       └── page.tsx
│   │   │
│   │   ├── (dashboard)/                # Route group (authenticated pages)
│   │   │   ├── layout.tsx
│   │   │   ├── workspaces/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [workspaceId]/
│   │   │   │       ├── page.tsx
│   │   │   │       └── boards/
│   │   │   │           └── [boardId]/
│   │   │   │               └── page.tsx
│   │   │   ├── settings/
│   │   │   │   └── page.tsx
│   │   │   └── profile/
│   │   │       └── page.tsx
│   │   │
│   │   ├── layout.tsx                  # Root layout
│   │   ├── page.tsx                    # Landing page
│   │   ├── loading.tsx
│   │   ├── error.tsx
│   │   ├── not-found.tsx
│   │   └── globals.css
│   │
│   ├── components/
│   │   ├── ui/                         # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   │
│   │   ├── board/                      # Board-specific components
│   │   │   ├── board-view.tsx
│   │   │   ├── board-column.tsx
│   │   │   ├── board-card.tsx
│   │   │   └── card-detail-modal.tsx
│   │   │
│   │   ├── workspace/                  # Workspace components
│   │   │   ├── workspace-switcher.tsx
│   │   │   └── member-list.tsx
│   │   │
│   │   ├── git/                        # Git integration components
│   │   │   ├── pr-badge.tsx
│   │   │   ├── branch-create-button.tsx
│   │   │   └── ci-status-indicator.tsx
│   │   │
│   │   ├── layout/                     # Layout components
│   │   │   ├── navbar.tsx
│   │   │   ├── sidebar.tsx
│   │   │   ├── command-palette.tsx
│   │   │   └── user-menu.tsx
│   │   │
│   │   └── shared/                     # Shared components
│   │       ├── avatar.tsx
│   │       ├── loading-spinner.tsx
│   │       └── error-boundary.tsx
│   │
│   ├── lib/
│   │   ├── api/                        # API client and services
│   │   │   ├── client.ts
│   │   │   ├── workspaces.ts
│   │   │   ├── boards.ts
│   │   │   ├── cards.ts
│   │   │   ├── git.ts
│   │   │   └── types.ts
│   │   │
│   │   ├── hooks/                      # Custom React hooks
│   │   │   ├── use-auth.ts
│   │   │   ├── use-websocket.ts
│   │   │   ├── use-board.ts
│   │   │   ├── use-cards.ts
│   │   │   └── use-debounce.ts
│   │   │
│   │   ├── store/                      # Zustand stores
│   │   │   ├── ui-store.ts
│   │   │   ├── board-store.ts
│   │   │   └── command-palette-store.ts
│   │   │
│   │   ├── utils/                      # Utility functions
│   │   │   ├── cn.ts
│   │   │   ├── date.ts
│   │   │   ├── validation.ts
│   │   │   └── constants.ts
│   │   │
│   │   └── websocket/                  # WebSocket client
│   │       ├── client.ts
│   │       └── events.ts
│   │
│   ├── types/                          # TypeScript types
│   │   ├── api.ts
│   │   ├── board.ts
│   │   ├── card.ts
│   │   └── workspace.ts
│   │
│   ├── styles/
│   │   └── theme.css
│   │
│   └── middleware.ts                   # Next.js middleware (auth)
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── .env.local.example
├── components.json                     # shadcn/ui config
├── next.config.js
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── vitest.config.ts
```

---

## Component Standards

### Component Template (Client Component)

```typescript
'use client'

import { useState } from 'react'
import { cn } from '@/lib/utils/cn'

interface BoardCardProps {
  id: string
  title: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  assignees?: Array<{ id: string; name: string; avatar: string }>
  onCardClick?: (id: string) => void
  className?: string
}

export function BoardCard({
  id,
  title,
  priority,
  assignees = [],
  onCardClick,
  className,
}: BoardCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  const handleClick = () => {
    onCardClick?.(id)
  }

  const priorityColors = {
    low: 'bg-blue-100 text-blue-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    urgent: 'bg-red-100 text-red-800',
  }

  return (
    <div
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={cn(
        'rounded-lg border bg-white p-4 shadow-sm transition-shadow cursor-pointer',
        isHovered && 'shadow-md',
        className
      )}
    >
      <div className="mb-2 flex items-center justify-between">
        <span
          className={cn(
            'inline-flex rounded-full px-2 py-1 text-xs font-medium',
            priorityColors[priority]
          )}
        >
          {priority}
        </span>
      </div>
      <h3 className="text-sm font-medium text-gray-900">{title}</h3>
      {assignees.length > 0 && (
        <div className="mt-3 flex -space-x-2">
          {assignees.map((assignee) => (
            <img
              key={assignee.id}
              src={assignee.avatar}
              alt={assignee.name}
              className="h-6 w-6 rounded-full border-2 border-white"
              title={assignee.name}
            />
          ))}
        </div>
      )}
    </div>
  )
}
```

### Naming Conventions

- **Files:** kebab-case (`board-card.tsx`, `user-menu.tsx`)
- **Components:** PascalCase (`BoardCard`, `UserMenu`)
- **Props:** `{ComponentName}Props` interface
- **Event Handlers:** `on{Event}` (props), `handle{Event}` (internal)
- **Boolean Props:** Prefix with `is`, `has`, `should`, `can`
- **Server vs Client:** Use Server Components by default, add `'use client'` only when needed

---

## State Management

### Philosophy

- **Client State (Zustand):** Modals, sidebar, theme, filters
- **Server State (TanStack Query):** API data (boards, cards, users)

### Store Structure

```
lib/store/
├── ui-store.ts              # Global UI state
├── board-store.ts           # Board UI state
└── command-palette-store.ts # Command palette state
```

### UI Store Example

```typescript
// lib/store/ui-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIStore {
  theme: 'light' | 'dark' | 'system'
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  isSidebarOpen: boolean
  toggleSidebar: () => void
  activeModal: 'card-detail' | 'create-board' | 'settings' | null
  modalData: Record<string, any> | null
  openModal: (modal: string, data?: Record<string, any>) => void
  closeModal: () => void
}

export const useUIStore = create<UIStore>()(
  persist(
    (set) => ({
      theme: 'system',
      isSidebarOpen: true,
      activeModal: null,
      modalData: null,
      setTheme: (theme) => set({ theme }),
      toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
      openModal: (modal, data) => set({ activeModal: modal as any, modalData: data || null }),
      closeModal: () => set({ activeModal: null, modalData: null }),
    }),
    {
      name: 'taskly-ui-store',
      partialize: (state) => ({ theme: state.theme, isSidebarOpen: state.isSidebarOpen }),
    }
  )
)
```

### TanStack Query Pattern

```typescript
// lib/hooks/use-board.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getBoard, updateCard } from '@/lib/api/boards'

export function useBoard(boardId: string) {
  return useQuery({
    queryKey: ['boards', boardId],
    queryFn: () => getBoard(boardId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true,
  })
}

export function useUpdateCard(boardId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ cardId, updates }) => updateCard(cardId, updates),
    onMutate: async ({ cardId, updates }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['boards', boardId] })
      const previousBoard = queryClient.getQueryData(['boards', boardId])
      queryClient.setQueryData(['boards', boardId], (old) => ({
        ...old,
        cards: old.cards.map((card) =>
          card.id === cardId ? { ...card, ...updates } : card
        ),
      }))
      return { previousBoard }
    },
    onError: (err, variables, context) => {
      queryClient.setQueryData(['boards', boardId], context.previousBoard)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['boards', boardId] })
    },
  })
}
```

---

## API Integration

### Base API Client

```typescript
// lib/api/client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.taskly.app'

export class APIError extends Error {
  constructor(
    public status: number,
    public type: string,
    public title: string,
    message: string,
    public errors?: Array<{ field: string; message: string }>
  ) {
    super(message)
    this.name = 'APIError'
  }
}

function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('access_token')
}

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) return false

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (!response.ok) return false
    const data = await response.json()
    localStorage.setItem('access_token', data.access_token)
    return true
  } catch {
    return false
  }
}

export async function apiClient<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const accessToken = getAccessToken()

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }

  let response = await fetch(url, { ...options, headers })

  // Handle 401 - Try to refresh token
  if (response.status === 401 && accessToken) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      const newToken = getAccessToken()
      if (newToken) {
        headers['Authorization'] = `Bearer ${newToken}`
        response = await fetch(url, { ...options, headers })
      }
    } else {
      localStorage.clear()
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
  }

  const data = await response.json()

  if (!response.ok) {
    throw new APIError(
      response.status,
      data.type || 'https://taskly.app/errors/unknown',
      data.title || 'API Error',
      data.detail || `HTTP ${response.status}`,
      data.errors
    )
  }

  return data as T
}

export const api = {
  get: <T = any>(endpoint: string, options?: RequestInit) =>
    apiClient<T>(endpoint, { ...options, method: 'GET' }),
  post: <T = any>(endpoint: string, data?: any, options?: RequestInit) =>
    apiClient<T>(endpoint, { ...options, method: 'POST', body: JSON.stringify(data) }),
  patch: <T = any>(endpoint: string, data?: any, options?: RequestInit) =>
    apiClient<T>(endpoint, { ...options, method: 'PATCH', body: JSON.stringify(data) }),
  delete: <T = any>(endpoint: string, options?: RequestInit) =>
    apiClient<T>(endpoint, { ...options, method: 'DELETE' }),
}
```

### API Services

```typescript
// lib/api/cards.ts
import { api } from './client'

export const cardsAPI = {
  getCard: (cardId: string) => api.get(`/cards/${cardId}`),
  createCard: (data) => api.post('/cards', data),
  updateCard: (cardId: string, updates) => api.patch(`/cards/${cardId}`, updates),
  deleteCard: (cardId: string) => api.delete(`/cards/${cardId}`),
  bulkUpdate: (cardIds, updates) => api.post('/cards/bulk-update', { card_ids: cardIds, updates }),
  createBranch: (cardId: string, data) => api.post(`/cards/${cardId}/create-branch`, data),
}
```

---

## Routing

### Middleware (Authentication)

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const protectedRoutes = ['/workspaces', '/settings', '/profile']
const authRoutes = ['/login']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const accessToken = request.cookies.get('access_token')?.value

  const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route))
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route))

  if (isProtectedRoute && !accessToken) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  if (isAuthRoute && accessToken) {
    return NextResponse.redirect(new URL('/workspaces', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|public).*)'],
}
```

### Route Definitions

| Path | Protection | Description |
|------|------------|-------------|
| `/` | Public | Landing page |
| `/login` | Public | GitHub OAuth |
| `/callback` | Public | OAuth callback |
| `/workspaces` | Protected | Workspace list |
| `/workspaces/[id]/boards/[id]` | Protected | Board view |
| `/settings` | Protected | User settings |

---

## Styling Guidelines

### Tailwind Approach

**Utility-first with Custom Theme:**
- Use Tailwind utility classes directly in JSX
- Custom components use `cn()` utility for conditional classes
- Global theme defined in CSS custom properties
- Dark mode via `next-themes` (class-based)

### Global Theme Variables

```css
/* styles/theme.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 224.3 76.3% 48%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

**Tailwind Config:**

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config
```

---

## Testing Requirements

### Component Test Template

```typescript
// tests/unit/components/board/board-card.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BoardCard } from '@/components/board/board-card'

describe('BoardCard', () => {
  it('renders card with title and priority', () => {
    render(
      <BoardCard
        id="card-1"
        title="Test Card"
        priority="high"
      />
    )

    expect(screen.getByText('Test Card')).toBeInTheDocument()
    expect(screen.getByText('high')).toBeInTheDocument()
  })

  it('calls onCardClick when clicked', () => {
    const handleClick = vi.fn()
    render(
      <BoardCard
        id="card-1"
        title="Test Card"
        priority="high"
        onCardClick={handleClick}
      />
    )

    fireEvent.click(screen.getByText('Test Card'))
    expect(handleClick).toHaveBeenCalledWith('card-1')
  })

  it('displays assignees avatars', () => {
    const assignees = [
      { id: '1', name: 'Alice', avatar: '/avatar1.jpg' },
      { id: '2', name: 'Bob', avatar: '/avatar2.jpg' },
    ]

    render(
      <BoardCard
        id="card-1"
        title="Test Card"
        priority="high"
        assignees={assignees}
      />
    )

    const avatars = screen.getAllByRole('img')
    expect(avatars).toHaveLength(2)
    expect(avatars[0]).toHaveAttribute('alt', 'Alice')
  })
})
```

### E2E Test Template

```typescript
// tests/e2e/board-operations.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Board Operations', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login')
    // Assume OAuth mock or test credentials
    await page.click('text=Sign in with GitHub')
    await page.waitForURL('/workspaces')
  })

  test('create and move card', async ({ page }) => {
    // Navigate to board
    await page.click('text=My Workspace')
    await page.click('text=Sprint Board')

    // Create card
    await page.click('button:has-text("Add Card")')
    await page.fill('input[name="title"]', 'Test Card')
    await page.click('button:has-text("Create")')

    // Verify card created
    await expect(page.locator('text=Test Card')).toBeVisible()

    // Drag card to In Progress column
    const card = page.locator('text=Test Card')
    const targetColumn = page.locator('text=In Progress').locator('..')
    await card.dragTo(targetColumn)

    // Verify card moved
    await expect(targetColumn.locator('text=Test Card')).toBeVisible()
  })
})
```

### Testing Best Practices

1. **Unit Tests:** Test components in isolation with mocked dependencies
2. **Integration Tests:** Test component interactions and API integration
3. **E2E Tests:** Test critical user flows (auth, CRUD, drag-and-drop)
4. **Coverage Goals:** 80% code coverage
5. **AAA Pattern:** Arrange, Act, Assert
6. **Mock External Dependencies:** API calls, routing, WebSocket

---

## Environment Configuration

### Environment Variables

```bash
# .env.local.example

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# GitHub OAuth
NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_client_id

# Application
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_COMMAND_PALETTE=true
NEXT_PUBLIC_ENABLE_DARK_MODE=true

# Analytics (optional)
NEXT_PUBLIC_SENTRY_DSN=
```

**Usage in Code:**

```typescript
// Access env vars
const API_URL = process.env.NEXT_PUBLIC_API_URL

// Type-safe env vars (optional)
// lib/utils/env.ts
export const env = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL!,
  wsUrl: process.env.NEXT_PUBLIC_WS_URL!,
  githubClientId: process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID!,
  appUrl: process.env.NEXT_PUBLIC_APP_URL!,
}
```

---

## Frontend Developer Standards

### Critical Coding Rules

**RULE 1: Use Server Components by Default**
```typescript
// ❌ WRONG - Unnecessary 'use client'
'use client'
export default function Page() {
  return <div>Static page</div>
}

// ✅ CORRECT - Server Component (no directive)
export default function Page() {
  return <div>Static page</div>
}
```

**RULE 2: Always Use TanStack Query for API Calls**
```typescript
// ❌ WRONG - Manual fetch in useEffect
const [data, setData] = useState(null)
useEffect(() => {
  fetch('/api/boards').then(r => r.json()).then(setData)
}, [])

// ✅ CORRECT - TanStack Query
const { data } = useQuery({ queryKey: ['boards'], queryFn: getBoards })
```

**RULE 3: Never Store Sensitive Data in localStorage Without Encryption**
```typescript
// ❌ WRONG - Plain text token
localStorage.setItem('token', accessToken)

// ✅ CORRECT - Use httpOnly cookies or encrypted storage
// (handled by API client)
```

**RULE 4: Always Use TypeScript Types for Props**
```typescript
// ❌ WRONG - Inline type
function Card({ title, id }: { title: string; id: string }) {}

// ✅ CORRECT - Interface
interface CardProps {
  title: string
  id: string
}
function Card({ title, id }: CardProps) {}
```

**RULE 5: Use cn() Utility for Conditional Classes**
```typescript
// ❌ WRONG - Template literal hell
className={`base-class ${isActive ? 'active-class' : ''} ${className}`}

// ✅ CORRECT - cn() utility
className={cn('base-class', isActive && 'active-class', className)}
```

**RULE 6: Optimize Re-renders with Zustand Selectors**
```typescript
// ❌ WRONG - Re-renders on any store change
const store = useUIStore()
const theme = store.theme

// ✅ CORRECT - Selector (only re-renders when theme changes)
const theme = useUIStore((state) => state.theme)
```

**RULE 7: Always Provide Loading States**
```typescript
// ❌ WRONG - No loading state
const { data } = useQuery(...)
return <div>{data.title}</div> // Crashes if data is undefined

// ✅ CORRECT - Handle loading
const { data, isLoading } = useQuery(...)
if (isLoading) return <Spinner />
return <div>{data?.title}</div>
```

**RULE 8: Use Optimistic Updates for Better UX**
```typescript
// ❌ WRONG - Wait for server response
const updateCard = useMutation({ mutationFn: updateCardAPI })

// ✅ CORRECT - Optimistic update (see State Management section)
const updateCard = useMutation({
  mutationFn: updateCardAPI,
  onMutate: async (updates) => {
    // Optimistically update cache
  },
  onError: (err, variables, context) => {
    // Rollback on error
  },
})
```

**RULE 9: Invalidate TanStack Query Cache on WebSocket Events**
```typescript
// ✅ CORRECT
ws.onmessage = (event) => {
  const { type, data } = JSON.parse(event.data)
  if (type === 'card_moved') {
    queryClient.invalidateQueries({ queryKey: ['boards', data.board_id] })
  }
}
```

**RULE 10: Always Handle API Errors with User-Friendly Messages**
```typescript
// ❌ WRONG - Show raw error
onError: (error) => alert(error.message)

// ✅ CORRECT - User-friendly toast
onError: (error) => {
  if (error instanceof APIError && error.status === 403) {
    toast({ title: 'Permission Denied', description: 'You cannot edit this board.' })
  } else {
    toast({ title: 'Error', description: 'Something went wrong. Please try again.' })
  }
}
```

---

### Quick Reference

**Common Commands:**
```bash
# Development
npm run dev          # Start dev server (localhost:3000)
npm run build        # Production build
npm run start        # Start production server
npm run lint         # Run ESLint
npm run test         # Run Vitest tests
npm run test:e2e     # Run Playwright E2E tests

# shadcn/ui
npx shadcn-ui@latest add button    # Add button component
npx shadcn-ui@latest add dialog    # Add dialog component
```

**Key Import Patterns:**
```typescript
// Components
import { Button } from '@/components/ui/button'
import { BoardCard } from '@/components/board/board-card'

// Hooks
import { useBoard } from '@/lib/hooks/use-board'
import { useUIStore } from '@/lib/store/ui-store'

// API
import { cardsAPI } from '@/lib/api/cards'
import { api } from '@/lib/api/client'

// Utils
import { cn } from '@/lib/utils/cn'
import { formatDate } from '@/lib/utils/date'

// Types
import type { Card, Board } from '@/types/api'
```

**File Naming:**
- Components: `kebab-case.tsx` (e.g., `board-card.tsx`)
- Pages: `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`
- Hooks: `use-*.ts` (e.g., `use-board.ts`)
- Stores: `*-store.ts` (e.g., `ui-store.ts`)
- Tests: `*.test.tsx` or `*.spec.ts`

---

## Next Steps

This frontend architecture is ready for implementation alongside the backend architecture. Together, they provide complete guidance for building Taskly.

**Implementation Order:**
1. **Epic 1 Story 1.1:** Set up frontend with `create-next-app` + shadcn/ui
2. **Epic 1 Story 1.4:** Implement GitHub OAuth login
3. **Epic 2:** Build board and card components with drag-and-drop
4. **Epic 3:** Integrate Git features (branch creation, PR linking)
5. **Epic 4:** Add sprint management and timeline view
6. **Epic 5:** Implement command palette

**Frontend-Backend Integration:**
- Backend API runs on `localhost:8000`
- Frontend dev server runs on `localhost:3000`
- CORS configured in backend to allow frontend origin
- WebSocket connection to `ws://localhost:8000/ws/boards/{boardId}`

---

**Document Status:** ✅ **APPROVED FOR IMPLEMENTATION**

This frontend architecture provides comprehensive guidance for AI-driven development while maintaining consistency with the backend architecture.
