/**
 * SecureRedLab - Dashboard Store Tests
 * Phase 8.5 - Testing & Polish
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useDashboardStore } from '@/stores/dashboardStore';
import type { Scan, Attack, DashboardStats, Notification } from '@/types';

describe('Dashboard Store', () => {
  beforeEach(() => {
    // Reset store before each test
    const store = useDashboardStore.getState();
    store.setStats(null);
    store.activeScans.forEach(scan => store.removeScan(scan.id));
    store.activeAttacks.forEach(attack => store.removeAttack(attack.id));
    store.clearNotifications();
    store.setLoading(false);
  });

  it('initializes with default state', () => {
    const state = useDashboardStore.getState();
    expect(state.stats).toBeNull();
    expect(state.activeScans).toEqual([]);
    expect(state.activeAttacks).toEqual([]);
    expect(state.notifications).toEqual([]);
    expect(state.isLoading).toBe(false);
  });

  it('sets dashboard stats', () => {
    const mockStats: DashboardStats = {
      total_scans: 10,
      active_scans: 2,
      total_attacks: 5,
      active_attacks: 1,
      total_vulnerabilities: 15,
      critical_vulnerabilities: 3,
      recent_scans: [],
      recent_attacks: [],
      severity_distribution: {
        critical: 3,
        high: 5,
        medium: 4,
        low: 2,
        info: 1
      },
      scan_history: []
    };

    useDashboardStore.getState().setStats(mockStats);
    expect(useDashboardStore.getState().stats).toEqual(mockStats);
  });

  it('adds and updates scan', () => {
    const mockScan: Scan = {
      id: 'scan-1',
      target: '192.168.1.0/24',
      scan_type: 'NMAP',
      status: 'RUNNING',
      progress: 50,
      started_at: '2024-01-20T10:00:00Z',
      created_at: '2024-01-20T09:55:00Z',
      updated_at: '2024-01-20T10:00:00Z',
      user_id: 'user-1'
    };

    const store = useDashboardStore.getState();
    store.addScan(mockScan);
    
    expect(store.activeScans).toHaveLength(1);
    expect(store.activeScans[0]).toEqual(mockScan);

    // Update scan
    store.updateScan('scan-1', { progress: 75, status: 'RUNNING' });
    expect(store.activeScans[0].progress).toBe(75);
  });

  it('removes scan', () => {
    const mockScan: Scan = {
      id: 'scan-1',
      target: '192.168.1.0/24',
      scan_type: 'NMAP',
      status: 'RUNNING',
      progress: 50,
      started_at: '2024-01-20T10:00:00Z',
      created_at: '2024-01-20T09:55:00Z',
      updated_at: '2024-01-20T10:00:00Z',
      user_id: 'user-1'
    };

    const store = useDashboardStore.getState();
    store.addScan(mockScan);
    expect(store.activeScans).toHaveLength(1);

    store.removeScan('scan-1');
    expect(store.activeScans).toHaveLength(0);
  });

  it('adds and updates attack', () => {
    const mockAttack: Attack = {
      id: 'attack-1',
      target: '192.168.1.10',
      attack_type: 'METASPLOIT',
      module: 'exploit/windows/smb/ms17_010_eternalblue',
      status: 'RUNNING',
      progress: 30,
      started_at: '2024-01-20T11:00:00Z',
      created_at: '2024-01-20T10:55:00Z',
      updated_at: '2024-01-20T11:00:00Z',
      user_id: 'user-1'
    };

    const store = useDashboardStore.getState();
    store.addAttack(mockAttack);
    
    expect(store.activeAttacks).toHaveLength(1);
    expect(store.activeAttacks[0]).toEqual(mockAttack);

    // Update attack
    store.updateAttack('attack-1', { progress: 60, status: 'RUNNING' });
    expect(store.activeAttacks[0].progress).toBe(60);
  });

  it('manages notifications', () => {
    const mockNotification: Notification = {
      id: 'notif-1',
      type: 'success',
      title: 'Test Notification',
      message: 'This is a test',
      timestamp: '2024-01-20T12:00:00Z',
      read: false
    };

    const store = useDashboardStore.getState();
    store.addNotification(mockNotification);
    
    expect(store.notifications).toHaveLength(1);
    expect(store.notifications[0].read).toBe(false);

    // Mark as read
    store.markNotificationRead('notif-1');
    expect(store.notifications[0].read).toBe(true);

    // Clear notifications
    store.clearNotifications();
    expect(store.notifications).toHaveLength(0);
  });

  it('limits notifications to 50', () => {
    const store = useDashboardStore.getState();
    
    // Add 60 notifications
    for (let i = 0; i < 60; i++) {
      store.addNotification({
        id: `notif-${i}`,
        type: 'info',
        title: `Notification ${i}`,
        message: 'Test',
        timestamp: new Date().toISOString(),
        read: false
      });
    }

    expect(store.notifications).toHaveLength(50);
  });

  it('toggles loading state', () => {
    const store = useDashboardStore.getState();
    expect(store.isLoading).toBe(false);

    store.setLoading(true);
    expect(store.isLoading).toBe(true);

    store.setLoading(false);
    expect(store.isLoading).toBe(false);
  });
});
