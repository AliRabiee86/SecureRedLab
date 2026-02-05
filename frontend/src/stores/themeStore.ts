/**
 * SecureRedLab - Theme Store
 * Phase 8.1 - State Management with Zustand
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Theme } from '../types'

interface ThemeStore {
  // State
  theme: Theme
  
  // Actions
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => ({
      // Initial state
      theme: 'dark',

      // Actions
      setTheme: (theme) => {
        set({ theme })
        applyTheme(theme)
      },

      toggleTheme: () => {
        const currentTheme = get().theme
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark'
        set({ theme: newTheme })
        applyTheme(newTheme)
      },
    }),
    {
      name: 'theme-storage',
    }
  )
)

// Helper function to apply theme to DOM
function applyTheme(theme: Theme) {
  const root = document.documentElement
  
  if (theme === 'system') {
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light'
    root.classList.toggle('dark', systemTheme === 'dark')
  } else {
    root.classList.toggle('dark', theme === 'dark')
  }
}

// Initialize theme on load
if (typeof window !== 'undefined') {
  const storedTheme = (localStorage.getItem('theme-storage') 
    ? JSON.parse(localStorage.getItem('theme-storage')!).state.theme 
    : 'dark') as Theme
  applyTheme(storedTheme)
}
