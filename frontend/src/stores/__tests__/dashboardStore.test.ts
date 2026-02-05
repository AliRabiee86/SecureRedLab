/**
 * SecureRedLab - Dashboard Store Tests
 * Phase 8.1 - Testing Example
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useDashboardStore } from '@stores/dashboardStore'
import type { Scan, ScanStatus, ScanType } from '@types'

describe('DashboardStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useDashboardStore.setState({
      stats: null,
      activeScans: [],
      activeAttacks: [],
      notifications: [],
      isLoading: false,
    })
  })

  it('should add a scan', () => {
    const store = useDashboardStore.getState()
    
    const mockScan: Scan = {
      id: '1',
      target: '192.168.1.1',
      scan_type: 'nmap' as ScanType,
      status: 'running' as ScanStatus,
      progress: 50,
      started_at: new Date().toISOString(),
      user_id: 'user1',
    }

    store.addScan(mockScan)

    const state = useDashboardStore.getState()
    expect(state.activeScans).toHaveLength(1)
    expect(state.activeScans[0]).toEqual(mockScan)
  })

  it('should update a scan', () => {
    const store = useDashboardStore.getState()
    
    const mockScan: Scan = {
      id: '1',
      target: '192.168.1.1',
      scan_type: 'nmap' as ScanType,
      status: 'running' as ScanStatus,
      progress: 50,
      started_at: new Date().toISOString(),
      user_id: 'user1',
    }

    store.addScan(mockScan)
    store.updateScan('1', { progress: 100, status: 'completed' as ScanStatus })

    const state = useDashboardStore.getState()
    expect(state.activeScans[0].progress).toBe(100)
    expect(state.activeScans[0].status).toBe('completed')
  })

  it('should remove a scan', () => {
    const store = useDashboardStore.getState()
    
    const mockScan: Scan = {
      id: '1',
      target: '192.168.1.1',
      scan_type: 'nmap' as ScanType,
      status: 'completed' as ScanStatus,
      progress: 100,
      started_at: new Date().toISOString(),
      user_id: 'user1',
    }

    store.addScan(mockScan)
    store.removeScan('1')

    const state = useDashboardStore.getState()
    expect(state.activeScans).toHaveLength(0)
  })
})
