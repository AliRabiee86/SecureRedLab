/**
 * SecureRedLab - Spinner Component
 * Phase 8.2 - Common UI Components
 */

import { Loader2 } from 'lucide-react'

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

export default function Spinner({ size = 'md', className = '' }: SpinnerProps) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12',
  }

  return (
    <Loader2 className={`animate-spin text-critical-500 ${sizes[size]} ${className}`} />
  )
}

export function LoadingOverlay({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 p-12">
      <Spinner size="xl" />
      <p className="text-dark-400">{message}</p>
    </div>
  )
}
