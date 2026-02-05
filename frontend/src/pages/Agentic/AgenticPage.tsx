import React, { useState, useEffect, useRef } from 'react';
import { Bot, Target, Zap, Shield, Cpu, Eye, Terminal, Play, CheckCircle2, AlertCircle } from 'lucide-react';

const AgenticPage: React.FC = () => {
  const [goal, setGoal] = useState('');
  const [target, setTarget] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<{msg: string, color: string, time: string, type: string}[]>([]);
  const logEndRef = useRef<HTMLDivElement>(null);

  const [agentsStatus, setAgentsStatus] = useState({
    decision: { status: 'idle', model: 'DeepSeek-R1', icon: Cpu, color: 'text-cyber-blue' },
    vision: { status: 'idle', model: 'Qwen2.5-VL', icon: Eye, color: 'text-cyber-purple' },
    execution: { status: 'idle', model: 'GLM-4.7', icon: Zap, color: 'text-cyber-gold' },
    analysis: { status: 'idle', model: 'Qwen3-235B', icon: Shield, color: 'text-cyber-green' },
  });

  const scrollToBottom = () => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const addLog = (msg: string, type: string = 'info') => {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const colors: Record<string, string> = {
      info: 'text-cyber-gray',
      success: 'text-cyber-green',
      warning: 'text-cyber-gold',
      error: 'text-cyber-red',
      agent: 'text-cyber-blue',
      system: 'text-white font-black'
    };
    setLogs(prev => [...prev, { msg, color: colors[type], time, type }]);
  };

  const handleStartMission = () => {
    if (!goal || !target) return;
    
    setIsRunning(true);
    setLogs([]);
    addLog(`INITIALIZING NEURAL MISSION FOR TARGET: ${target}`, 'system');
    
    setTimeout(() => {
      setAgentsStatus(prev => ({...prev, decision: { ...prev.decision, status: 'processing' }}));
      addLog(`[Decision Agent] Analysing target architecture and decomposing goals...`, 'agent');
    }, 1000);

    setTimeout(() => {
      addLog(`[Decision Agent -> Vision Agent] Requesting visual analysis of web assets...`, 'info');
      setAgentsStatus(prev => ({...prev, vision: { ...prev.vision, status: 'processing' }}));
    }, 2500);

    setTimeout(() => {
      addLog(`[Vision Agent] Visual analysis complete: Identified hidden login portal at /admin-portal.`, 'success');
      setAgentsStatus(prev => ({...prev, vision: { ...prev.vision, status: 'idle' }}));
    }, 4500);

    setTimeout(() => {
      addLog(`[Decision Agent] Strategy finalized: Deploying smart-fuzzer module.`, 'agent');
      setAgentsStatus(prev => ({...prev, execution: { ...prev.execution, status: 'processing' }}));
    }, 6000);

    setTimeout(() => {
      addLog(`[Execution Agent] Running automated penetration sequences...`, 'warning');
    }, 8000);

    setTimeout(() => {
      addLog(`[Analysis Agent] Monitoring traffic for IDS/IPS evasion...`, 'info');
      setAgentsStatus(prev => ({...prev, analysis: { ...prev.analysis, status: 'processing' }}));
    }, 10000);

    setTimeout(() => {
      addLog(`MISSION COMPLETE: VULNERABILITIES DOCUMENTED.`, 'system');
      setIsRunning(false);
      setAgentsStatus(prev => ({
        decision: { ...prev.decision, status: 'idle' },
        vision: { ...prev.vision, status: 'idle' },
        execution: { ...prev.execution, status: 'idle' },
        analysis: { ...prev.analysis, status: 'idle' },
      }));
    }, 15000);
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-1000">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-cyber-blue/20 flex items-center justify-center">
              <Bot className="h-6 w-6 text-cyber-blue" />
            </div>
            <h1 className="text-4xl font-black text-white tracking-tighter">Neural <span className="text-cyber-blue">Commander</span></h1>
          </div>
          <p className="text-cyber-gray max-w-xl font-medium">
            Deploy autonomous agent swarms to perform advanced security reasoning and multi-step execution.
          </p>
        </div>
        <div className="flex items-center gap-4">
           <div className="glass-card px-4 py-2 flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-cyber-green animate-pulse"></div>
              <span className="text-[10px] font-black text-white uppercase tracking-widest">Neural Core: Active</span>
           </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Left: Mission Control */}
        <div className="xl:col-span-2 space-y-8">
          <div className="glass-card p-8 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
              <Target className="w-32 h-32 text-cyber-blue" />
            </div>
            
            <h2 className="text-sm font-black text-white uppercase tracking-widest mb-8 flex items-center gap-2">
              <span className="w-2 h-2 bg-cyber-blue rounded-full"></span>
              Mission Parameters
            </h2>

            <div className="space-y-6 relative z-10">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-cyber-gray uppercase tracking-widest ml-1">Target Vector</label>
                  <input 
                    type="text" 
                    value={target}
                    onChange={(e) => setTarget(e.target.value)}
                    placeholder="e.g. internal-api.secure.mesh"
                    className="cyber-input w-full font-mono text-sm"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-cyber-gray uppercase tracking-widest ml-1">Mission Priority</label>
                  <select className="cyber-input w-full text-sm appearance-none">
                    <option>High Priority (Autonomous)</option>
                    <option>Standard (Supervised)</option>
                    <option>Low (Observation Only)</option>
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-cyber-gray uppercase tracking-widest ml-1">Strategic Objective</label>
                <textarea 
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="Describe the end goal for the agent swarm..."
                  className="cyber-input w-full h-32 resize-none text-sm"
                />
              </div>

              <button 
                onClick={handleStartMission}
                disabled={isRunning || !goal || !target}
                className={`w-full py-4 rounded-2xl font-black text-lg flex items-center justify-center gap-3 transition-all duration-500 ${isRunning ? 'bg-white/5 text-gray-500 cursor-not-allowed' : 'cyber-button'}`}
              >
                {isRunning ? (
                  <>
                    <div className="w-5 h-5 border-2 border-cyber-gray border-t-white rounded-full animate-spin"></div>
                    <span className="tracking-tighter uppercase">Swarm Engaged</span>
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5 fill-current" />
                    <span className="tracking-tighter uppercase">Initiate Autonomous Mission</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Agent Communication Bus */}
          <div className="glass-card bg-cyber-black/80 overflow-hidden flex flex-col h-[450px]">
            <div className="p-6 border-b border-white/5 flex items-center justify-between bg-white/5">
              <div className="flex items-center gap-3">
                <Terminal className="h-4 w-4 text-cyber-blue" />
                <h3 className="text-[10px] font-black text-white uppercase tracking-widest">Neural Communication Bus</h3>
              </div>
              <div className="flex gap-1.5">
                <div className="w-2 h-2 rounded-full bg-cyber-red/30"></div>
                <div className="w-2 h-2 rounded-full bg-cyber-gold/30"></div>
                <div className="w-2 h-2 rounded-full bg-cyber-green/30"></div>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-3 font-mono text-xs md:text-sm custom-scrollbar">
              {logs.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-cyber-gray/30 space-y-2">
                  <Cpu className="h-12 w-12 opacity-10 animate-pulse" />
                  <p className="uppercase tracking-[0.3em] font-black">Awaiting Neural Link</p>
                </div>
              ) : (
                logs.map((log, i) => (
                  <div key={i} className={`flex gap-4 p-3 rounded-xl border border-transparent hover:border-white/5 hover:bg-white/5 transition-all animate-in slide-in-from-left-2 duration-300 ${log.color}`}>
                    <span className="opacity-30 shrink-0">[{log.time}]</span>
                    <span className="leading-relaxed">{log.msg}</span>
                  </div>
                ))
              )}
              <div ref={logEndRef} />
            </div>
          </div>
        </div>

        {/* Right: Swarm Status */}
        <div className="space-y-8">
          <div className="glass-card p-8">
            <h3 className="text-sm font-black text-white uppercase tracking-widest mb-8 flex items-center gap-2">
              <span className="w-2 h-2 bg-cyber-purple rounded-full"></span>
              Swarm Intelligence
            </h3>
            <div className="space-y-6">
              {Object.entries(agentsStatus).map(([name, info]) => (
                <div key={name} className={`p-5 rounded-2xl border transition-all duration-700 ${info.status === 'idle' ? 'bg-white/5 border-white/5' : 'bg-cyber-blue/10 border-cyber-blue/30 shadow-[0_0_20px_rgba(56,189,248,0.1)]'}`}>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-500 ${info.status === 'idle' ? 'bg-white/5 text-cyber-gray' : 'bg-cyber-blue text-cyber-black shadow-lg shadow-cyber-blue/20'}`}>
                        <info.icon className="h-6 w-6" />
                      </div>
                      <div>
                        <p className="font-black text-sm text-white capitalize">{name} Agent</p>
                        <p className="text-[10px] font-bold text-cyber-gray font-mono">{info.model}</p>
                      </div>
                    </div>
                    {info.status === 'processing' ? (
                      <div className="flex items-center gap-1.5">
                        <span className="flex h-2 w-2 rounded-full bg-cyber-green animate-pulse"></span>
                        <span className="text-[10px] font-black text-cyber-green uppercase">Active</span>
                      </div>
                    ) : (
                      <span className="text-[10px] font-black text-cyber-gray uppercase">Standby</span>
                    )}
                  </div>
                  <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-1000 ${info.status === 'idle' ? 'w-0' : 'w-full bg-cyber-blue'}`}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-8 bg-gradient-to-br from-cyber-blue/10 to-transparent">
            <h3 className="text-sm font-black text-white uppercase tracking-widest mb-4">Neural Health</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs text-cyber-gray font-medium">Cognitive Load</span>
                <span className="text-xs text-white font-bold">12%</span>
              </div>
              <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                <div className="h-full w-[12%] bg-cyber-blue"></div>
              </div>
              <div className="flex items-center justify-between pt-2">
                <span className="text-xs text-cyber-gray font-medium">Neural Latency</span>
                <span className="text-xs text-cyber-green font-bold">24ms</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgenticPage;
