import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Scan,
  Swords,
  FileText,
  Settings,
  Shield,
  Bot,
  Zap
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
    <div className="flex w-72 flex-col bg-cyber-black/50 backdrop-blur-2xl border-r border-white/5 relative z-10">
      {/* Brand Header */}
      <div className="flex h-24 items-center gap-4 px-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-cyber-blue/5 blur-3xl rounded-full -translate-x-1/2 -translate-y-1/2"></div>
        <div className="relative flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-cyber-blue to-cyber-purple shadow-[0_0_20px_rgba(56,189,248,0.3)]">
          <Shield className="h-7 w-7 text-white animate-pulse" />
        </div>
        <div className="relative">
          <h1 className="text-xl font-black tracking-tighter text-white leading-none">SECURE<span className="text-cyber-blue">RED</span></h1>
          <div className="flex items-center gap-1.5 mt-1">
            <Zap className="h-3 w-3 text-cyber-gold fill-cyber-gold" />
            <span className="text-[10px] font-bold text-cyber-gray tracking-widest uppercase">Agentic v2.0</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 px-4 py-8">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `group flex items-center gap-4 rounded-2xl px-4 py-3.5 text-sm font-bold transition-all duration-500 relative overflow-hidden ${
                isActive
                  ? 'bg-white/10 text-white shadow-[0_0_30px_rgba(255,255,255,0.05)]'
                  : 'text-cyber-gray hover:bg-white/5 hover:text-white'
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && <div className="absolute left-0 top-0 bottom-0 w-1 bg-cyber-blue shadow-[0_0_15px_rgba(56,189,248,0.8)]"></div>}
                <item.icon className={`h-5 w-5 transition-transform duration-500 group-hover:scale-110 ${isActive ? 'text-cyber-blue' : 'text-cyber-gray'}`} />
                <span className="tracking-tight">{item.name}</span>
                {item.name === 'Agentic AI' && (
                  <span className="ml-auto flex h-2 w-2 rounded-full bg-cyber-green animate-ping"></span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User Status / Footer */}
      <div className="p-6 mt-auto">
        <div className="p-4 rounded-2xl bg-gradient-to-br from-white/5 to-transparent border border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-cyber-green"></div>
            <span className="text-[10px] font-bold text-cyber-green uppercase tracking-widest">Network Secure</span>
          </div>
          <p className="text-[10px] text-cyber-gray mt-2 leading-relaxed">
            Encrypted connection active.
            Monitoring 128 nodes.
          </p>
        </div>
      </div>
    </div>
  )
}
