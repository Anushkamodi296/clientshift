import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Layers,
  Activity,
  Sparkles,
  Clock,
  Terminal
} from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { UserProfileMenu } from './UserProfileMenu';
import type { SystemHealth } from '../services/api';

interface NavbarProps {
  activeTab: 'dashboard' | 'workspace' | 'benchmark';
  setActiveTab: (tab: 'dashboard' | 'workspace' | 'benchmark') => void;
  systemHealth: SystemHealth | null;
  onOpenNilo: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  systemHealth,
  onOpenNilo
}) => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour >= 5 && hour < 12) return 'Good morning, Engineer ☀️';
    if (hour >= 12 && hour < 17) return 'Good afternoon, Engineer ⚡';
    if (hour >= 17 && hour < 22) return 'Good evening, Architect 🌙';
    return 'Burning the midnight oil, Visionary 🚀';
  };

  const formatLocalTime = () => {
    return currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const formatUtcTime = () => {
    return currentTime.toISOString().substring(11, 19) + ' UTC';
  };

  return (
    <header className="sticky top-0 z-40 border-b border-gray-200 dark:border-white/10 bg-[#FBF9F5]/90 dark:bg-[#0B0C10]/90 backdrop-blur-xl transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Dynamic Greeting */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#87A7D0] via-[#5C85B7] to-[#B3CEEC] p-0.5 shadow-md shadow-[#87A7D0]/25">
                <div className="w-full h-full rounded-[10px] bg-[#0B0C10] flex items-center justify-center">
                  <Cpu className="w-5 h-5 text-[#87A7D0]" />
                </div>
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-extrabold text-base tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-[#3D6390] via-[#5C85B7] to-[#87A7D0] dark:from-[#87A7D0] dark:via-white dark:to-[#B3CEEC]">
                    CLIENTSHIFT
                  </span>
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-black/5 dark:bg-white/10 text-gray-600 dark:text-gray-300">
                    v1.0
                  </span>
                </div>
                <div className="text-[11px] font-medium text-[#3D6390] dark:text-[#87A7D0] flex items-center gap-1">
                  <span>{getGreeting()}</span>
                </div>
              </div>
            </div>

            {/* Live Ticking Clock Badge */}
            <div className="hidden lg:flex items-center gap-2 pl-3 border-l border-gray-200 dark:border-white/10 text-xs font-mono text-gray-500 dark:text-gray-400">
              <Clock className="w-3.5 h-3.5 text-[#5C85B7] dark:text-[#87A7D0]" />
              <span>{formatLocalTime()}</span>
              <span className="text-gray-300 dark:text-gray-600">•</span>
              <span className="text-[11px] text-gray-400 dark:text-gray-500">{formatUtcTime()}</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center gap-1 bg-gray-100 dark:bg-white/5 p-1 rounded-xl border border-gray-200 dark:border-white/10">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'dashboard'
                  ? 'bg-[#87A7D0] text-slate-950 font-bold dark:bg-[#87A7D0]/25 dark:text-[#87A7D0] dark:border dark:border-[#87A7D0]/50 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              Dashboard
            </button>

            <button
              onClick={() => setActiveTab('workspace')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'workspace'
                  ? 'bg-[#87A7D0] text-slate-950 font-bold dark:bg-[#87A7D0]/25 dark:text-[#87A7D0] dark:border dark:border-[#87A7D0]/50 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              Migration Workspace
            </button>

            <button
              onClick={() => setActiveTab('benchmark')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === 'benchmark'
                  ? 'bg-[#87A7D0] text-slate-950 font-bold dark:bg-[#87A7D0]/25 dark:text-[#87A7D0] dark:border dark:border-[#87A7D0]/50 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              Benchmark Explorer
            </button>
          </nav>

          {/* Right Controls: Model Status, Nilo AI Trigger, Theme Toggle & User Profile */}
          <div className="flex items-center gap-2.5">
            {/* Model Status Indicator */}
            <div
              className={`hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
                systemHealth?.is_ollama_online
                  ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/30'
                  : 'bg-[#87A7D0]/10 dark:bg-white/5 text-[#3D6390] dark:text-[#87A7D0] border-[#87A7D0]/30'
              }`}
              title={systemHealth?.provider || 'AI Engine'}
            >
              <div className="w-2 h-2 rounded-full bg-current animate-pulse" />
              <span>
                {systemHealth?.is_ollama_online ? 'Ollama Active' : 'Deterministic Mock Adapter'}
              </span>
            </div>

            {/* Nilo Trigger Button */}
            <button
              onClick={onOpenNilo}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-[#6087B8] to-[#87A7D0] text-slate-950 font-bold text-xs shadow-md shadow-[#87A7D0]/25 hover:opacity-95 active:scale-95 transition-all cursor-pointer"
              title="Open Nilo AI Migration Specialist (Ctrl+K)"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Ask Nilo</span>
              <kbd className="hidden lg:inline text-[10px] bg-black/10 px-1 py-0.5 rounded font-mono">⌘K</kbd>
            </button>

            {/* Tri-Mode Theme Toggle */}
            <ThemeToggle />

            {/* User Profile Badge & Dropdown */}
            <UserProfileMenu />
          </div>
        </div>
      </div>
    </header>
  );
};
