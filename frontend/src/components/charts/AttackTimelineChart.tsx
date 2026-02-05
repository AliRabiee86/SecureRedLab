/**
 * SecureRedLab - Attack Timeline Chart
 * Phase 8.4 - Interactive Components
 * 
 * Real-time attack timeline visualization with ECharts
 */

import React, { useEffect, useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import type { Attack } from '@/types';

interface AttackTimelineChartProps {
  attacks: Attack[];
  height?: number | string;
  theme?: 'light' | 'dark';
}

const AttackTimelineChart: React.FC<AttackTimelineChartProps> = ({
  attacks,
  height = 400,
  theme = 'dark'
}) => {
  const option: EChartsOption = useMemo(() => {
    // Sort attacks by start time
    const sortedAttacks = [...attacks].sort((a, b) => 
      new Date(a.started_at).getTime() - new Date(b.started_at).getTime()
    );

    // Prepare data for timeline
    const timelineData = sortedAttacks.map(attack => ({
      name: attack.target,
      value: [
        new Date(attack.started_at).getTime(),
        attack.completed_at ? new Date(attack.completed_at).getTime() : Date.now(),
        attack.attack_type,
        attack.status
      ],
      itemStyle: {
        color: attack.status === 'SUCCESS' ? '#10b981' :
               attack.status === 'FAILED' ? '#ef4444' :
               attack.status === 'RUNNING' ? '#3b82f6' : '#6b7280'
      }
    }));

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const data = params.data;
          const startTime = new Date(data.value[0]).toLocaleString();
          const endTime = new Date(data.value[1]).toLocaleString();
          const duration = ((data.value[1] - data.value[0]) / 1000).toFixed(2);
          
          return `
            <div style="padding: 8px;">
              <strong>${data.name}</strong><br/>
              Type: ${data.value[2]}<br/>
              Status: ${data.value[3]}<br/>
              Start: ${startTime}<br/>
              End: ${endTime}<br/>
              Duration: ${duration}s
            </div>
          `;
        }
      },
      grid: {
        left: '10%',
        right: '10%',
        top: '15%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'time',
        axisLabel: {
          color: theme === 'dark' ? '#9ca3af' : '#4b5563',
          formatter: (value: number) => {
            const date = new Date(value);
            return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
          }
        },
        axisLine: {
          lineStyle: {
            color: theme === 'dark' ? '#374151' : '#d1d5db'
          }
        },
        splitLine: {
          lineStyle: {
            color: theme === 'dark' ? '#1f2937' : '#e5e7eb',
            type: 'dashed'
          }
        }
      },
      yAxis: {
        type: 'category',
        data: sortedAttacks.map(a => a.target),
        axisLabel: {
          color: theme === 'dark' ? '#9ca3af' : '#4b5563'
        },
        axisLine: {
          lineStyle: {
            color: theme === 'dark' ? '#374151' : '#d1d5db'
          }
        }
      },
      series: [{
        type: 'custom',
        renderItem: (params: any, api: any) => {
          const categoryIndex = api.value(0);
          const start = api.coord([api.value(1), categoryIndex]);
          const end = api.coord([api.value(2), categoryIndex]);
          const height = api.size([0, 1])[1] * 0.6;

          return {
            type: 'rect',
            shape: {
              x: start[0],
              y: start[1] - height / 2,
              width: end[0] - start[0],
              height: height
            },
            style: api.style({
              fill: params.data.itemStyle.color
            })
          };
        },
        encode: {
          x: [1, 2],
          y: 0
        },
        data: timelineData
      }]
    };
  }, [attacks, theme]);

  return (
    <div className="w-full">
      <ReactECharts
        option={option}
        style={{ height, width: '100%' }}
        theme={theme}
        opts={{ renderer: 'canvas' }}
      />
    </div>
  );
};

export default AttackTimelineChart;
