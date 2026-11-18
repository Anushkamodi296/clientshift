import React, { useEffect, useState } from 'react';
import {
  Activity,
  CheckCircle2,
  Clock,
  Layers,
  Sparkles,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Zap,
  Terminal,
  FileCode2
} from 'lucide-react';
import { api } from '../services/api';
import type { MigrationRunRecord, ExperimentSummary, SystemHealth } from '../services/api';

interface DashboardProps {
  onNavigateToWorkspace: (presetCode?: string, presetTest?: string) => void;
  onNavigateToBenchmark: () => void;
  systemHealth: SystemHealth | null;
}

export const Dashboard: React.FC<DashboardProps> = ({
  onNavigateToWorkspace,
  onNavigateToBenchmark,
  systemHealth
}) => {
  const [recentRuns, setRecentRuns] = useState<MigrationRunRecord[]>([]);
  const [_benchmarkSummaries, setBenchmarkSummaries] = useState<ExperimentSummary[]>([]);
  const [_loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [runs, summaries] = await Promise.all([
          api.listMigrations(8),
          api.getBenchmarkSummaries().catch(() => [])
        ]);
        setRecentRuns(runs);
        setBenchmarkSummaries(summaries);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const totalRuns = recentRuns.length;
  const passedRuns = recentRuns.filter(r => r.passed_validation).length;
  const passRate = totalRuns > 0 ? Math.round((passedRuns / totalRuns) * 100) : 100;
  const avgLatency = totalRuns > 0
    ? Math.round(recentRuns.reduce((acc, r) => acc + r.total_latency_ms, 0) / totalRuns)
    : 450;

  const presets = [
    {
      title: "PF-001: Method Rename",
      desc: "Migrate client.charge.create to client.payments.create",
      code: `def process_order(client, total, user_id):\n    return client.charge.create(amount=total, currency="USD", customer=user_id)`,
      test: `def test_process_order():\n    from migrated_module import process_order\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    client = PayFlowClient(config=ClientConfig(api_key="test"))\n    res = process_order(client, 100, "usr_1")\n    assert res["status"] == "succeeded"\n    assert res["amount"] == 100`
    },
    {
      title: "PF-004: Client Auth Config",
      desc: "Direct apiKey instantiation to ClientConfig object",
      code: `from payflow.client import PayFlowClient\ndef make_client(token):\n    return PayFlowClient(apiKey=token)`,
      test: `def test_make_client():\n    from migrated_module import make_client\n    c = make_client("live_secret_123")\n    assert c.config.api_key == "live_secret_123"`
    },
    {
      title: "PF-003: Exception Modernization",
      desc: "Replace PayFlowError with PayFlowAPIException",
      code: `from payflow.exceptions import PayFlowError\ndef safe_execute(action):\n    try:\n        return action()\n    except PayFlowError as err:\n        return {"error": str(err)}`,
      test: `def test_safe():\n    from migrated_module import safe_execute\n    from payflow.exceptions import PayFlowAPIException\n    def failing():\n        raise PayFlowAPIException("API rate limit")\n    res = safe_execute(failing)\n    assert "API rate limit" in res["error"]`
    },
    {
      title: "Multi-Change Combo",
      desc: "Auth config + Charge rename + Amount cents + Pytest sandbox",
      code: `from payflow.client import PayFlowClient\ndef checkout(key, total):\n    client = PayFlowClient(apiKey=key)\n    return client.charge.create(amount_cents=total)`,
      test: `def test_checkout():\n    from migrated_module import checkout\n    res = checkout("key_123", 5000)\n    assert res["amount"] == 5000 and res["currency"] == "USD"`
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-in fade-in duration-300">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl p-8 bg-gradient-to-br from-[#87A7D0]/10 via-[#5C85B7]/5 to-[#B3CEEC]/10 dark:from-[#121218] dark:via-[#161922] dark:to-[#0B0C10] border border-gray-200 dark:border-white/10 shadow-lg card-3d">
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="max-w-2xl space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-[#87A7D0]/15 text-[#3D6390] dark:text-[#87A7D0] border border-[#87A7D0]/30 font-bold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Deterministic AI Code Migration Engine</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white">
              Migrate Breaking SDKs with{' '}
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#3D6390] via-[#5C85B7] to-[#87A7D0] dark:from-[#87A7D0] dark:to-[#C5DAF2]">
                Deterministic Proof
              </span>
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
              ClientShift pairs Python AST static analysis and ground-truth catalog retrieval with local AI generation, verified by strict sandboxed Pytest execution and bounded self-healing loops.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3 shrink-0">
            <button
              onClick={() => onNavigateToWorkspace()}
              className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-gradient-to-r from-[#5076A3] to-[#87A7D0] hover:from-[#436791] hover:to-[#7696BE] text-white font-extrabold text-sm shadow-lg shadow-[#87A7D0]/25 active:scale-95 transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              <Layers className="w-4 h-4" />
              <span>Launch Workspace</span>
            </button>
            <button
              onClick={onNavigateToBenchmark}
              className="w-full sm:w-auto px-5 py-3 rounded-2xl bg-white dark:bg-white/5 hover:bg-gray-100 dark:hover:bg-white/10 text-gray-800 dark:text-white font-bold text-sm border border-gray-200 dark:border-white/10 transition flex items-center justify-center gap-2 cursor-pointer shadow-sm"
            >
              <Terminal className="w-4 h-4 text-[#3D6390] dark:text-[#87A7D0]" />
              <span>MiniBench Harness</span>
            </button>
          </div>
        </div>
      </div>

      {/* Primary KPI Metrics Cards with 3D Depth */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="p-5 rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 shadow-sm transition card-3d">
          <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Pytest Pass Rate</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-gray-900 dark:text-white font-mono">
            {passRate}%
          </div>
          <div className="mt-2 text-[11px] text-emerald-600 dark:text-emerald-400 flex items-center gap-1 font-semibold">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Strict exit code 0 enforcement</span>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="p-5 rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 shadow-sm transition card-3d">
          <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Average Latency</span>
            <div className="w-9 h-9 rounded-xl bg-[#87A7D0]/15 text-[#3D6390] dark:text-[#87A7D0] flex items-center justify-center">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-gray-900 dark:text-white font-mono">
            {avgLatency}ms
          </div>
          <div className="mt-2 text-[11px] text-gray-500 dark:text-gray-400 flex items-center gap-1 font-medium">
            <Zap className="w-3.5 h-3.5 text-amber-500" />
            <span>AST parse + sandbox execution</span>
          </div>
        </div>

        {/* Metric 3 */}
        <div className="p-5 rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 shadow-sm transition card-3d">
          <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Active Catalog Rules</span>
            <div className="w-9 h-9 rounded-xl bg-purple-500/15 text-purple-600 dark:text-[#8A2BE2] flex items-center justify-center">
              <Layers className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-gray-900 dark:text-white font-mono">
            {systemHealth?.rules_count || 6} Rules
          </div>
          <div className="mt-2 text-[11px] text-purple-600 dark:text-[#8A2BE2] flex items-center gap-1 font-semibold">
            <FileCode2 className="w-3.5 h-3.5" />
            <span>PayFlow v1.0 ➔ v2.0 indexed</span>
          </div>
        </div>

        {/* Metric 4 */}
        <div className="p-5 rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 shadow-sm transition card-3d">
          <div className="flex items-center justify-between text-gray-500 dark:text-gray-400 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Benchmark Cases</span>
            <div className="w-9 h-9 rounded-xl bg-amber-500/15 text-amber-600 dark:text-[#D4AF37] flex items-center justify-center">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-gray-900 dark:text-white font-mono">
            60 Cases
          </div>
          <div className="mt-2 text-[11px] text-gray-500 dark:text-gray-400 flex items-center gap-1 font-medium">
            <span>6 distinct failure categories</span>
          </div>
        </div>
      </div>

      {/* Quick Start Presets Section with 3D Depth */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-extrabold text-gray-900 dark:text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-[#3D6390] dark:text-[#87A7D0]" />
            <span>Quick-Start Migration Presets</span>
          </h2>
          <span className="text-xs text-gray-500 dark:text-gray-400">Click any card to load into workspace</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {presets.map((preset, idx) => (
            <div
              key={idx}
              onClick={() => onNavigateToWorkspace(preset.code, preset.test)}
              className="p-5 rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 hover:border-[#87A7D0] hover:shadow-xl cursor-pointer transition group card-3d"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-extrabold text-[#3D6390] dark:text-[#87A7D0]">
                  {preset.title}
                </span>
                <ArrowRight className="w-4 h-4 text-gray-400 group-hover:translate-x-1 group-hover:text-[#3D6390] dark:group-hover:text-[#87A7D0] transition" />
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mb-3 font-medium">
                {preset.desc}
              </p>
              <pre className="p-3 rounded-2xl bg-gray-50 dark:bg-black/40 border border-gray-100 dark:border-white/5 font-mono text-[11px] text-gray-800 dark:text-gray-300 overflow-hidden line-clamp-3">
                {preset.code}
              </pre>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Migrations Table */}
      <div className="rounded-3xl bg-white dark:bg-[#121218] border border-gray-200 dark:border-white/10 p-6 shadow-sm card-3d">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-extrabold text-gray-900 dark:text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#3D6390] dark:text-[#87A7D0]" />
              <span>Recent Migration Runs</span>
            </h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Live audit trail of AST detections and sandboxed Pytest results
            </p>
          </div>
          <button
            onClick={() => onNavigateToWorkspace()}
            className="text-xs font-bold text-[#3D6390] dark:text-[#87A7D0] hover:underline flex items-center gap-1 cursor-pointer"
          >
            <span>Open Workspace</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {recentRuns.length === 0 ? (
          <div className="text-center py-12 text-gray-400 text-xs">
            No migration runs logged yet. Launch the workspace to run your first migration!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-gray-200 dark:border-white/10 text-gray-500 dark:text-gray-400 font-bold uppercase tracking-wider">
                  <th className="py-3 px-3">Run ID</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Rules Applied</th>
                  <th className="py-3 px-3">Pytest Sandbox</th>
                  <th className="py-3 px-3">Repair Loops</th>
                  <th className="py-3 px-3">Latency</th>
                  <th className="py-3 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-white/5 font-mono">
                {recentRuns.map((r) => (
                  <tr key={r.id} className="hover:bg-gray-50/80 dark:hover:bg-white/5 transition">
                    <td className="py-3 px-3 font-bold text-gray-900 dark:text-white">
                      {r.id}
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider ${
                          r.status === 'success'
                            ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30'
                            : r.status === 'repaired'
                            ? 'bg-purple-500/15 text-purple-700 dark:text-purple-300 border border-purple-500/30'
                            : 'bg-rose-500/15 text-rose-700 dark:text-rose-400 border border-rose-500/30'
                        }`}
                      >
                        {r.status}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex flex-wrap gap-1">
                        {r.rules_applied.map((rule, idx) => (
                          <span
                            key={idx}
                            className="px-1.5 py-0.5 rounded bg-gray-100 dark:bg-white/10 text-gray-700 dark:text-gray-300 text-[10px] font-semibold"
                          >
                            {rule}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`font-bold ${
                          r.passed_validation
                            ? 'text-emerald-700 dark:text-emerald-400'
                            : 'text-rose-700 dark:text-rose-400'
                        }`}
                      >
                        {r.passed_validation ? 'Exit 0 (Passed)' : 'Exit 1 (Failed)'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-gray-700 dark:text-gray-300">
                      {r.repair_attempts}
                    </td>
                    <td className="py-3 px-3 text-gray-500 dark:text-gray-400">
                      {r.total_latency_ms}ms
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => onNavigateToWorkspace(r.source_code)}
                        className="px-3 py-1 rounded-xl bg-gray-100 dark:bg-white/10 hover:bg-gray-200 dark:hover:bg-white/20 text-gray-800 dark:text-gray-200 transition text-[11px] font-semibold cursor-pointer"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
