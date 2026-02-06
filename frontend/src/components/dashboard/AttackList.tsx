/**
 * SecureRedLab - AttackList Component
 * Phase 8.2 - Recent Attacks List
 */

import { Swords, CheckCircle, XCircle, Activity, Clock } from 'lucide-react'
import type { Attack } from '../../types'
import { Card, Badge, EmptyState } from '../common'
import { formatRelativeTime } from '../../utils/date'

export interface AttackListProps {
  attacks: Attack[]
  isLoading?: boolean
}

export default function AttackList({ attacks, isLoading = false }: AttackListProps) {
  if (isLoading) {
    return (
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Recent Attacks</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-16 rounded bg-gray-700" />
            </div>
          ))}
        </div>
      </Card>
    )
  }

  if (attacks.length === 0) {
    return (
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Recent Attacks</h3>
        <EmptyState
          icon={Swords}
          title="No attacks yet"
          description="Launch your first exploitation attack"
        />
      </Card>
    )
  }

  const getStatusIcon = (status: Attack['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-info-500" />
      case 'running':
        return <Activity className="h-5 w-5 text-low-500 animate-pulse" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-critical-500" />
      case 'pending':
        return <Clock className="h-5 w-5 text-medium-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getModuleShortName = (module: string) => {
    const parts = module.split('/')
    return parts[parts.length - 1] || module
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Recent Attacks</h3>
        <button className="text-sm text-critical-500 hover:text-critical-400">
          View all →
        </button>
      </div>

      <div className="space-y-3">
        {attacks.map((attack) => (
          <div
            key={attack.id}
            className="flex items-center gap-4 p-4 rounded-lg bg-gray-700/50 hover:bg-gray-700 transition-colors cursor-pointer border border-transparent hover:border-gray-600"
          >
            {/* Status Icon */}
            <div className="flex-shrink-0">
              {getStatusIcon(attack.status)}
            </div>

            {/* Attack Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <p className="font-medium text-white truncate">{attack.target}</p>
                <Badge variant={attack.status} size="sm">
                  {attack.status}
                </Badge>
              </div>
              <p className="text-sm text-gray-400 truncate">
                {getModuleShortName(attack.module)}
              </p>
              <p className="text-xs text-gray-500">
                {attack.attack_type.toUpperCase()} • {formatRelativeTime(attack.started_at)}
              </p>
            </div>

            {/* Progress/Results */}
            {attack.status === 'running' && (
              <div className="flex-shrink-0 text-right">
                <p className="text-sm font-medium text-white">{attack.progress}%</p>
                <div className="mt-1 w-16 h-1.5 bg-gray-600 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-high-500 transition-all duration-300"
                    style={{ width: `${attack.progress}%` }}
                  />
                </div>
              </div>
            )}

            {attack.status === 'success' && attack.results?.sessions && (
              <div className="flex-shrink-0 text-right">
                <p className="text-sm font-medium text-info-500">
                  {attack.results.sessions.length} session(s)
                </p>
                <p className="text-xs text-gray-400">Exploited</p>
              </div>
            )}

            {attack.status === 'failed' && (
              <div className="flex-shrink-0 text-right">
                <p className="text-sm font-medium text-critical-500">Failed</p>
                <p className="text-xs text-gray-400">No exploit</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </Card>
  )
}
