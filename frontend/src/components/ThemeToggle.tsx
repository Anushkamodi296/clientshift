import React from 'react';
import { Sun, Moon, Sparkles } from 'lucide-react';
import { useTheme, ThemeMode } from '../context/ThemeContext';

export const ThemeToggle: React.FC = () => {
  const { theme, resolvedTheme, setTheme } = useTheme();

  return (
    <div className="flex items-center gap-1 p-1 rounded-xl bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10 text-xs">
      <button
        onClick={() => setTheme('dark')}
        title="Deep Midnight Obsidian (Dark)"
        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
          theme === 'dark'
            ? 'bg-[#87A7D0]/20 text-[#87A7D0] border border-[#87A7D0]/40 shadow-sm font-bold'
            : 'text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200'
        }`}
      >
        <Moon className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Dark</span>
      </button>

      <button
        onClick={() => setTheme('light')}
        title="Cream Vanilla & Soft Steel Blue (Light)"
        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
          theme === 'light'
            ? 'bg-[#87A7D0]/25 text-[#3D6390] dark:text-[#87A7D0] border border-[#87A7D0]/40 shadow-sm font-bold'
            : 'text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200'
        }`}
      >
        <Sun className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Light</span>
      </button>

      <button
        onClick={() => setTheme('system_auto')}
        title="Dynamic Day/Night Sync (06:00-18:59 Light, 19:00-05:59 Dark)"
        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
          theme === 'system_auto'
            ? 'bg-[#87A7D0]/20 text-[#3D6390] dark:text-[#87A7D0] border border-[#87A7D0]/40 shadow-sm font-bold'
            : 'text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200'
        }`}
      >
        <Sparkles className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Auto-Sync</span>
      </button>
    </div>
  );
};
