import React, { useState, useEffect, useRef } from 'react';
import { Bot, Send, Terminal, CheckCircle2, Circle, Clock, Play, Shield, Target, Cpu, ChevronRight } from 'lucide-react';

interface Task {
  id: number;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
}

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  time: string;
}

const AgenticPage: React.FC = () => {
  const [goal, setGoal] = useState('');
  const [target, setTarget] = useState('');
  const [isStarted, setIsStarted] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [plan, setPlan] = useState<Task[]>([]);
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (content: string, role: 'user' | 'assistant' | 'system' = 'assistant') => {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setMessages(prev => [...prev, { role, content, time }]);
  };

  const handleStartMission = () => {
    if (!goal || !target) return;
    
    setIsStarted(true);
    setIsRunning(true);
    
    // شبیه‌سازی Manus: اول تحلیل و ساخت پلن
    addMessage(`Initializing mission for ${target}. Analyzing goal: "${goal}"...`, 'system');
    
    setTimeout(() => {
      const initialPlan: Task[] = [
        { id: 1, title: 'Target Reconnaissance', description: `Gathering intel on ${target}`, status: 'in_progress' },
        { id: 2, title: 'Vulnerability Analysis', description: 'Scanning for open vectors', status: 'pending' },
        { id: 3, title: 'Exploitation Simulation', description: 'Executing controlled payload', status: 'pending' },
        { id: 4, title: 'Data Impact Assessment', description: 'Analyzing potential data leak', status: 'pending' },
        { id: 5, title: 'Final Security Report', description: 'Generating comprehensive findings', status: 'pending' },
      ];
      setPlan(initialPlan);
      addMessage(`I've analyzed the objective. Here is my action plan to secure/analyze ${target}. I'm starting with the reconnaissance phase.`, 'assistant');
    }, 1500);

    // شبیه‌سازی اجرای تسک‌ها
    let currentTask = 1;
    const interval = setInterval(() => {
      if (currentTask > 5) {
        clearInterval(interval);
        setIsRunning(false);
        addMessage("Mission successfully completed. All security vectors have been analyzed and documented.", "assistant");
        return;
      }

      setPlan(prev => prev.map(t => {
        if (t.id === currentTask) return { ...t, status: 'completed' };
        if (t.id === currentTask + 1) return { ...t, status: 'in_progress' };
        return t;
      }));

      if (currentTask === 1) addMessage("Reconnaissance complete. Found 3 open ports. Moving to vulnerability analysis.", "assistant");
      if (currentTask === 2) addMessage("Vulnerability found: CVE-2023-XXXX. Simulating exploitation in a sandbox environment.", "assistant");
      if (currentTask === 3) addMessage("Exploitation successful. Accessing simulated database layer...", "assistant");
      
      currentTask++;
    }, 5000);
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    addMessage(input, 'user');
    const userMsg = input.toLowerCase();
    setInput('');

    setTimeout(() => {
      if (userMsg.includes('status') || userMsg.includes('چطوری')) {
        addMessage("All systems are operational. I am currently executing the defined security plan.", 'assistant');
      } else {
        addMessage("I understand. I will incorporate this into my ongoing analysis of the target environment.", 'assistant');
      }
    }, 1000);
  };

  return (
    <div className="flex h-[calc(100vh-120px)] gap-6 animate-in fade-in duration-700">
      {/* Left Side: Chat Interface (The "Manus" experience) */}
      <div className="flex-1 flex flex-col glass-card overflow-hidden">
        <div className="p-4 border-b border-white/5 bg-white/5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-cyber-blue/20 flex items-center justify-center">
              <Bot className="h-5 w-5 text-cyber-blue" />
            </div>
            <div>
              <h2 className="text-sm font-black text-white uppercase tracking-widest">Agentic Chat</h2>
              <p className="text-[10px] text-cyber-green font-bold">REASONING ENGINE ACTIVE</p>
            </div>
          </div>
          <div className="flex gap-1.5">
            <div className="w-2 h-2 rounded-full bg-cyber-red/20"></div>
            <div className="w-2 h-2 rounded-full bg-cyber-gold/20"></div>
            <div className="w-2 h-2 rounded-full bg-cyber-green/20"></div>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          {!isStarted ? (
            <div className="h-full flex flex-col items-center justify-center space-y-8 max-w-md mx-auto text-center">
              <div className="relative">
                <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-cyber-blue/20 to-cyber-purple/20 flex items-center justify-center border border-white/10">
                  <Shield className="h-12 w-12 text-cyber-blue animate-pulse" />
                </div>
                <div className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-cyber-green border-4 border-cyber-black flex items-center justify-center">
                  <Zap className="h-4 w-4 text-white" />
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="text-2xl font-black text-white tracking-tighter">Initiate Neural Mission</h3>
                <div className="space-y-4">
                  <input 
                    type="text" 
                    placeholder="Target (IP/Domain)"
                    value={target}
                    onChange={(e) => setTarget(e.target.value)}
                    className="cyber-input w-full"
                  />
                  <textarea 
                    placeholder="What is your objective?"
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    className="cyber-input w-full h-24 resize-none"
                  />
                  <button 
                    onClick={handleStartMission}
                    className="cyber-button w-full py-4 uppercase tracking-widest text-sm"
                  >
                    Deploy Agent Swarm
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2 duration-300`}>
                  <div className={`max-w-[80%] flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-lg shrink-0 flex items-center justify-center border ${msg.role === 'user' ? 'bg-cyber-purple/20 border-cyber-purple/30' : msg.role === 'system' ? 'bg-white/5 border-white/10' : 'bg-cyber-blue/20 border-cyber-blue/30'}`}>
                      {msg.role === 'user' ? <Target className="h-4 w-4 text-cyber-purple" /> : <Bot className="h-4 w-4 text-cyber-blue" />}
                    </div>
                    <div className={`p-4 rounded-2xl border ${msg.role === 'user' ? 'bg-cyber-purple/10 border-cyber-purple/20 text-white' : msg.role === 'system' ? 'bg-white/5 border-transparent text-cyber-gray italic text-xs' : 'bg-white/5 border-white/10 text-gray-200'}`}>
                      <p className="text-sm leading-relaxed">{msg.content}</p>
                      <p className="text-[10px] opacity-30 mt-2 font-mono">{msg.time}</p>
                    </div>
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <form onSubmit={handleSendMessage} className="p-4 bg-white/5 border-t border-white/5">
          <div className="relative">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={!isStarted}
              placeholder={isStarted ? "Ask the agent anything..." : "Waiting for mission start..."}
              className="cyber-input w-full pr-12 disabled:opacity-50"
            />
            <button 
              type="submit"
              disabled={!isStarted || !input.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-lg bg-cyber-blue text-cyber-black hover:scale-110 transition-transform disabled:opacity-50 disabled:scale-100"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </form>
      </div>

      {/* Right Side: Task Plan (The Manus logic) */}
      <div className="w-96 flex flex-col gap-6">
        <div className="glass-card flex-1 flex flex-col overflow-hidden">
          <div className="p-6 border-b border-white/5 bg-white/5">
            <h3 className="text-sm font-black text-white uppercase tracking-widest flex items-center gap-2">
              <Cpu className="h-4 w-4 text-cyber-blue" />
              Task Execution Plan
            </h3>
          </div>
          <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
            {!isStarted ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4 opacity-30">
                <Clock className="h-12 w-12" />
                <p className="text-xs font-bold uppercase tracking-widest">Awaiting Objectives</p>
              </div>
            ) : (
              plan.map((task, i) => (
                <div key={task.id} className={`p-4 rounded-xl border transition-all duration-500 ${task.status === 'completed' ? 'bg-cyber-green/5 border-cyber-green/20 opacity-60' : task.status === 'in_progress' ? 'bg-cyber-blue/10 border-cyber-blue/40 shadow-lg shadow-cyber-blue/5' : 'bg-white/5 border-white/5'}`}>
                  <div className="flex items-start gap-3">
                    <div className="mt-1">
                      {task.status === 'completed' ? <CheckCircle2 className="h-4 w-4 text-cyber-green" /> : task.status === 'in_progress' ? <div className="w-4 h-4 border-2 border-cyber-blue border-t-transparent rounded-full animate-spin" /> : <Circle className="h-4 w-4 text-cyber-gray" />}
                    </div>
                    <div>
                      <h4 className={`text-xs font-black uppercase tracking-tight ${task.status === 'in_progress' ? 'text-cyber-blue' : 'text-white'}`}>{task.title}</h4>
                      <p className="text-[10px] text-cyber-gray mt-1 leading-relaxed">{task.description}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Swarm Metrics */}
        <div className="glass-card p-6 space-y-4">
          <h3 className="text-[10px] font-black text-cyber-gray uppercase tracking-[0.2em]">Neural Swarm Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between text-[10px] font-bold">
              <span className="text-cyber-gray uppercase">Reasoning Load</span>
              <span className="text-white">{isRunning ? '78%' : '0%'}</span>
            </div>
            <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
              <div className={`h-full bg-cyber-blue transition-all duration-1000 ${isRunning ? 'w-[78%]' : 'w-0'}`}></div>
            </div>
            <div className="flex justify-between text-[10px] font-bold pt-1">
              <span className="text-cyber-gray uppercase">Active Nodes</span>
              <span className="text-cyber-green">{isRunning ? '128/128' : '0/128'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgenticPage;
