import { Bell, Moon, Sun, Search, Command } from 'lucide-react'
import { useThemeStore, useAuthStore, useDashboardStore } from '../../stores'

export default function Header() {
  const { theme, toggleTheme } = useThemeStore()
  const user = useAuthStore((state) => state.user)
  const notifications = useDashboardStore((state) => state.notifications)
  
  const unreadCount = notifications.filter((n) => !n.read).length

  return (
    <header className="flex h-24 items-center justify-between px-10 bg-cyber-black/20 backdrop-blur-md border-b border-white/5 relative z-10">
      {/* Search Bar */}
      <div className="relative group hidden md:block">
        <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
          <Search className="h-4 w-4 text-cyber-gray group-focus-within:text-cyber-blue transition-colors" />
        </div>
        <input 
          type="text" 
          placeholder="Quick Search Assets..."
          className="bg-white/5 border border-white/5 rounded-2xl pl-12 pr-16 py-2.5 text-sm text-white w-80 focus:w-96 focus:border-cyber-blue/30 focus:bg-white/10 outline-none transition-all duration-500"
        />
        <div className="absolute inset-y-0 right-4 flex items-center gap-1 pointer-events-none">
          <Command className="h-3 w-3 text-cyber-gray" />
          <span className="text-[10px] font-bold text-cyber-gray">K</span>
        </div>
      </div>

      {/* Actions Area */}
      <div className="flex items-center gap-6">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="w-11 h-11 flex items-center justify-center rounded-2xl bg-white/5 border border-white/5 text-cyber-gray hover:text-white hover:bg-white/10 transition-all duration-300"
        >
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>

        {/* Notifications */}
        <button className="relative w-11 h-11 flex items-center justify-center rounded-2xl bg-white/5 border border-white/5 text-cyber-gray hover:text-white hover:bg-white/10 transition-all duration-300">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-cyber-blue text-[10px] font-black text-cyber-black shadow-[0_0_15px_rgba(56,189,248,0.5)]">
              {unreadCount}
            </span>
          )}
        </button>

        {/* User Profile */}
        <div className="flex items-center gap-4 pl-6 border-l border-white/10">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-black text-white tracking-tight">{user?.full_name || 'Admin Agent'}</p>
            <p className="text-[10px] font-bold text-cyber-blue uppercase tracking-widest">{user?.role || 'System Root'}</p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-cyber-blue/20 to-cyber-purple/20 border border-cyber-blue/20 flex items-center justify-center overflow-hidden group cursor-pointer hover:scale-105 transition-transform">
            <img 
              src={`https://api.dicebear.com/7.x/bottts/svg?seed=${user?.username || 'admin'}&backgroundColor=transparent`} 
              alt="avatar" 
              className="w-9 h-9 group-hover:rotate-12 transition-transform"
            />
          </div>
        </div>
      </div>
    </header>
  )
}
