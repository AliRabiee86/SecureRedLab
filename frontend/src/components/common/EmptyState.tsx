/**
 * SecureRedLab - EmptyState Component
 * Phase 8.2 - Common UI Components
 */

import type { LucideIcon } from 'lucide-react'
import Button from './Button'

export interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
}

export default function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 p-12 text-center">
      {Icon && (
        <div className="rounded-full bg-gray-700 p-4">
          <Icon className="h-8 w-8 text-gray-400" />
        </div>
      )}
      
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        {description && (
          <p className="text-sm text-gray-400">{description}</p>
        )}
      </div>

      {action && (
        <Button onClick={action.onClick} variant="primary" size="md">
          {action.label}
        </Button>
      )}
    </div>
  )
}
