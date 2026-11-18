import React, { useState } from 'react';
import { DiffEditor } from '@monaco-editor/react';
import { useTheme } from '../context/ThemeContext';
import { Copy, Check } from 'lucide-react';

interface DiffViewerProps {
  originalCode: string;
  migratedCode: string;
  diffText?: string;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({
  originalCode,
  migratedCode,
  diffText
}) => {
  const { resolvedTheme } = useTheme();
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState<'editor' | 'unified'>('editor');

  const handleCopy = () => {
    navigator.clipboard.writeText(migratedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-full rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 overflow-hidden shadow-lg card-3d">
      {/* Header Bar */}
      <div className="flex items-center justify-between px-5 py-3 bg-gray-50/80 dark:bg-white/5 border-b border-gray-200 dark:border-white/10 text-xs">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 font-semibold text-gray-700 dark:text-gray-300">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-sm shadow-rose-500/30" />
            <span className="text-gray-600 dark:text-gray-400">Legacy (PayFlow v1.0)</span>
            <span className="text-gray-300 dark:text-gray-600 mx-1">➔</span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/30" />
            <span className="text-[#3D6390] dark:text-[#87A7D0] font-bold">Modernized (PayFlow v2.0)</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View toggle */}
          <div className="flex items-center bg-gray-100 dark:bg-white/5 rounded-xl p-0.5 border border-gray-200 dark:border-white/10">
            <button
              onClick={() => setViewMode('editor')}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition cursor-pointer ${
                viewMode === 'editor'
                  ? 'bg-white dark:bg-[#87A7D0]/25 text-[#3D6390] dark:text-[#87A7D0] shadow-sm font-bold'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Side-by-Side
            </button>
            <button
              onClick={() => setViewMode('unified')}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition cursor-pointer ${
                viewMode === 'unified'
                  ? 'bg-white dark:bg-[#87A7D0]/25 text-[#3D6390] dark:text-[#87A7D0] shadow-sm font-bold'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Unified Patch
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gray-100 dark:bg-white/5 hover:bg-gray-200 dark:hover:bg-white/10 border border-gray-200 dark:border-white/10 text-gray-700 dark:text-gray-300 transition text-[11px] font-medium"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-500" />
                <span className="text-emerald-600 dark:text-emerald-400 font-bold">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy Migrated</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Editor Content Area */}
      <div className="flex-1 min-h-[400px] relative">
        {viewMode === 'editor' ? (
          <DiffEditor
            height="100%"
            language="python"
            original={originalCode}
            modified={migratedCode}
            theme={resolvedTheme === 'dark' ? 'vs-dark' : 'light'}
            options={{
              readOnly: true,
              renderSideBySide: true,
              minimap: { enabled: false },
              fontSize: 12.5,
              scrollBeyondLastLine: false,
              wordWrap: 'on',
              lineNumbersMinChars: 3,
              automaticLayout: true
            }}
          />
        ) : (
          <div className="p-5 font-mono text-xs overflow-auto h-full bg-gray-50 dark:bg-[#0B0C10] text-gray-800 dark:text-gray-200">
            {diffText ? (
              <pre className="whitespace-pre space-y-0.5">
                {diffText.split('\n').map((line, idx) => {
                  let colorClass = 'text-gray-600 dark:text-gray-400';
                  if (line.startsWith('+') && !line.startsWith('+++')) {
                    colorClass = 'text-emerald-700 bg-emerald-100/60 dark:text-emerald-400 dark:bg-emerald-950/40 font-semibold';
                  } else if (line.startsWith('-') && !line.startsWith('---')) {
                    colorClass = 'text-rose-700 bg-rose-100/60 dark:text-rose-400 dark:bg-rose-950/40 font-semibold';
                  } else if (line.startsWith('@@')) {
                    colorClass = 'text-[#3D6390] bg-[#87A7D0]/20 dark:text-[#87A7D0] dark:bg-[#87A7D0]/20 font-bold';
                  }
                  return (
                    <div key={idx} className={`${colorClass} px-2.5 py-0.5 rounded`}>
                      {line}
                    </div>
                  );
                })}
              </pre>
            ) : (
              <div className="text-gray-400 py-12 text-center text-xs">
                No unified patch generated yet. Run migration to generate diff.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
