/**
 * SecureRedLab - ScanList Component
 * Phase 8.2 - Recent Scans List
 */

import { Activity, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import type { Scan } from '../../types'
import { Card, Badge, EmptyState } from '../common'
import { formatRelativeTime } from '../../utils/date'

export interface ScanListProps {
  scans: Scan[]
  isLoading?: boolean
}

export default function ScanList({ scans, isLoading = false }: ScanListProps) {
  if (isLoading) {
    return (
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Recent Scans</h3>
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

  if (scans.length === 0) {
    return (
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Recent Scans</h3>
        <EmptyState
          icon={Activity}
          title="No scans yet"
          description="Start your first network scan to begin"
        />
      </Card>
    )
  }

  const getStatusIcon = (status: Scan['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-info-500" />
      case 'running':
        return <Activity className="h-5 w-5 text-low-500 animate-pulse" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-critical-500" />
      case 'pending':
        return <Clock className="h-5 w-5 text-medium-500" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />
    }
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Recent Scans</h3>
        <button className="text-sm text-critical-500 hover:text-critical-400">
          View all →
        </button>
      </div>

      <div className="space-y-3">
        {scans.map((scan) => (
          <div
            key={scan.id}
            className="flex items-center gap-4 p-4 rounded-lg bg-gray-700/50 hover:bg-gray-700 transition-colors cursor-pointer border border-transparent hover:border-gray-600"
          >
            {/* Status Icon */}
            <div className="flex-shrink-0">
              {getStatusIcon(scan.status)}
            </div>

            {/* Scan Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <p className="font-medium text-white truncate">{scan.target}</p>
                <Badge variant={scan.status} size="sm">
                  {scan.status}
                </Badge>
              </div>
              <p className="text-sm text-gray-400">
                {scan.scan_type.toUpperCase()} • {formatRelativeTime(scan.started_at)}
              </p>
            </div>

            {/* Progress */}
            {scan.status === 'running' && (
              <div className="flex-shrink-0 text-right">
                <p className="text-sm font-medium text-white">{scan.progress}%</p>
                <div className="mt-1 w-16 h-1.5 bg-gray-600 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-low-500 transition-all duration-300"
                    style={{ width: `${scan.progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Results */}
            {scan.status === 'completed' && scan.results && (
              <div className="flex-shrink-0 text-right">
                <p className="text-sm font-medium text-white">
                  {scan.results.open_ports?.length || 0} ports
                </p>
                <p className="text-xs text-gray-400">
                  {scan.results.services?.length || 0} services
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </Card>
  )
}
