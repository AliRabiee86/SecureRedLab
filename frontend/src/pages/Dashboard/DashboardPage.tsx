import { useEffect, useState } from 'react';
import { Activity, Shield, Target, FileText, Wifi, WifiOff } from 'lucide-react';
import { useDashboardStore } from '../../stores/dashboardStore';
import { useWebSocket, useWebSocketEvent } from '../../hooks/useWebSocket';
import {
  StatCard,
  ScanList,
  AttackList,
  SeverityChart,
  ScanHistoryChart,
  VulnerabilityCard,
  QuickActions,
} from '../../components/dashboard';
import { mockScans, mockAttacks, mockVulnerabilities } from '../../data/mockData';

export default function DashboardPage() {
  const { stats, recentScans, recentAttacks, updateStats, setRecentScans, setRecentAttacks, updateScan } =
    useDashboardStore();
  const [isLoading, setIsLoading] = useState(true);
  
  // WebSocket connection
  const { isConnected } = useWebSocket({
    autoConnect: true,
    onConnect: () => console.log('✅ Dashboard: WebSocket connected'),
    onDisconnect: () => console.log('🔌 Dashboard: WebSocket disconnected'),
  });

  // Subscribe to scan progress updates
  useWebSocketEvent('scan.progress', (data) => {
    console.log('📊 Scan progress update:', data);
    updateScan(data.scan_id, { progress: data.progress, status: data.status });
  });

  // Subscribe to scan completed events
  useWebSocketEvent('scan.completed', (data) => {
    console.log('✅ Scan completed:', data);
    updateScan(data.scan_id, { status: 'completed', progress: 100 });
  });

  useEffect(() => {
    // Simulate loading data
    const loadData = async () => {
      setIsLoading(true);
      
      // In production, this would be API calls
      await new Promise((resolve) => setTimeout(resolve, 500));
      
      setRecentScans(mockScans.slice(0, 5));
      setRecentAttacks(mockAttacks.slice(0, 5));

      updateStats({
        total_scans: mockScans.length,
        total_attacks: mockAttacks.length,
        total_vulnerabilities: mockVulnerabilities.length,
        totalScans: mockScans.length,
        totalAttacks: mockAttacks.length,
        totalVulnerabilities: mockVulnerabilities.length,
        totalReports: 12,
        critical_count: mockVulnerabilities.filter((v) => v.severity === 'critical').length,
        high_count: mockVulnerabilities.filter((v) => v.severity === 'high').length,
        medium_count: mockVulnerabilities.filter((v) => v.severity === 'medium').length,
        low_count: mockVulnerabilities.filter((v) => v.severity === 'low').length,
        info_count: mockVulnerabilities.filter((v) => v.severity === 'info').length,
        active_scans: 0,
        active_attacks: 0,
        critical_vulnerabilities: 0,
        recent_scans: [],
        recent_attacks: [],
        severity_distribution: {
          critical: 0,
          high: 0,
          medium: 0,
          low: 0,
          info: 0,
        },
        scan_history: [],
      });

      setIsLoading(false);
    };

    loadData();
  }, [setRecentScans, setRecentAttacks, updateStats]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-600 dark:text-gray-400">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Welcome back! Here's what's happening with your security testing.
          </p>
        </div>
        
        {/* WebSocket Connection Status */}
        <div className="flex items-center space-x-2">
          {isConnected ? (
            <>
              <Wifi className="w-5 h-5 text-green-500" />
              <span className="text-sm text-green-600 dark:text-green-400">Live</span>
            </>
          ) : (
            <>
              <WifiOff className="w-5 h-5 text-red-500" />
              <span className="text-sm text-red-600 dark:text-red-400">Offline</span>
            </>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Scans"
          value={stats?.total_scans || 0}
          icon={<Activity className="w-6 h-6" />}
          trend={{ value: 12, isPositive: true }}
          color="blue"
        />
        <StatCard
          title="Active Attacks"
          value={stats?.total_attacks || 0}
          icon={<Target className="w-6 h-6" />}
          trend={{ value: 8, isPositive: true }}
          color="red"
        />
        <StatCard
          title="Vulnerabilities"
          value={stats?.total_vulnerabilities || 0}
          icon={<Shield className="w-6 h-6" />}
          trend={{ value: 5, isPositive: false }}
          color="orange"
        />
        <StatCard
          title="Reports"
          value={(stats as any)?.totalReports || 0}
          icon={<FileText className="w-6 h-6" />}
          trend={{ value: 3, isPositive: true }}
          color="green"
        />
      </div>

      {/* Quick Actions */}
      <QuickActions
        onNewScan={() => console.log('New Scan')}
        onNewAttack={() => console.log('New Attack')}
        onViewReports={() => console.log('View Reports')}
        onSettings={() => console.log('Settings')}
      />

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SeverityChart data={mockVulnerabilities} />
        <ScanHistoryChart data={mockScans} />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ScanList scans={recentScans} onScanClick={(scan) => console.log('Scan clicked:', scan)} />
        <AttackList
          attacks={recentAttacks}
          onAttackClick={(attack) => console.log('Attack clicked:', attack)}
        />
      </div>

      {/* Top Vulnerabilities */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Critical Vulnerabilities
          </h2>
          <button className="text-sm text-primary hover:text-primary-dark">View All →</button>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {mockVulnerabilities
            .filter((v) => v.severity === 'critical' || v.severity === 'high')
            .slice(0, 4)
            .map((vuln) => (
              <VulnerabilityCard
                key={vuln.id}
                vulnerability={vuln}
                onClick={() => console.log('Vulnerability clicked:', vuln)}
              />
            ))}
        </div>
      </div>
    </div>
  );
}
