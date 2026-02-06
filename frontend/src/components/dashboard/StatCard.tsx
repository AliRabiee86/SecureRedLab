/**
 * SecureRedLab - StatCard Component
 * Phase 8.2 - Dashboard Statistics Card
 */

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
    blue: 'text-low-500 bg-low-500/10',
    orange: 'text-high-500 bg-high-500/10',
    red: 'text-critical-500 bg-critical-500/10',
    green: 'text-info-500 bg-info-500/10',
    purple: 'text-medium-500 bg-medium-500/10',
  }

  return (
    <Card className="hover:border-dark-600 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-dark-400">{title}</p>
          
          {isLoading ? (
            <div className="mt-2 h-8 w-24 animate-pulse rounded bg-dark-700" />
          ) : (
            <p className="mt-2 text-3xl font-bold text-white">{value}</p>
          )}

          {trend && !isLoading && (
            <div className="mt-2 flex items-center gap-1 text-sm">
              <span className={trend.isPositive ? 'text-info-500' : 'text-critical-500'}>
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className="text-dark-400">vs last week</span>
            </div>
          )}
        </div>

        <div className={`rounded-full p-3 ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </Card>
  )
}
