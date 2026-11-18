import React, { useState } from 'react';
import {
  Layers,
  Play,
  Search,
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  Terminal,
  FileCode2,
  Clock,
  Shield,
  Upload,
  Info
} from 'lucide-react';
import { DiffViewer } from '../components/DiffViewer';
import { ValidationPanel } from '../components/ValidationPanel';
import { api } from '../services/api';
import type { ASTEvidence, RuleMatch, MigrationRunRecord } from '../services/api';

interface MigrationWorkspaceProps {
  initialCode?: string;
  initialTest?: string;
  onAskNilo: (errorTrace: string) => void;
}

export const MigrationWorkspace: React.FC<MigrationWorkspaceProps> = ({
  initialCode,
  initialTest,
  onAskNilo
}) => {
  const defaultSource = initialCode || `from payflow.client import PayFlowClient
from payflow.exceptions import PayFlowError

def process_checkout(api_key, cents):
    try:
        client = PayFlowClient(apiKey=api_key)
        return client.charge.create(amount_cents=cents)
    except PayFlowError as err:
        return {"error": str(err)}
`;

  const defaultTest = initialTest || `def test_checkout():
    from migrated_module import process_checkout
    res = process_checkout("live_secret_key", 5000)
    assert res["status"] == "succeeded"
    assert res["amount"] == 5000
    assert res["currency"] == "USD"
`;

  const [sourceCode, setSourceCode] = useState(defaultSource);
  const [testCode, setTestCode] = useState(defaultTest);
  const [showTestEditor, setShowTestEditor] = useState(false);
  const [maxRepairs, setMaxRepairs] = useState(2);

  // Results & Pipeline State
  const [isMigrating, setIsMigrating] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeStageNumber, setActiveStageNumber] = useState<number>(0);
  const [migrationRecord, setMigrationRecord] = useState<MigrationRunRecord | null>(null);
  const [astFindings, setAstFindings] = useState<ASTEvidence[]>([]);
  const [_matchedRules, setMatchedRules] = useState<RuleMatch[]>([]);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  // Quick Preset Loader
  const handleLoadPreset = (key: string) => {
    if (key === 'rename') {
      setSourceCode(`def process_order(client, total, user_id):\n    return client.charge.create(amount=total, currency="USD", customer=user_id)`);
      setTestCode(`def test_process_order():\n    from migrated_module import process_order\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    client = PayFlowClient(config=ClientConfig(api_key="test"))\n    res = process_order(client, 100, "usr_1")\n    assert res["status"] == "succeeded"\n    assert res["amount"] == 100`);
    } else if (key === 'auth') {
      setSourceCode(`from payflow.client import PayFlowClient\ndef make_client(token):\n    return PayFlowClient(apiKey=token)`);
      setTestCode(`def test_make_client():\n    from migrated_module import make_client\n    c = make_client("live_secret_123")\n    assert c.config.api_key == "live_secret_123"`);
    } else if (key === 'exception') {
      setSourceCode(`from payflow.exceptions import PayFlowError\ndef safe_execute(action):\n    try:\n        return action()\n    except PayFlowError as err:\n        return {"error": str(err)}`);
      setTestCode(`def test_safe():\n    from migrated_module import safe_execute\n    from payflow.exceptions import PayFlowAPIException\n    def failing():\n        raise PayFlowAPIException("API rate limit")\n    res = safe_execute(failing)\n    assert "API rate limit" in res["error"]`);
    } else if (key === 'multi') {
      setSourceCode(`from payflow.client import PayFlowClient\ndef checkout(key, total):\n    client = PayFlowClient(apiKey=key)\n    return client.charge.create(amount_cents=total)`);
      setTestCode(`def test_checkout():\n    from migrated_module import checkout\n    res = checkout("key_123", 5000)\n    assert res["amount"] == 5000 and res["currency"] == "USD"`);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      if (content) setSourceCode(content);
    };
    reader.readAsText(file);
  };

  // Run Stage 1 & 2: AST Analysis Only
  const handleAnalyzeOnly = async () => {
    setIsAnalyzing(true);
    setErrorBanner(null);
    try {
      const res = await api.analyzeCode(sourceCode);
      setAstFindings(res.ast_findings);
      setMatchedRules(res.matched_rules);
      if (res.syntax_error) {
        setErrorBanner(`Syntax Error: ${res.syntax_error}`);
      }
    } catch (err: any) {
      setErrorBanner(err.message || 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Run Full 5-Stage Migration Pipeline
  const handleRunFullMigration = async () => {
    setIsMigrating(true);
    setErrorBanner(null);
    setActiveStageNumber(1);

    try {
      const timer1 = setTimeout(() => setActiveStageNumber(2), 200);
      const timer2 = setTimeout(() => setActiveStageNumber(3), 400);
      const timer3 = setTimeout(() => setActiveStageNumber(4), 650);
      const timer4 = setTimeout(() => setActiveStageNumber(5), 900);

      const record = await api.migrateCode(sourceCode, testCode, maxRepairs);
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);

      setMigrationRecord(record);
      setAstFindings(record.ast_findings);
      setActiveStageNumber(5);
    } catch (err: any) {
      setErrorBanner(err.message || 'Migration pipeline execution failed');
    } finally {
      setIsMigrating(false);
    }
  };

  const stagesList = [
    { num: 1, name: 'AST Analysis', desc: 'Deterministic Syntax Tree extraction' },
    { num: 2, name: 'Rule Retrieval', desc: 'TF-IDF Catalog Rule Grounding' },
    { num: 3, name: 'AI Plan', desc: 'Local model patch synthesis' },
    { num: 4, name: 'Diff Patch', desc: 'Syntax verification & unified diff' },
    { num: 5, name: 'Sandbox Pytest', desc: 'Isolated test & bounded repair loop' }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in duration-300">
      {/* Workspace Header & Action Bar with 3D Depth */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-6 rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 shadow-sm card-3d">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white flex items-center gap-2.5">
            <Layers className="w-6 h-6 text-[#3D6390] dark:text-[#87A7D0]" />
            <span>AI Code Migration Workbench</span>
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 font-medium">
            Deterministic AST parsing, rule citations, verified unified diffs, and sandboxed Pytest execution
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Preset Selector */}
          <select
            onChange={(e) => handleLoadPreset(e.target.value)}
            className="px-3 py-2 rounded-xl bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10 text-xs font-semibold text-gray-800 dark:text-gray-200 focus:outline-none"
          >
            <option value="">Load Preset Scenario...</option>
            <option value="rename">PF-001: Method Rename</option>
            <option value="auth">PF-004: Client Auth Config</option>
            <option value="exception">PF-003: Exception Hierarchy</option>
            <option value="multi">Multi-Change Combo</option>
          </select>

          {/* Upload Button */}
          <label className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-gray-100 dark:bg-white/5 hover:bg-gray-200 dark:hover:bg-white/10 border border-gray-200 dark:border-white/10 text-xs font-semibold text-gray-800 dark:text-gray-200 cursor-pointer transition">
            <Upload className="w-3.5 h-3.5" />
            <span>Upload .py</span>
            <input type="file" accept=".py" onChange={handleFileUpload} className="hidden" />
          </label>

          {/* Analyze AST button */}
          <button
            onClick={handleAnalyzeOnly}
            disabled={isAnalyzing || isMigrating}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#87A7D0]/10 hover:bg-[#87A7D0]/20 text-[#3D6390] dark:text-[#87A7D0] border border-[#87A7D0]/30 font-bold text-xs transition disabled:opacity-50 cursor-pointer"
          >
            {isAnalyzing ? <RotateCw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            <span>Analyze AST</span>
          </button>

          {/* Migrate & Validate button */}
          <button
            onClick={handleRunFullMigration}
            disabled={isMigrating || isAnalyzing}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#5076A3] to-[#87A7D0] hover:from-[#436791] hover:to-[#7696BE] text-white font-extrabold text-xs shadow-lg shadow-[#87A7D0]/25 hover:opacity-95 active:scale-95 transition disabled:opacity-50 cursor-pointer"
          >
            {isMigrating ? <RotateCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
            <span>Migrate & Validate (Pytest)</span>
          </button>
        </div>
      </div>

      {/* Error banner if any */}
      {errorBanner && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-500/15 border border-rose-200 dark:border-rose-500/30 text-rose-800 dark:text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-500" />
            <span className="font-mono font-semibold">{errorBanner}</span>
          </div>
          <button
            onClick={() => onAskNilo(errorBanner)}
            className="px-3 py-1 rounded-xl bg-rose-100 dark:bg-rose-500/20 hover:bg-rose-200 dark:hover:bg-rose-500/30 font-bold transition text-[11px] cursor-pointer"
          >
            Ask Nilo to Diagnose
          </button>
        </div>
      )}

      {/* 5-Stage Live Timeline Indicator */}
      <div className="p-6 rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 shadow-sm card-3d">
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-extrabold uppercase tracking-wider text-gray-500 dark:text-gray-400">
            5-Stage Deterministic Migration Timeline
          </span>
          {migrationRecord && (
            <span className="text-xs font-mono text-[#3D6390] dark:text-[#87A7D0] flex items-center gap-1 font-bold">
              <Clock className="w-3.5 h-3.5" />
              Total Latency: {migrationRecord.total_latency_ms}ms
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {stagesList.map((stg) => {
            const stageLog = migrationRecord?.stages.find(s => s.stage_number === stg.num);
            const isCompleted = stageLog?.status === 'completed';
            const isFailed = stageLog?.status === 'failed';
            const isActive = isMigrating && activeStageNumber === stg.num;

            return (
              <div
                key={stg.num}
                className={`p-4 rounded-2xl border transition-all ${
                  isCompleted
                    ? 'bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/30 text-emerald-800 dark:text-emerald-300'
                    : isFailed
                    ? 'bg-rose-50 dark:bg-rose-500/10 border-rose-200 dark:border-rose-500/30 text-rose-800 dark:text-rose-300'
                    : isActive
                    ? 'bg-[#87A7D0]/15 border-[#87A7D0]/50 text-[#3D6390] dark:text-[#87A7D0] shadow-md shadow-[#87A7D0]/15'
                    : 'bg-gray-50 dark:bg-white/5 border-gray-200 dark:border-white/10 text-gray-500 dark:text-gray-400 opacity-90'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10">
                    STAGE {stg.num}
                  </span>
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  ) : isFailed ? (
                    <AlertTriangle className="w-4 h-4 text-rose-500" />
                  ) : isActive ? (
                    <RotateCw className="w-4 h-4 text-[#87A7D0] animate-spin" />
                  ) : (
                    <span className="w-2 h-2 rounded-full bg-gray-300 dark:bg-gray-600" />
                  )}
                </div>
                <h4 className="font-extrabold text-xs text-gray-900 dark:text-white mb-0.5">{stg.name}</h4>
                <p className="text-[10px] text-gray-500 dark:text-gray-400 line-clamp-2">{stg.desc}</p>
                {stageLog && (
                  <div className="mt-2 text-[10px] font-mono font-semibold text-gray-500 dark:text-gray-400">
                    {stageLog.latency_ms}ms
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Split: Code Inputs & Diff Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Input Code Area & Test Editor */}
        <div className="lg:col-span-5 space-y-4">
          <div className="rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 overflow-hidden shadow-sm card-3d">
            <div className="flex items-center justify-between px-5 py-3 bg-gray-50/80 dark:bg-white/5 border-b border-gray-200 dark:border-white/10 text-xs font-bold text-gray-700 dark:text-gray-300">
              <div className="flex items-center gap-2">
                <FileCode2 className="w-4 h-4 text-[#3D6390] dark:text-[#87A7D0]" />
                <span>Source Code (PayFlow v1.0 Input)</span>
              </div>
              <button
                onClick={() => setSourceCode('')}
                className="text-[11px] text-gray-400 hover:text-gray-600 dark:hover:text-white cursor-pointer"
              >
                Clear
              </button>
            </div>
            <textarea
              value={sourceCode}
              onChange={(e) => setSourceCode(e.target.value)}
              rows={12}
              className="w-full p-4 font-mono text-xs bg-transparent text-gray-900 dark:text-gray-100 focus:outline-none resize-none"
              placeholder="# Paste PayFlow v1.0 Python code here..."
            />
          </div>

          {/* Test Code Editor Toggle Card */}
          <div className="rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 overflow-hidden shadow-sm card-3d">
            <div className="flex items-center justify-between px-5 py-3 bg-gray-50/80 dark:bg-white/5 border-b border-gray-200 dark:border-white/10 text-xs font-bold text-gray-700 dark:text-gray-300">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <span>Pytest Sandbox Verification Code</span>
              </div>
              <button
                onClick={() => setShowTestEditor(!showTestEditor)}
                className="text-[11px] text-[#3D6390] dark:text-[#87A7D0] hover:underline font-bold cursor-pointer"
              >
                {showTestEditor ? 'Hide Test' : 'Edit Test'}
              </button>
            </div>
            {showTestEditor ? (
              <textarea
                value={testCode}
                onChange={(e) => setTestCode(e.target.value)}
                rows={8}
                className="w-full p-4 font-mono text-xs bg-transparent text-gray-900 dark:text-gray-100 focus:outline-none resize-none"
              />
            ) : (
              <div className="p-4 text-xs text-gray-500 dark:text-gray-400 flex items-center justify-between">
                <span>Verification test loaded ({testCode.split('\n').length} lines)</span>
                <span className="font-mono text-[10px] text-emerald-700 dark:text-emerald-400 font-bold">test_migrated.py</span>
              </div>
            )}
          </div>

          {/* Repair loop configuration */}
          <div className="p-4 rounded-2xl bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <RotateCw className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span className="font-semibold text-gray-700 dark:text-gray-300">Bounded Repair Loop Cap</span>
            </div>
            <select
              value={maxRepairs}
              onChange={(e) => setMaxRepairs(Number(e.target.value))}
              className="px-3 py-1.5 rounded-xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 text-xs font-mono font-bold"
            >
              <option value={1}>Max 1 Repair</option>
              <option value={2}>Max 2 Repairs (Standard)</option>
              <option value={3}>Max 3 Repairs</option>
            </select>
          </div>
        </div>

        {/* Right Column: Monaco Side-by-Side Diff Viewer */}
        <div className="lg:col-span-7 h-full">
          <DiffViewer
            originalCode={sourceCode}
            migratedCode={migrationRecord?.migrated_code || sourceCode}
            diffText={migrationRecord?.diff}
          />
        </div>
      </div>

      {/* Evidence Panel (AST Findings) with 3D Depth */}
      <div className="rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 p-6 shadow-sm card-3d">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-extrabold text-gray-900 dark:text-white flex items-center gap-2">
              <Shield className="w-5 h-5 text-[#3D6390] dark:text-[#87A7D0]" />
              <span>AST Static Evidence Panel ({astFindings.length} Detected)</span>
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Deterministic AST detections mapped directly to breaking catalog signatures
            </p>
          </div>
        </div>

        {astFindings.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-xs font-medium">
            No breaking AST patterns flagged in current source code. Click <strong>Analyze AST</strong> to inspect.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {astFindings.map((finding, idx) => (
              <div
                key={idx}
                className="p-4 rounded-2xl bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="font-mono font-extrabold text-[#3D6390] dark:text-[#87A7D0]">
                      {finding.rule_id}
                    </span>
                    <span className="text-gray-300 dark:text-gray-600">•</span>
                    <span className="font-bold text-gray-800 dark:text-gray-200">
                      {finding.rule_name}
                    </span>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
                      finding.risk_level === 'HIGH'
                        ? 'bg-rose-500/15 text-rose-700 dark:text-rose-400'
                        : 'bg-amber-500/15 text-amber-700 dark:text-amber-400'
                    }`}
                  >
                    {finding.risk_level} RISK
                  </span>
                </div>

                <div className="text-gray-600 dark:text-gray-300 font-medium">
                  {finding.evidence_text}
                </div>

                <div className="p-2.5 rounded-xl bg-white dark:bg-black/30 border border-gray-200 dark:border-white/10 font-mono text-[11px] text-gray-800 dark:text-gray-200">
                  <span className="text-gray-400">Line {finding.line_number}: </span>
                  {finding.snippet}
                </div>

                <div className="text-[11px] text-emerald-700 dark:text-emerald-400 flex items-center gap-1 font-semibold">
                  <Info className="w-3.5 h-3.5 shrink-0" />
                  <span>{finding.recommended_fix}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Validation Sandbox Panel */}
      <ValidationPanel
        pytestResult={migrationRecord?.pytest_result}
        repairAttempts={migrationRecord?.repair_attempts || 0}
        status={migrationRecord?.status || 'idle'}
        onAskNilo={onAskNilo}
      />
    </div>
  );
};
