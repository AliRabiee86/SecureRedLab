/**
 * SecureRedLab - SeverityChart Component
 * Phase 8.2 - Vulnerability Severity Distribution Chart
 */

import { Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  type ChartOptions,
} from 'chart.js'
import type { SeverityDistribution } from '../../types'
import { Card } from '../common'

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend)

export interface SeverityChartProps {
  data: SeverityDistribution
  isLoading?: boolean
}

export default function SeverityChart({ data, isLoading = false }: SeverityChartProps) {
  const chartData = {
    labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
    datasets: [
      {
        data: [data.critical, data.high, data.medium, data.low, data.info],
        backgroundColor: [
          'rgba(220, 38, 38, 0.8)',   // Critical - Red
          'rgba(234, 88, 12, 0.8)',   // High - Orange
          'rgba(202, 138, 4, 0.8)',   // Medium - Yellow
          'rgba(37, 99, 235, 0.8)',   // Low - Blue
          'rgba(22, 197, 94, 0.8)',   // Info - Green
        ],
        borderColor: [
          'rgb(220, 38, 38)',
          'rgb(234, 88, 12)',
          'rgb(202, 138, 4)',
          'rgb(37, 99, 235)',
          'rgb(22, 197, 94)',
        ],
        borderWidth: 2,
      },
    ],
  }

  const options: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#cbd5e1',
          padding: 15,
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: '#f1f5f9',
        bodyColor: '#cbd5e1',
        borderColor: '#475569',
        borderWidth: 1,
        padding: 12,
        displayColors: true,
        callbacks: {
          label: function (context) {
            const label = context.label || ''
            const value = context.parsed || 0
            const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0'
            return `${label}: ${value} (${percentage}%)`
          },
        },
      },
    },
  }

  const total = data.critical + data.high + data.medium + data.low + data.info

  return (
    <Card>
      <h3 className="text-lg font-semibold text-white mb-4">
        Vulnerability Distribution
      </h3>

      {isLoading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="animate-pulse text-gray-400">Loading chart...</div>
        </div>
      ) : total === 0 ? (
        <div className="h-64 flex items-center justify-center text-gray-400">
          No vulnerabilities found
        </div>
      ) : (
        <div className="h-64">
          <Doughnut data={chartData} options={options} />
        </div>
      )}

      {/* Summary Stats */}
      {!isLoading && total > 0 && (
        <div className="mt-6 grid grid-cols-5 gap-3 text-center border-t border-gray-700 pt-4">
          <div>
            <p className="text-2xl font-bold text-critical-500">{data.critical}</p>
            <p className="text-xs text-gray-400 mt-1">Critical</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-high-500">{data.high}</p>
            <p className="text-xs text-gray-400 mt-1">High</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-medium-500">{data.medium}</p>
            <p className="text-xs text-gray-400 mt-1">Medium</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-low-500">{data.low}</p>
            <p className="text-xs text-gray-400 mt-1">Low</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-info-500">{data.info}</p>
            <p className="text-xs text-gray-400 mt-1">Info</p>
          </div>
        </div>
      )}
    </Card>
  )
}
