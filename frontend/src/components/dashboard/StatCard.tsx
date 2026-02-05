import type { LucideIcon } from 'lucide-react'
import { Card } from '../common'

export interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  color?: 'blue' | 'orange' | 'red' | 'green' | 'purple'
  isLoading?: boolean
}

export default function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  trend,
  color = 'blue',
  isLoading = false 
}: StatCardProps) {
  const colorClasses = {
    blue: 'text-cyber-blue bg-cyber-blue/10 border-cyber-blue/20',
    orange: 'text-cyber-gold bg-cyber-gold/10 border-cyber-gold/20',
    red: 'text-cyber-red bg-cyber-red/10 border-cyber-red/20',
    green: 'text-cyber-green bg-cyber-green/10 border-cyber-green/20',
    purple: 'text-cyber-purple bg-cyber-purple/10 border-cyber-purple/20',
  }

  return (
    <Card className="group hover:scale-[1.02] active:scale-[0.98]">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-[10px] font-black text-cyber-gray uppercase tracking-[0.2em]">{title}</p>
          
          {isLoading ? (
            <div className="mt-2 h-8 w-24 animate-pulse rounded-lg bg-white/5" />
          ) : (
            <p className="mt-2 text-3xl font-black text-white tracking-tighter">{value}</p>
          )}

          {trend && !isLoading && (
            <div className="mt-3 flex items-center gap-2">
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-black ${trend.isPositive ? 'bg-cyber-green/10 text-cyber-green' : 'bg-cyber-red/10 text-cyber-red'}`}>
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className="text-[10px] font-bold text-cyber-gray uppercase">vs last cycle</span>
            </div>
          )}
        </div>

        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center border transition-all duration-500 group-hover:rotate-12 ${colorClasses[color]}`}>
          <Icon className="h-7 w-7" />
        </div>
      </div>
    </Card>
  )
}
