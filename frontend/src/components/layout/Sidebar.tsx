/**
 * SecureRedLab - Sidebar Component
 * Phase 8.1 - Navigation Sidebar
 */

import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Scan,
  Swords,
  FileText,
  Settings,
  Shield,
  Bot,
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Scans', href: '/scans', icon: Scan },
  { name: 'Attacks', href: '/attacks', icon: Swords },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Agentic AI', href: '/agentic', icon: Bot },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  return (
    <div className="flex w-64 flex-col bg-gray-800 border-r border-gray-700">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 px-6 border-b border-gray-700">
        <Shield className="h-8 w-8 text-critical-500" />
        <div>
          <h1 className="text-xl font-bold text-white">SecureRedLab</h1>
          <p className="text-xs text-gray-400">Penetration Testing Platform</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-critical-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-700 px-6 py-4">
        <p className="text-xs text-gray-400">
          Version 2.0.0 (Agentic)
          <br />
          © 2026 SecureRedLab
        </p>
      </div>
    </div>
  )
}
