import { useEffect, useState } from 'react';
import { Activity, Shield, Target, FileText, Zap, Globe, Cpu, AlertTriangle } from 'lucide-react';
import { useDashboardStore } from '../../stores/dashboardStore';
import { useWebSocket } from '../../hooks/useWebSocket';
import {
  StatCard,
  ScanList,
  AttackList,
  SeverityChart,
  ScanHistoryChart,
  QuickActions,
} from '../../components/dashboard';
import { mockScans, mockAttacks, mockVulnerabilities } from '../../data/mockData';

export default function DashboardPage() {
  const { stats, recentScans, recentAttacks, updateStats, setRecentScans, setRecentAttacks } = useDashboardStore();
  const [isLoading, setIsLoading] = useState(true);
  
  const { isConnected } = useWebSocket({ autoConnect: true });

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 1200));
      
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
        active_scans: 2,
        active_attacks: 1,
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
      <div className="flex flex-col items-center justify-center h-[60vh] space-y-6">
        <div className="relative">
          <div className="w-20 h-20 border-2 border-cyber-blue/20 rounded-full animate-ping"></div>
          <div className="absolute inset-0 w-20 h-20 border-t-2 border-cyber-blue rounded-full animate-spin"></div>
          <Shield className="absolute inset-0 m-auto h-8 w-8 text-cyber-blue animate-pulse" />
        </div>
        <div className="flex flex-col items-center">
          <p className="text-white font-black tracking-widest uppercase text-sm">Synchronizing Intelligence</p>
          <p className="text-cyber-gray text-xs mt-1 font-mono">Accessing secure neural nodes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-1000">
      {/* Hero Section */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 rounded-full bg-cyber-blue/10 border border-cyber-blue/20 text-cyber-blue text-[10px] font-black uppercase tracking-widest">System Operational</span>
            <div className="flex items-center gap-1.5">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-cyber-green animate-pulse' : 'bg-cyber-red'}`}></div>
              <span className="text-[10px] font-bold text-cyber-gray uppercase">{isConnected ? 'Live Link Active' : 'Offline Mode'}</span>
            </div>
          </div>
          <h1 className="text-5xl font-black text-white tracking-tighter">Security <span className="text-cyber-blue">Pulse</span></h1>
          <p className="text-cyber-gray max-w-2xl font-medium leading-relaxed">
            Welcome to the command center. All agent nodes are currently monitoring 
            <span className="text-white"> 1,240 active vectors </span> across your infrastructure.
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="glass-card px-6 py-3 flex items-center gap-4">
            <div className="text-right">
              <p className="text-[10px] font-bold text-cyber-gray uppercase tracking-widest">Global Threat Level</p>
              <p className="text-xl font-black text-cyber-gold">MODERATE</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-cyber-gold animate-bounce" />
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          { title: 'Intelligence Scans', value: stats?.total_scans, icon: Activity, color: 'blue', trend: '+12%' },
          { title: 'Neural Attacks', value: stats?.total_attacks, icon: Target, color: 'red', trend: '+8%' },
          { title: 'Threats Neutralized', value: stats?.total_vulnerabilities, icon: Shield, color: 'orange', trend: '-5%' },
          { title: 'Agent Reports', value: 12, icon: FileText, color: 'green', trend: '+3%' },
        ].map((stat, i) => (
          <div key={i} className="glass-card p-6 group hover:border-cyber-blue/30 transition-all duration-500 hover:-translate-y-1">
            <div className="flex items-start justify-between">
              <div className={`p-3 rounded-2xl bg-cyber-${stat.color}/10 text-cyber-${stat.color} group-hover:scale-110 transition-transform`}>
                <stat.icon className="h-6 w-6" />
              </div>
              <span className={`text-[10px] font-black ${stat.trend.startsWith('+') ? 'text-cyber-green' : 'text-cyber-red'}`}>{stat.trend}</span>
            </div>
            <div className="mt-6">
              <p className="text-[10px] font-bold text-cyber-gray uppercase tracking-widest">{stat.title}</p>
              <p className="text-3xl font-black text-white mt-1">{stat.value || 0}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Main Analysis Area */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Left: Charts */}
        <div className="xl:col-span-2 space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="glass-card p-8">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-sm font-black text-white uppercase tracking-widest">Threat Distribution</h3>
                <Cpu className="h-4 w-4 text-cyber-blue" />
              </div>
              <div className="h-64">
                <SeverityChart data={stats?.severity_distribution || { critical: 0, high: 0, medium: 0, low: 0, info: 0 }} />
              </div>
            </div>
            <div className="glass-card p-8">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-sm font-black text-white uppercase tracking-widest">Attack Velocity</h3>
                <Zap className="h-4 w-4 text-cyber-gold" />
              </div>
              <div className="h-64">
                <ScanHistoryChart data={mockScans} />
              </div>
            </div>
          </div>
          
          <div className="glass-card overflow-hidden">
            <div className="p-8 border-b border-white/5 flex items-center justify-between">
              <h3 className="text-sm font-black text-white uppercase tracking-widest">Neural Scan Pipeline</h3>
              <Globe className="h-4 w-4 text-cyber-green" />
            </div>
            <ScanList scans={recentScans} />
          </div>
        </div>

        {/* Right: Active Threats & Quick Actions */}
        <div className="space-y-8">
          <div className="glass-card p-8">
            <h3 className="text-sm font-black text-white uppercase tracking-widest mb-6">Agent Actions</h3>
            <QuickActions
              onNewScan={() => {}}
              onNewAttack={() => {}}
              onViewReports={() => {}}
              onSettings={() => {}}
            />
          </div>

          <div className="glass-card p-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-black text-white uppercase tracking-widest">Active Engagements</h3>
              <span className="flex h-2 w-2 rounded-full bg-cyber-red animate-ping"></span>
            </div>
            <AttackList attacks={recentAttacks} />
          </div>
        </div>
      </div>
    </div>
  );
}
