import React, { useState, useRef, useEffect } from 'react';
import {
  User,
  LogOut,
  Sparkles,
  Layers,
  Terminal,
  ShieldCheck,
  ChevronDown,
  LogIn,
  Sun,
  Moon,
  Zap
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export const UserProfileMenu: React.FC = () => {
  const { user, stats, isAuthenticated, logout, openAuthModal } = useAuth();
  const { theme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!user) {
    return (
      <button
        onClick={openAuthModal}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#87A7D0] hover:bg-[#7295BF] text-slate-950 text-xs font-bold shadow-md shadow-[#87A7D0]/25 transition cursor-pointer"
      >
        <LogIn className="w-3.5 h-3.5" />
        <span>Sign In</span>
      </button>
    );
  }

  const isGuest = user.provider === 'guest';
  const defaultAvatar = `https://api.dicebear.com/7.x/bottts/svg?seed=${user.email}&backgroundColor=87A7D0,5C85B7`;
  const avatarSrc = user.avatar_url || defaultAvatar;

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Header Profile Trigger Badge */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 p-1 pl-1.5 pr-2.5 rounded-2xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 hover:border-[#87A7D0]/60 dark:hover:border-[#87A7D0]/50 shadow-sm transition-all group cursor-pointer"
      >
        <div className="relative">
          <img
            src={avatarSrc}
            alt={user.full_name}
            className="w-7 h-7 rounded-xl object-cover bg-black/10 dark:bg-white/10 border border-gray-200 dark:border-white/15"
          />
          <span
            className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full border border-white dark:border-[#121218] ${
              isGuest ? 'bg-amber-400' : 'bg-emerald-400'
            }`}
          />
        </div>

        <div className="text-left hidden sm:block">
          <div className="text-xs font-bold text-gray-900 dark:text-white leading-tight flex items-center gap-1">
            <span className="truncate max-w-[110px]">{user.full_name}</span>
            {isGuest && (
              <span className="text-[9px] font-mono px-1 rounded bg-amber-500/15 text-amber-700 dark:text-amber-300">
                GUEST
              </span>
            )}
          </div>
          <div className="text-[10px] text-gray-500 dark:text-gray-400 truncate max-w-[120px]">
            {user.email}
          </div>
        </div>

        <ChevronDown className="w-3.5 h-3.5 text-gray-400 group-hover:text-gray-700 dark:group-hover:text-white transition" />
      </button>

      {/* Profile Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 rounded-2xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 shadow-2xl p-3 z-50 animate-in fade-in zoom-in-95 duration-150">
          {/* User Info Header */}
          <div className="flex items-center gap-3 p-2 rounded-xl bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-white/5 mb-3">
            <img
              src={avatarSrc}
              alt={user.full_name}
              className="w-10 h-10 rounded-xl object-cover border border-gray-200 dark:border-white/20"
            />
            <div className="overflow-hidden">
              <h4 className="font-bold text-xs text-gray-900 dark:text-white truncate">
                {user.full_name}
              </h4>
              <p className="text-[11px] text-gray-500 dark:text-gray-400 truncate">
                {user.email}
              </p>
              <div className="mt-1 flex items-center gap-1">
                <span className="text-[9px] uppercase tracking-wider font-mono px-1.5 py-0.2 rounded bg-[#87A7D0]/15 text-[#3D6390] dark:text-[#87A7D0] font-bold">
                  {user.provider} provider
                </span>
              </div>
            </div>
          </div>

          {/* User Stats Card */}
          <div className="grid grid-cols-3 gap-2 p-2.5 rounded-xl bg-gray-50 dark:bg-white/5 border border-gray-100 dark:border-white/5 mb-3 text-center">
            <div>
              <div className="text-[10px] text-gray-500 dark:text-gray-400">Migrations</div>
              <div className="text-xs font-bold text-[#3D6390] dark:text-[#87A7D0] font-mono">
                {stats?.saved_migrations ?? 20}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-gray-500 dark:text-gray-400">Benchmarks</div>
              <div className="text-xs font-bold text-[#5C85B7] dark:text-[#A2BFE3] font-mono">
                {stats?.benchmark_runs ?? 3}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-gray-500 dark:text-gray-400">Pass Rate</div>
              <div className="text-xs font-bold text-emerald-600 dark:text-emerald-400 font-mono">
                {stats?.success_rate ?? 100}%
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-1 text-xs">
            {isGuest ? (
              <button
                onClick={() => { setIsOpen(false); openAuthModal(); }}
                className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-[#3D6390] dark:text-[#87A7D0] bg-[#87A7D0]/10 hover:bg-[#87A7D0]/20 font-semibold transition cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-[#D4AF37]" />
                  <span>Connect Google / Full Account</span>
                </div>
                <Zap className="w-3.5 h-3.5" />
              </button>
            ) : null}

            {/* Quick Theme Switcher */}
            <div className="flex items-center justify-between px-3 py-2 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/5 transition">
              <span className="text-[11px] font-medium">Theme Mode</span>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setTheme('light')}
                  className={`p-1 rounded-lg ${theme === 'light' ? 'bg-[#87A7D0]/20 text-[#3D6390]' : 'text-gray-400'}`}
                  title="Light"
                >
                  <Sun className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setTheme('dark')}
                  className={`p-1 rounded-lg ${theme === 'dark' ? 'bg-[#87A7D0]/20 text-[#87A7D0]' : 'text-gray-400'}`}
                  title="Dark"
                >
                  <Moon className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Sign Out / Switch User */}
            <button
              onClick={() => { setIsOpen(false); logout(); }}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/20 font-medium transition"
            >
              <LogOut className="w-4 h-4" />
              <span>{isGuest ? 'Reset Guest State' : 'Sign Out'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
