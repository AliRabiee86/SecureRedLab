/**
 * SecureRedLab v2.0 - Agentic Control Center
 * =========================================
 * صفحه کنترل مرکزی سیستم ایجنتیک (Multi-Agent)
 * 
 * این صفحه به کاربر اجازه می‌دهد:
 * 1. وضعیت لحظه‌ای تمام Agents (Decision, Execution, Analysis, Vision) را مشاهده کند.
 * 2. ماموریت‌های جدید (Goals) برای سیستم تعریف کند.
 * 3. زنجیره حملات طراحی شده توسط Decision Agent را بررسی و تایید کند.
 * 4. لاگ‌های ارتباطی بین Agents را به صورت Real-time مشاهده کند.
 */

import React, { useState } from 'react';

const AgenticPage: React.FC = () => {
  const [goal, setGoal] = useState('');
  const [target, setTarget] = useState('');
  const [isRunning, setIsRunning] = useState(false);

  // وضعیت Agents
  const [agentsStatus] = useState({
    decision: { status: 'idle', model: 'DeepSeek-R1', load: 0 },
    execution: { status: 'idle', model: 'GLM-4.7', load: 0 },
    analysis: { status: 'idle', model: 'Qwen3-235B', load: 0 },
    vision: { status: 'idle', model: 'Qwen2.5-VL', load: 0 },
  });

  const handleStartMission = () => {
    if (!goal || !target) {
      alert('لطفاً هدف و آدرس هدف را وارد کنید.');
      return;
    }
    setIsRunning(true);
    console.log('شروع ماموریت ایجنتیک برای:', target, 'با هدف:', goal);
  };

  return (
    <div className="p-6 space-y-6 bg-gray-900 text-white min-h-screen" dir="rtl">
      <header className="flex justify-between items-center border-b border-gray-700 pb-4">
        <h1 className="text-3xl font-bold text-blue-400">مرکز کنترل ایجنتیک v2.0</h1>
        <div className="flex items-center space-x-4 space-x-reverse">
          <span className="px-3 py-1 bg-green-900 text-green-300 rounded-full text-sm">سیستم آنلاین (آفلاین محلی)</span>
        </div>
      </header>

      {/* بخش تعریف ماموریت */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
          <h2 className="text-xl font-semibold mb-4 text-gray-200">تعریف ماموریت جدید</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">آدرس هدف (IP/Domain)</label>
              <input 
                type="text" 
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="مثلاً: 192.168.1.100"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">هدف نهایی (Goal)</label>
              <textarea 
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="مثلاً: شناسایی آسیب‌پذیری‌های SQL Injection و استخراج نام جداول"
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 h-24 focus:ring-2 focus:ring-blue-500 outline-none text-white"
              />
            </div>
            <button 
              onClick={handleStartMission}
              disabled={isRunning}
              className={`w-full py-3 rounded-lg font-bold text-lg transition-all ${isRunning ? 'bg-gray-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 shadow-blue-900/20 shadow-xl'}`}
            >
              {isRunning ? 'در حال اجرای ماموریت...' : 'شروع عملیات هوشمند'}
            </button>
          </div>
        </div>

        {/* وضعیت Agents */}
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
          <h2 className="text-xl font-semibold mb-4 text-gray-200">وضعیت Agents</h2>
          <div className="space-y-4">
            {Object.entries(agentsStatus).map(([name, info]) => (
              <div key={name} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg border border-gray-600">
                <div>
                  <p className="font-bold capitalize text-blue-300">{name} Agent</p>
                  <p className="text-xs text-gray-400">{info.model}</p>
                </div>
                <div className="text-right">
                  <span className={`text-xs px-2 py-1 rounded ${info.status === 'idle' ? 'bg-gray-600 text-gray-300' : 'bg-green-900 text-green-300'}`}>
                    {info.status === 'idle' ? 'آماده باش' : 'در حال پردازش'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* بخش لاگ‌های ایجنتیک */}
      <section className="bg-black p-4 rounded-xl border border-gray-700 font-mono text-sm h-64 overflow-y-auto shadow-inner">
        <h3 className="text-gray-500 mb-2 border-b border-gray-800 pb-1">Agent Communication Bus (Real-time)</h3>
        <div className="space-y-1">
          <p className="text-gray-500">[SYSTEM] باس ارتباطی آماده دریافت پیام است...</p>
          {isRunning && (
            <>
              <p className="text-blue-400">[Decision Agent] در حال تحلیل هدف: {target}</p>
              <p className="text-purple-400">[Decision Agent -&gt; Goal Decomposer] درخواست تجزیه هدف ارسال شد.</p>
              <p className="text-green-400">[Goal Decomposer] هدف به 3 زیر-هدف تقسیم شد.</p>
              <p className="text-yellow-400">[Execution Agent] در حال آماده‌سازی ابزارهای Nmap و Metasploit...</p>
            </>
          )}
        </div>
      </section>
    </div>
  );
};

export default AgenticPage;
