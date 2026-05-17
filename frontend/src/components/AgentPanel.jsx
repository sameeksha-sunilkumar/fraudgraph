// src/components/AgentPanel.jsx
// The signature component: shows all 4 Jac walkers running live
import { useState } from "react";
import { api } from "../api";

const WALKERS = [
  {
    id: "detect",
    name: "FraudDetectionWalker",
    icon: "🔍",
    desc: "Traverses account→transaction graph, ML-scores each tx",
    color: "blue",
    requiresAccount: true,
    fn: (id) => api.runDetection(id),
  },
  {
    id: "anomalies",
    name: "AnomalyPatternWalker",
    icon: "📡",
    desc: "Detects velocity spikes, geo anomalies, high-risk merchant clusters",
    color: "purple",
    requiresAccount: true,
    fn: (id) => api.runAnomalies(id),
  },
  {
    id: "escalate",
    name: "EscalationWalker",
    icon: "⚡",
    desc: "Routes high-risk accounts, uses by llm() for action recommendation",
    color: "orange",
    requiresAccount: true,
    fn: (id) => api.runEscalation(id),
  },
  {
    id: "synthesize",
    name: "SynthesisWalker",
    icon: "🧠",
    desc: "Aggregates all findings, produces executive report via by llm()",
    color: "emerald",
    requiresAccount: false,
    fn: () => api.runSynthesis(),
  },
];

const COLOR_MAP = {
  blue:    { btn: "bg-blue-600 hover:bg-blue-500",    badge: "bg-blue-500/10 text-blue-300 border-blue-500/30" },
  purple:  { btn: "bg-purple-600 hover:bg-purple-500", badge: "bg-purple-500/10 text-purple-300 border-purple-500/30" },
  orange:  { btn: "bg-orange-600 hover:bg-orange-500", badge: "bg-orange-500/10 text-orange-300 border-orange-500/30" },
  emerald: { btn: "bg-emerald-600 hover:bg-emerald-500", badge: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30" },
};

export default function AgentPanel({ accountId }) {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState({});
  const [fullLoading, setFullLoading] = useState(false);
  const [fullResult, setFullResult] = useState(null);

  const run = async (walker) => {
    if (walker.requiresAccount && !accountId) return;
    setLoading((l) => ({ ...l, [walker.id]: true }));
    try {
      const res = await walker.fn(accountId);
      setResults((r) => ({ ...r, [walker.id]: res.data }));
    } catch (e) {
      setResults((r) => ({ ...r, [walker.id]: { error: "Walker failed" } }));
    } finally {
      setLoading((l) => ({ ...l, [walker.id]: false }));
    }
  };

  const runFull = async () => {
    if (!accountId) return;
    setFullLoading(true);
    try {
      const res = await api.runFullScan(accountId);
      setFullResult(res.data);
    } finally {
      setFullLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-white font-bold text-lg">Jac Agent Walkers</h2>
          <p className="text-slate-400 text-xs mt-0.5">Object Spatial Programming — walkers traverse the fraud graph</p>
        </div>
        <button
          onClick={runFull}
          disabled={fullLoading || !accountId}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-slate-600 disabled:to-slate-600 text-white text-xs font-semibold px-4 py-2 rounded-lg transition"
        >
          {fullLoading ? "🔄 Running Pipeline..." : "▶▶ Full Agent Pipeline"}
        </button>
      </div>

      {/* Walker Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {WALKERS.map((w) => {
          const cfg = COLOR_MAP[w.color];
          const result = results[w.id];
          const isLoading = loading[w.id];

          return (
            <div key={w.id} className="bg-slate-700/40 rounded-xl p-4 border border-slate-600/50">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{w.icon}</span>
                  <div>
                    <p className="text-white text-sm font-semibold font-mono">{w.name}</p>
                    <p className="text-slate-400 text-xs">{w.desc}</p>
                  </div>
                </div>
              </div>

              <button
                onClick={() => run(w)}
                disabled={isLoading || (w.requiresAccount && !accountId)}
                className={`w-full ${cfg.btn} disabled:bg-slate-600 text-white text-xs font-semibold py-1.5 rounded-lg transition mb-3`}
              >
                {isLoading ? "🔄 Traversing graph..." : `▶ Run ${w.name}`}
              </button>

              {/* Result */}
              {result && (
                <div className={`rounded-lg border p-3 text-xs ${cfg.badge}`}>
                  {result.error ? (
                    <p className="text-red-400">{result.error}</p>
                  ) : (
                    <pre className="whitespace-pre-wrap overflow-auto max-h-32 font-mono text-xs">
                      {JSON.stringify(result.result ?? result, null, 2)}
                    </pre>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Full pipeline synthesis result */}
      {fullResult && (
        <div className="mt-4 bg-slate-700/40 rounded-xl p-4 border border-emerald-500/30">
          <p className="text-emerald-300 text-sm font-bold mb-2">🧠 Executive Fraud Report (SynthesisWalker)</p>
          <p className="text-slate-300 text-xs mb-3">{fullResult.results?.synthesis?.result?.summary}</p>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="bg-red-900/20 border border-red-800/30 rounded-lg p-3 text-center">
              <p className="text-red-400 text-xl font-bold">{fullResult.results?.synthesis?.result?.critical_count ?? "–"}</p>
              <p className="text-slate-400 text-xs">Critical Cases</p>
            </div>
            <div className="bg-orange-900/20 border border-orange-800/30 rounded-lg p-3 text-center">
              <p className="text-orange-400 text-xl font-bold">{fullResult.results?.synthesis?.result?.high_count ?? "–"}</p>
              <p className="text-slate-400 text-xs">High Risk</p>
            </div>
          </div>
          {fullResult.results?.synthesis?.result?.immediate_actions && (
            <div>
              <p className="text-slate-400 text-xs font-semibold mb-1">Immediate Actions:</p>
              {fullResult.results.synthesis.result.immediate_actions.map((a, i) => (
                <p key={i} className="text-slate-300 text-xs">• {a}</p>
              ))}
            </div>
          )}
          <p className="text-slate-500 text-xs mt-2">Pipeline completed in {fullResult.total_duration_ms}ms</p>
        </div>
      )}
    </div>
  );
}
