/**
 * SecureRedLab - ScanHistoryChart Component
 * Phase 8.2 - Scan History Line Chart
 */

import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  type ChartOptions,
} from 'chart.js'
import type { ChartDataPoint } from '../../types'
import { Card } from '../common'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

export interface ScanHistoryChartProps {
  data: ChartDataPoint[]
  isLoading?: boolean
}

export default function ScanHistoryChart({ data, isLoading = false }: ScanHistoryChartProps) {
  const chartData = {
    labels: data.map((d) => d.label || d.date),
    datasets: [
      {
        label: 'Scans',
        data: data.map((d) => d.value),
        borderColor: 'rgb(220, 38, 38)',
        backgroundColor: 'rgba(220, 38, 38, 0.1)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: 'rgb(220, 38, 38)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  }

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: '#f1f5f9',
        bodyColor: '#cbd5e1',
        borderColor: '#475569',
        borderWidth: 1,
        padding: 12,
        displayColors: false,
        callbacks: {
          label: function (context) {
            return `Scans: ${context.parsed.y}`
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(71, 85, 105, 0.3)',
        },
        ticks: {
          color: '#94a3b8',
          font: {
            size: 11,
          },
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(71, 85, 105, 0.3)',
        },
        ticks: {
          color: '#94a3b8',
          font: {
            size: 11,
          },
          stepSize: 5,
        },
      },
    },
  }

  return (
    <Card>
      <h3 className="text-lg font-semibold text-white mb-4">Scan Activity (Last 7 Days)</h3>

      {isLoading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="animate-pulse text-dark-400">Loading chart...</div>
        </div>
      ) : (
        <div className="h-64">
          <Line data={chartData} options={options} />
        </div>
      )}
    </Card>
  )
}
