import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RotateCw,
  Terminal,
  Sparkles,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import type { PytestOutput } from '../services/api';

interface ValidationPanelProps {
  pytestResult?: PytestOutput;
  repairAttempts: number;
  status: string;
  onAskNilo: (errorTrace: string) => void;
}

export const ValidationPanel: React.FC<ValidationPanelProps> = ({
  pytestResult,
  repairAttempts,
  status: _status,
  onAskNilo
}) => {
  const [showStdout, setShowStdout] = useState(false);

  if (!pytestResult) {
    return (
      <div className="p-6 rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 text-center text-gray-500 dark:text-gray-400 text-xs shadow-sm card-3d">
        <Terminal className="w-6 h-6 mx-auto mb-2 text-indigo-500 dark:text-[#00F2FE] opacity-60" />
        No validation run executed yet. Run migration to launch the isolated Pytest sandbox.
      </div>
    );
  }

  const passed = pytestResult.passed;

  return (
    <div className="rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 overflow-hidden shadow-lg transition-colors card-3d">
      {/* Header */}
      <div
        className={`px-5 py-3.5 flex items-center justify-between border-b ${
          passed
            ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-800 dark:text-emerald-300'
            : 'bg-rose-500/10 border-rose-500/20 text-rose-800 dark:text-rose-300'
        }`}
      >
        <div className="flex items-center gap-3">
          {passed ? (
            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          ) : (
            <div className="w-8 h-8 rounded-xl bg-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center justify-center shrink-0">
              <XCircle className="w-5 h-5" />
            </div>
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xs uppercase tracking-wider">
                {passed ? 'Pytest Sandbox Passed' : 'Pytest Validation Failed'}
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-black/10 dark:bg-white/10 font-bold">
                exit code {pytestResult.exit_code}
              </span>
              {repairAttempts > 0 && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-700 dark:text-purple-300 flex items-center gap-1 font-bold">
                  <RotateCw className="w-2.5 h-2.5 animate-spin" />
                  {repairAttempts} repair loop{repairAttempts > 1 ? 's' : ''}
                </span>
              )}
            </div>
            <p className="text-[11px] opacity-90 font-medium">{pytestResult.summary}</p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 text-xs">
          <span className="font-mono text-gray-500 dark:text-gray-400 text-[11px] font-semibold">
            {pytestResult.duration_s}s runtime
          </span>
          {!passed && (
            <button
              onClick={() => onAskNilo(pytestResult.failure_details || pytestResult.stderr || pytestResult.stdout)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-[#6087B8] to-[#87A7D0] text-slate-950 text-[11px] font-bold shadow-md shadow-[#87A7D0]/25 hover:opacity-95 transition cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Ask Nilo to Fix</span>
            </button>
          )}
        </div>
      </div>

      {/* Failure Box if failed */}
      {!passed && pytestResult.failure_details && (
        <div className="p-4 bg-rose-50 dark:bg-rose-950/20 border-b border-rose-200 dark:border-rose-500/20 text-xs">
          <div className="flex items-center gap-1.5 font-bold text-rose-700 dark:text-rose-400 mb-1">
            <AlertTriangle className="w-4 h-4" />
            <span>Traceback Root Cause:</span>
          </div>
          <pre className="font-mono text-[11px] text-rose-800 dark:text-rose-300/90 whitespace-pre-wrap overflow-x-auto bg-white dark:bg-black/40 border border-rose-200 dark:border-rose-500/20 p-3 rounded-xl shadow-inner">
            {pytestResult.failure_details}
          </pre>
        </div>
      )}

      {/* Expandable Console Output */}
      <div className="p-4 bg-slate-900 text-slate-200 font-mono text-[11px]">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Terminal className="w-3.5 h-3.5 text-[#87A7D0]" />
            <span className="text-slate-400 font-semibold">Sandbox Pytest Isolation Test Log</span>
          </div>
          <button
            onClick={() => setShowStdout(!showStdout)}
            className="flex items-center gap-1 text-[11px] text-[#87A7D0] hover:text-[#A2BFE3] font-semibold cursor-pointer"
          >
            <span>{showStdout ? 'Collapse' : 'Expand full output'}</span>
            {showStdout ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        <pre
          className={`mt-2 overflow-x-auto transition-all ${
            showStdout ? 'max-h-96' : 'max-h-24'
          } text-slate-300 scrollbar-none whitespace-pre`}
        >
          {pytestResult.stdout || pytestResult.stderr || 'No stdout produced.'}
        </pre>
      </div>
    </div>
  );
};
