/**
 * SecureRedLab - Header Component
 * Phase 8.1 - Top Navigation Header
 */

import { Bell, Moon, Sun, User, LogOut } from 'lucide-react'
import { useThemeStore, useAuthStore, useDashboardStore } from '../../stores'

export default function Header() {
  const { theme, toggleTheme } = useThemeStore()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)
  const notifications = useDashboardStore((state) => state.notifications)
  
  const unreadCount = notifications.filter((n) => !n.read).length

  return (
    <header className="flex h-16 items-center justify-between border-b border-dark-700 bg-dark-800 px-6">
      {/* Left side - Empty for now */}
      <div></div>

      {/* Right side - Actions */}
      <div className="flex items-center gap-4">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-dark-300 hover:bg-dark-700 hover:text-white transition-colors"
          title="Toggle theme"
        >
          {theme === 'dark' ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </button>

        {/* Notifications */}
        <button
          className="relative rounded-lg p-2 text-dark-300 hover:bg-dark-700 hover:text-white transition-colors"
          title="Notifications"
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-critical-500 text-xs text-white">
              {unreadCount}
            </span>
          )}
        </button>

        {/* User Menu */}
        <div className="flex items-center gap-3 pl-4 border-l border-dark-700">
          <div className="text-right">
            <p className="text-sm font-medium text-white">
              {user?.full_name || 'Guest User'}
            </p>
            <p className="text-xs text-dark-400">{user?.role || 'viewer'}</p>
          </div>
          
          <button
            className="rounded-lg p-2 text-dark-300 hover:bg-dark-700 hover:text-white transition-colors"
            title="User menu"
          >
            <User className="h-5 w-5" />
          </button>

          <button
            onClick={logout}
            className="rounded-lg p-2 text-dark-300 hover:bg-critical-600 hover:text-white transition-colors"
            title="Logout"
          >
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  )
}
