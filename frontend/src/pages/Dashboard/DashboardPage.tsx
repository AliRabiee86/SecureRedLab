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
      await new Promise((resolve) => setTimeout(resolve, 800));
      
      setRecentScans(mockScans.slice(0, 5));
      setRecentAttacks(mockAttacks.slice(0, 5));

      const distribution = {
        critical: mockVulnerabilities.filter((v) => v.severity === 'critical').length,
        high: mockVulnerabilities.filter((v) => v.severity === 'high').length,
        medium: mockVulnerabilities.filter((v) => v.severity === 'medium').length,
        low: mockVulnerabilities.filter((v) => v.severity === 'low').length,
        info: mockVulnerabilities.filter((v) => v.severity === 'info').length,
      };

      updateStats({
        total_scans: mockScans.length,
        total_attacks: mockAttacks.length,
        total_vulnerabilities: mockVulnerabilities.length,
        totalScans: mockScans.length,
        totalAttacks: mockAttacks.length,
        totalVulnerabilities: mockVulnerabilities.length,
        totalReports: 12,
        critical_count: distribution.critical,
        high_count: distribution.high,
        medium_count: distribution.medium,
        low_count: distribution.low,
        info_count: distribution.info,
        active_scans: 0,
        active_attacks: 0,
        critical_vulnerabilities: distribution.critical,
        recent_scans: mockScans.slice(0, 5),
        recent_attacks: mockAttacks.slice(0, 5),
        severity_distribution: distribution,
        scan_history: mockScans,
      });

      setIsLoading(false);
    };

    loadData();
  }, [setRecentScans, setRecentAttacks, updateStats]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <div className="w-12 h-12 border-4 border-critical-500 border-t-transparent rounded-full animate-spin"></div>
        <div className="text-gray-600 dark:text-gray-400 font-medium">Initializing Security Dashboard...</div>
      </div>
    );
  }

  // Safely get distribution for the chart
  const severityData = stats?.severity_distribution || {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    info: 0
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Security Overview</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Real-time monitoring and threat intelligence dashboard.
          </p>
        </div>
        
        {/* WebSocket Connection Status */}
        <div className="flex items-center space-x-2 bg-gray-800/50 px-3 py-1.5 rounded-full border border-gray-700">
          {isConnected ? (
            <>
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs font-medium text-green-400">System Live</span>
            </>
          ) : (
            <>
              <div className="w-2 h-2 rounded-full bg-red-500" />
              <span className="text-xs font-medium text-red-400">System Offline</span>
            </>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Scans"
          value={stats?.total_scans || 0}
          icon={Activity}
          trend={{ value: 12, isPositive: true }}
          color="blue"
        />
        <StatCard
          title="Total Attacks"
          value={stats?.total_attacks || 0}
          icon={Target}
          trend={{ value: 8, isPositive: true }}
          color="red"
        />
        <StatCard
          title="Vulnerabilities"
          value={stats?.total_vulnerabilities || 0}
          icon={Shield}
          trend={{ value: 5, isPositive: false }}
          color="orange"
        />
        <StatCard
          title="Reports Generated"
          value={(stats as any)?.totalReports || 0}
          icon={FileText}
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
        <SeverityChart data={severityData} />
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
          <button className="text-sm text-critical-500 hover:text-critical-400 transition-colors">View All Analysis →</button>
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
