import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Navbar } from '@/components/layout/navbar'

// Mock the useAuth hook
vi.mock('@/lib/hooks/use-auth', () => ({
  useAuth: vi.fn(),
}))

// Mock next-themes
vi.mock('next-themes', () => ({
  useTheme: () => ({
    theme: 'light',
    setTheme: vi.fn(),
  }),
}))

import { useAuth } from '@/lib/hooks/use-auth'

describe('Navbar', () => {
  const mockLogout = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders NavbarSkeleton when user is not loaded', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,
      login: vi.fn(),
      logout: mockLogout,
    })

    render(<Navbar />)

    // Check that skeleton is rendered (looking for the loading placeholders)
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('renders user info and navigation when user is authenticated', () => {
    const mockUser = {
      id: '123',
      username: 'testuser',
      email: 'test@example.com',
      avatar_url: 'https://avatars.githubusercontent.com/u/123',
      github_id: 123,
    }

    vi.mocked(useAuth).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false,
      error: null,
      login: vi.fn(),
      logout: mockLogout,
    })

    render(<Navbar />)

    // Check for logo
    expect(screen.getByText('Taskly')).toBeInTheDocument()

    // Check for navigation links
    expect(screen.getByText('Workspaces')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('renders avatar with user initial', () => {
    const mockUser = {
      id: '123',
      username: 'testuser',
      email: 'test@example.com',
      avatar_url: 'https://avatars.githubusercontent.com/u/123',
      github_id: 123,
    }

    vi.mocked(useAuth).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false,
      error: null,
      login: vi.fn(),
      logout: mockLogout,
    })

    render(<Navbar />)

    // Check that avatar button with user's initial exists
    const avatarButtons = screen.getAllByRole('button')
    const avatarButton = avatarButtons.find((btn) => btn.textContent?.includes('T'))
    expect(avatarButton).toBeDefined()
    expect(avatarButton?.getAttribute('aria-haspopup')).toBe('menu')
  })
})
