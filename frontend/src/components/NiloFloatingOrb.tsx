import React from 'react';
import { Bot, Sparkles } from 'lucide-react';

interface NiloFloatingOrbProps {
  onClick: () => void;
  hasActiveError?: boolean;
}

export const NiloFloatingOrb: React.FC<NiloFloatingOrbProps> = ({ onClick, hasActiveError }) => {
  return (
    <div className="fixed bottom-6 right-6 z-40 group select-none">
      <button
        onClick={onClick}
        className="relative flex items-center gap-3 pl-3 pr-4 py-2.5 rounded-full bg-white/90 dark:bg-[#121218]/90 border border-[#87A7D0]/40 dark:border-white/15 hover:border-[#87A7D0] shadow-2xl backdrop-blur-xl hover:scale-105 active:scale-95 transition-all cursor-pointer card-3d"
        title="Open Nilo AI DevOps Specialist (Ctrl+K)"
      >
        {/* Multi-Ring Rotating 3D Holographic Sphere Container */}
        <div className="relative w-9 h-9 flex items-center justify-center">
          {/* Outer Pulsing Aura */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-[#87A7D0] via-[#5C85B7] to-[#B3CEEC] blur-md opacity-75 group-hover:opacity-100 transition duration-300 nilo-3d-orb" />

          {/* Outer Rotating Gyro Ring */}
          <div className="absolute inset-[-3px] rounded-full border border-[#87A7D0]/80 border-dashed nilo-ring-outer pointer-events-none" />

          {/* Inner Counter-Rotating Ring */}
          <div className="absolute inset-[-1px] rounded-full border border-[#B3CEEC]/70 nilo-ring-inner pointer-events-none" />

          {/* Core Sphere */}
          <div className="relative w-8 h-8 rounded-full bg-gradient-to-tr from-[#0B0C10] to-[#233852] p-0.5 flex items-center justify-center shadow-inner">
            <Bot className="w-4 h-4 text-[#87A7D0] group-hover:scale-110 transition duration-200" />
            <span
              className={`absolute top-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-white dark:border-[#0B0C10] ${
                hasActiveError ? 'bg-amber-400 animate-ping' : 'bg-emerald-400'
              }`}
            />
          </div>
        </div>

        {/* Text Label & Hotkey Badge */}
        <div className="flex flex-col items-start text-left">
          <div className="flex items-center gap-1.5">
            <span className="font-extrabold text-xs tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-[#3D6390] via-[#5C85B7] to-[#87A7D0] dark:from-[#87A7D0] dark:to-white">
              Nilo AI
            </span>
            <Sparkles className="w-3 h-3 text-[#D4AF37]" />
          </div>
          <span className="text-[10px] font-mono text-gray-500 dark:text-gray-400 leading-none">
            DevOps Assistant
          </span>
        </div>

        {/* Keyboard Shortcut Chip */}
        <kbd className="hidden sm:inline-flex items-center text-[10px] font-mono font-bold px-1.5 py-0.5 rounded-md bg-gray-100 dark:bg-white/10 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-white/10 shadow-sm ml-1">
          ⌘K
        </kbd>
      </button>
    </div>
  );
};
