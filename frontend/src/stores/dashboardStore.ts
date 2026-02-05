/**
 * SecureRedLab - Dashboard Store
 * Phase 8.1 - State Management with Zustand
 */

import { create } from 'zustand'
import type { Scan, Attack, DashboardStats, Notification } from '../types'

interface DashboardStore {
  // State
  stats: DashboardStats | null
  activeScans: Scan[]
  activeAttacks: Attack[]
  recentScans: Scan[]
  recentAttacks: Attack[]
  notifications: Notification[]
  isLoading: boolean

  // Actions
  setStats: (stats: DashboardStats) => void
  updateStats: (updates: Partial<DashboardStats>) => void
  setRecentScans: (scans: Scan[]) => void
  setRecentAttacks: (attacks: Attack[]) => void
  addScan: (scan: Scan) => void
  updateScan: (scanId: string, updates: Partial<Scan>) => void
  removeScan: (scanId: string) => void
  addAttack: (attack: Attack) => void
  updateAttack: (attackId: string, updates: Partial<Attack>) => void
  removeAttack: (attackId: string) => void
  addNotification: (notification: Notification) => void
  markNotificationRead: (notificationId: string) => void
  clearNotifications: () => void
  setLoading: (isLoading: boolean) => void
}

export const useDashboardStore = create<DashboardStore>((set) => ({
  // Initial state
  stats: null,
  activeScans: [],
  activeAttacks: [],
  recentScans: [],
  recentAttacks: [],
  notifications: [],
  isLoading: false,

  // Actions
  setStats: (stats) => set({ stats }),

  updateStats: (updates) =>
    set((state) => ({
      stats: state.stats ? { ...state.stats, ...updates } : null,
    })),

  setRecentScans: (scans) => set({ recentScans: scans }),

  setRecentAttacks: (attacks) => set({ recentAttacks: attacks }),

  addScan: (scan) =>
    set((state) => ({
      activeScans: [scan, ...state.activeScans],
    })),

  updateScan: (scanId, updates) =>
    set((state) => ({
      activeScans: state.activeScans.map((scan) =>
        scan.id === scanId ? { ...scan, ...updates } : scan
      ),
    })),

  removeScan: (scanId) =>
    set((state) => ({
      activeScans: state.activeScans.filter((scan) => scan.id !== scanId),
    })),

  addAttack: (attack) =>
    set((state) => ({
      activeAttacks: [attack, ...state.activeAttacks],
    })),

  updateAttack: (attackId, updates) =>
    set((state) => ({
      activeAttacks: state.activeAttacks.map((attack) =>
        attack.id === attackId ? { ...attack, ...updates } : attack
      ),
    })),

  removeAttack: (attackId) =>
    set((state) => ({
      activeAttacks: state.activeAttacks.filter(
        (attack) => attack.id !== attackId
      ),
    })),

  addNotification: (notification) =>
    set((state) => ({
      notifications: [notification, ...state.notifications].slice(0, 50), // Keep last 50
    })),

  markNotificationRead: (notificationId) =>
    set((state) => ({
      notifications: state.notifications.map((notif) =>
        notif.id === notificationId ? { ...notif, read: true } : notif
      ),
    })),

  clearNotifications: () => set({ notifications: [] }),

  setLoading: (isLoading) => set({ isLoading }),
}))
