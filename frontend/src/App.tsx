import React, { useState, useEffect } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { MigrationWorkspace } from './pages/MigrationWorkspace';
import { BenchmarkExplorer } from './pages/BenchmarkExplorer';
import { NiloChatbot } from './components/NiloChatbot';
import { NiloFloatingOrb } from './components/NiloFloatingOrb';
import { AuthModal } from './components/AuthModal';
import { api } from './services/api';
import type { SystemHealth } from './services/api';

export const AppContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'workspace' | 'benchmark'>('workspace');
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [isNiloOpen, setIsNiloOpen] = useState(false);

  // Active workspace state shared for Nilo contextual diagnostics
  const [workspaceCode, setWorkspaceCode] = useState<string>('');
  const [workspaceTest, setWorkspaceTest] = useState<string>('');
  const [workspaceError, setWorkspaceError] = useState<string>('');

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const health = await api.getHealth();
        setSystemHealth(health);
      } catch (err) {
        console.error('Health check failed:', err);
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Global hotkey: Cmd+K / Ctrl+K to toggle Nilo AI Assistant
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsNiloOpen(prev => !prev);
      } else if (e.key === 'Escape' && isNiloOpen) {
        setIsNiloOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isNiloOpen]);

  const handleNavigateToWorkspaceWithPreset = (presetCode?: string, presetTest?: string) => {
    if (presetCode) setWorkspaceCode(presetCode);
    if (presetTest) setWorkspaceTest(presetTest);
    setActiveTab('workspace');
  };

  const handleAskNiloWithError = (errorTrace: string) => {
    setWorkspaceError(errorTrace);
    setIsNiloOpen(true);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FBF9F5] dark:bg-[#0B0C10] text-[#1E1B4B] dark:text-[#F3F4F6] transition-colors selection:bg-[#87A7D0]/40 selection:text-slate-900 dark:selection:text-white">
      {/* Dynamic Top Navigation Bar with User Profile */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemHealth={systemHealth}
        onOpenNilo={() => setIsNiloOpen(true)}
      />

      {/* Main Page Area */}
      <main className="flex-1">
        {activeTab === 'dashboard' && (
          <Dashboard
            onNavigateToWorkspace={handleNavigateToWorkspaceWithPreset}
            onNavigateToBenchmark={() => setActiveTab('benchmark')}
            systemHealth={systemHealth}
          />
        )}

        {activeTab === 'workspace' && (
          <MigrationWorkspace
            initialCode={workspaceCode || undefined}
            initialTest={workspaceTest || undefined}
            onAskNilo={handleAskNiloWithError}
          />
        )}

        {activeTab === 'benchmark' && (
          <BenchmarkExplorer
            onLoadCaseInWorkspace={handleNavigateToWorkspaceWithPreset}
          />
        )}
      </main>

      {/* 3D Holographic Sphere Floating Action Button for Nilo AI Assistant */}
      <NiloFloatingOrb
        onClick={() => setIsNiloOpen(true)}
        hasActiveError={!!workspaceError}
      />

      {/* Floating Side-Drawer Nilo Assistant Modal */}
      <NiloChatbot
        isOpen={isNiloOpen}
        onClose={() => setIsNiloOpen(false)}
        activeCode={workspaceCode}
        activeError={workspaceError}
        activeStage={activeTab}
      />

      {/* Authentication Gateway Modal (Sign In / Sign Up / Google OAuth / Guest) */}
      <AuthModal />

      {/* Global Minimal Footer */}
      <footer className="border-t border-gray-200 dark:border-white/10 py-4 px-6 text-center text-xs text-gray-500 dark:text-gray-400 bg-white/60 dark:bg-black/20">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span className="font-medium">ClientShift v1.2 • Deterministic AI Code Migration Engine & Benchmark Platform</span>
          <span className="font-mono text-[11px] text-gray-400 dark:text-gray-500">
            Python AST + Pytest Sandbox + Qwen2.5-Coder / Zero-Cost Adapter
          </span>
        </div>
      </footer>
    </div>
  );
};

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}
