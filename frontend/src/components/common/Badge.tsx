/**
 * SecureRedLab - Badge Component
 * Phase 8.2 - Common UI Components
 */

import { forwardRef, type HTMLAttributes } from 'react'
import type { VulnerabilitySeverity, ScanStatus, AttackStatus } from '../../types'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: VulnerabilitySeverity | ScanStatus | AttackStatus | 'default'
  size?: 'sm' | 'md' | 'lg'
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ children, variant = 'default', size = 'md', className = '', ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-full font-medium'

    const variants = {
      // Severity variants
      critical: 'bg-critical-500/10 text-critical-500 border border-critical-500/20',
      high: 'bg-high-500/10 text-high-500 border border-high-500/20',
      medium: 'bg-medium-500/10 text-medium-500 border border-medium-500/20',
      low: 'bg-low-500/10 text-low-500 border border-low-500/20',
      info: 'bg-info-500/10 text-info-500 border border-info-500/20',
      
      // Status variants
      pending: 'bg-medium-500/10 text-medium-500 border border-medium-500/20',
      running: 'bg-low-500/10 text-low-500 border border-low-500/20',
      completed: 'bg-info-500/10 text-info-500 border border-info-500/20',
      failed: 'bg-critical-500/10 text-critical-500 border border-critical-500/20',
      cancelled: 'bg-gray-600/10 text-gray-400 border border-gray-600/20',
      success: 'bg-info-500/10 text-info-500 border border-info-500/20',
      
      // Default
      default: 'bg-gray-600/10 text-gray-300 border border-gray-600/20',
    }

    const sizes = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-2.5 py-1 text-sm',
      lg: 'px-3 py-1.5 text-base',
    }

    return (
      <span
        ref={ref}
        className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
        {...props}
      >
        {children}
      </span>
    )
  }
)

Badge.displayName = 'Badge'

export default Badge
