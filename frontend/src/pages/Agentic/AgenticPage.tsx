/**
 * SecureRedLab v2.0 - Agentic Control Center
 * =========================================
 * صفحه کنترل مرکزی سیستم ایجنتیک (Multi-Agent)
 */

import React, { useState, useEffect, useRef } from 'react';

const AgenticPage: React.FC = () => {
  const [goal, setGoal] = useState('');
  const [target, setTarget] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<{msg: string, color: string, time: string}[]>([]);
  const logEndRef = useRef<HTMLDivElement>(null);

  const [agentsStatus, setAgentsStatus] = useState({
    decision: { status: 'idle', model: 'DeepSeek-R1', load: 0 },
    execution: { status: 'idle', model: 'GLM-4.7', load: 0 },
    analysis: { status: 'idle', model: 'Qwen3-235B', load: 0 },
    vision: { status: 'idle', model: 'Qwen2.5-VL', load: 0 },
  });

  const scrollToBottom = () => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const addLog = (msg: string, color: string = 'text-gray-400') => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { msg, color, time }]);
  };

  const handleStartMission = () => {
    if (!goal || !target) {
      alert('لطفاً هدف و آدرس هدف را وارد کنید.');
      return;
    }
    
    setIsRunning(true);
    setLogs([]);
    addLog(`[SYSTEM] شروع ماموریت ایجنتیک برای هدف: ${target}`, 'text-blue-500 font-bold');
    
    // شبیه‌سازی گام‌به‌گام ایجنت‌ها
    setTimeout(() => {
      setAgentsStatus(prev => ({...prev, decision: { ...prev.decision, status: 'processing', load: 85 }}));
      addLog(`[Decision Agent] در حال تحلیل معماری هدف و استخراج بردارهای حمله...`, 'text-blue-400');
    }, 1000);

    setTimeout(() => {
      addLog(`[Decision Agent -> Vision Agent] درخواست تحلیل اسکرین‌شات‌های پورت‌های وب ارسال شد.`, 'text-purple-400');
      setAgentsStatus(prev => ({...prev, vision: { ...prev.vision, status: 'processing', load: 40 }}));
    }, 2500);

    setTimeout(() => {
      addLog(`[Vision Agent] تحلیل بصری کامل شد: پنل مدیریت وردپرس در پورت 8080 شناسایی شد.`, 'text-green-400');
      setAgentsStatus(prev => ({...prev, vision: { ...prev.vision, status: 'idle', load: 0 }}));
    }, 4500);

    setTimeout(() => {
      addLog(`[Decision Agent] استراتژی نهایی: اجرای Brute-force روی wp-login با استفاده از دیتابیس اختصاصی.`, 'text-blue-400');
      setAgentsStatus(prev => ({...prev, execution: { ...prev.execution, status: 'processing', load: 95 }}));
    }, 6000);

    setTimeout(() => {
      addLog(`[Execution Agent] در حال اجرای ماژول هایدرای ایجنتیک...`, 'text-yellow-400');
    }, 8000);

    setTimeout(() => {
      addLog(`[Analysis Agent] در حال مانیتورینگ ترافیک برای جلوگیری از شناسایی توسط IDS/IPS...`, 'text-cyan-400');
      setAgentsStatus(prev => ({...prev, analysis: { ...prev.analysis, status: 'processing', load: 30 }}));
    }, 10000);

    setTimeout(() => {
      addLog(`[SYSTEM] ماموریت با موفقیت به پایان رسید. گزارش نهایی در بخش Reports آماده است.`, 'text-green-500 font-bold');
      setIsRunning(false);
      setAgentsStatus({
        decision: { status: 'idle', model: 'DeepSeek-R1', load: 0 },
        execution: { status: 'idle', model: 'GLM-4.7', load: 0 },
        analysis: { status: 'idle', model: 'Qwen3-235B', load: 0 },
        vision: { status: 'idle', model: 'Qwen2.5-VL', load: 0 },
      });
    }, 15000);
  };

  return (
    <div className="p-6 space-y-6 bg-gray-900 text-white min-h-screen" dir="rtl">
      <header className="flex justify-between items-center border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-l from-blue-400 to-cyan-300 bg-clip-text text-transparent">مرکز کنترل ایجنتیک v2.0</h1>
          <p className="text-gray-500 text-sm mt-1">مدیریت هوشمند حملات زنجیره‌ای با استفاده از Multi-Agent System</p>
        </div>
        <div className="flex items-center space-x-4 space-x-reverse">
          <div className="flex items-center gap-2 px-3 py-1 bg-gray-800 border border-gray-700 rounded-full">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-green-400 text-xs">هسته هوشمند فعال</span>
          </div>
        </div>
      </header>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* بخش تعریف ماموریت */}
        <div className="lg:col-span-2 bg-gray-800/50 p-6 rounded-xl border border-gray-700 shadow-xl backdrop-blur-sm">
          <h2 className="text-xl font-semibold mb-6 text-gray-200 flex items-center gap-2">
            <span className="w-2 h-6 bg-blue-500 rounded-full"></span>
            تعریف ماموریت عملیاتی
          </h2>
          <div className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-2 uppercase tracking-wider">آدرس هدف (IP/Domain)</label>
                <input 
                  type="text" 
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  placeholder="e.g. 10.0.0.15 or target.local"
                  className="w-full bg-gray-900/50 border border-gray-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500/50 outline-none text-white transition-all font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-2 uppercase tracking-wider">اولویت عملیات</label>
                <select className="w-full bg-gray-900/50 border border-gray-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500/50 outline-none text-white transition-all">
                  <option>بحرانی (Critical)</option>
                  <option>بالا (High)</option>
                  <option>متوسط (Medium)</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-2 uppercase tracking-wider">هدف نهایی (Mission Goal)</label>
              <textarea 
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="هدف خود را شرح دهید... (مثلاً: نفوذ به دیتابیس و بررسی آسیب‌پذیری‌های امنیتی)"
                className="w-full bg-gray-900/50 border border-gray-700 rounded-lg px-4 py-3 h-32 focus:ring-2 focus:ring-blue-500/50 outline-none text-white transition-all resize-none"
              />
            </div>
            <button 
              onClick={handleStartMission}
              disabled={isRunning}
              className={`w-full py-4 rounded-xl font-bold text-lg transition-all transform active:scale-95 ${isRunning ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 shadow-lg shadow-blue-900/20'}`}
            >
              {isRunning ? (
                <div className="flex items-center justify-center gap-3">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>در حال پردازش زنجیره حمله...</span>
                </div>
              ) : 'شروع عملیات هوشمند ایجنتیک'}
            </button>
          </div>
        </div>

        {/* وضعیت Agents */}
        <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 shadow-xl backdrop-blur-sm">
          <h2 className="text-xl font-semibold mb-6 text-gray-200 flex items-center gap-2">
            <span className="w-2 h-6 bg-purple-500 rounded-full"></span>
            وضعیت هوش مصنوعی
          </h2>
          <div className="space-y-4">
            {Object.entries(agentsStatus).map(([name, info]) => (
              <div key={name} className={`p-4 rounded-xl border transition-all duration-500 ${info.status === 'idle' ? 'bg-gray-900/30 border-gray-800' : 'bg-blue-900/20 border-blue-500/50 shadow-lg shadow-blue-500/5'}`}>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${info.status === 'idle' ? 'bg-gray-800 text-gray-500' : 'bg-blue-600 text-white'}`}>
                      {name[0].toUpperCase()}
                    </div>
                    <div>
                      <p className="font-bold capitalize text-sm">{name} Agent</p>
                      <p className="text-[10px] text-gray-500 font-mono">{info.model}</p>
                    </div>
                  </div>
                  <span className={`text-[10px] px-2 py-1 rounded-full font-bold uppercase ${info.status === 'idle' ? 'bg-gray-800 text-gray-500' : 'bg-green-500/20 text-green-400 animate-pulse'}`}>
                    {info.status === 'idle' ? 'Standby' : 'Active'}
                  </span>
                </div>
                <div className="w-full bg-gray-800 h-1 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-1000 ${info.status === 'idle' ? 'bg-gray-700 w-0' : 'bg-blue-500'}`}
                    style={{ width: `${info.load}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* بخش لاگ‌های ایجنتیک */}
      <section className="bg-gray-950 p-6 rounded-2xl border border-gray-800 shadow-2xl relative overflow-hidden group">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500/50 to-transparent opacity-50"></div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-gray-400 font-mono text-sm flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></span>
            AGENT_COMMUNICATION_BUS_v2.0
          </h3>
          <div className="flex gap-1">
            <div className="w-3 h-3 rounded-full bg-red-500/20"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500/20"></div>
            <div className="w-3 h-3 rounded-full bg-green-500/20"></div>
          </div>
        </div>
        <div className="font-mono text-xs md:text-sm h-80 overflow-y-auto space-y-2 custom-scrollbar pr-2">
          {logs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-700 opacity-50">
              <p className="">در انتظار شروع ماموریت...</p>
              <p className="text-[10px]">نودهای ارتباطی در وضعیت Listening هستند</p>
            </div>
          ) : (
            logs.map((log, i) => (
              <div key={i} className={`flex gap-3 border-l-2 border-gray-800 pl-3 py-1 hover:bg-white/5 transition-colors rounded-r-lg ${log.color}`}>
                <span className="text-gray-600 shrink-0">[{log.time}]</span>
                <span className="break-all leading-relaxed">{log.msg}</span>
              </div>
            ))
          )}
          <div ref={logEndRef} />
        </div>
      </section>
    </div>
  );
};

export default AgenticPage;
