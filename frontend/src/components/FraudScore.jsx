// src/components/FraudScore.jsx
import { useEffect, useState } from "react";
import { api } from "../api";

const TIER_CONFIG = {
  low:      { color: "text-emerald-400", bg: "bg-emerald-400/10", border: "border-emerald-400/30", icon: "🟢", label: "Low Risk" },
  medium:   { color: "text-yellow-400",  bg: "bg-yellow-400/10",  border: "border-yellow-400/30",  icon: "🟡", label: "Medium Risk" },
  high:     { color: "text-orange-400",  bg: "bg-orange-400/10",  border: "border-orange-400/30",  icon: "🟠", label: "High Risk" },
  critical: { color: "text-red-400",     bg: "bg-red-400/10",     border: "border-red-400/30",     icon: "🔴", label: "Critical" },
};

export default function FraudScore({ accountId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    api.getDashboardSummary().then((r) => setSummary(r.data));
  }, []);

  const runScan = async () => {
    if (!accountId) return;
    setLoading(true);
    try {
      const res = await api.runDetection(accountId);
      setData(res.data.result);
    } finally {
      setLoading(false);
    }
  };

  const tier = data?.risk_tier || "low";
  const cfg = TIER_CONFIG[tier];
  const score = data?.fraud_score ?? summary?.accounts?.flagged ?? 0;

  return (
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700 h-full flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-white font-bold text-lg">Fraud Risk Score</h2>
        <span className="text-slate-500 text-xs">Jac Walker</span>
      </div>

      {/* Score Ring */}
      <div className="flex flex-col items-center gap-3 flex-1 justify-center">
        <div className={`relative w-36 h-36 rounded-full border-4 ${cfg.border} ${cfg.bg} flex flex-col items-center justify-center`}>
          <span className="text-4xl">{cfg.icon}</span>
          <span className={`text-2xl font-black ${cfg.color}`}>
            {data ? `${data.fraud_score}` : summary ? `${summary.accounts.flagged}` : "--"}
          </span>
          <span className="text-slate-400 text-xs">{data ? "/ 100" : "flagged"}</span>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold ${cfg.bg} ${cfg.color}`}>
          {cfg.label}
        </div>
      </div>

      {/* Stats */}
      {summary && (
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "Total Accounts", value: summary.accounts.total },
            { label: "Flagged",        value: summary.accounts.flagged, red: true },
            { label: "Open Cases",     value: summary.cases.open },
            { label: "Critical",       value: summary.cases.critical, red: true },
          ].map(({ label, value, red }) => (
            <div key={label} className="bg-slate-700/50 rounded-lg p-3 text-center">
              <p className={`text-lg font-bold ${red ? "text-red-400" : "text-white"}`}>{value}</p>
              <p className="text-slate-400 text-xs">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Trigger Scan */}
      {accountId && (
        <button
          onClick={runScan}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 text-white text-sm font-semibold py-2 rounded-lg transition"
        >
          {loading ? "🔄 Walker Running..." : "▶ Run FraudDetectionWalker"}
        </button>
      )}

      {/* Flagged Transactions */}
      {data?.flagged_transactions?.length > 0 && (
        <div className="mt-2">
          <p className="text-slate-400 text-xs mb-2">
            Flagged Transactions ({data.flagged_transactions.length})
          </p>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {data.flagged_transactions.map((tx) => (
              <div key={tx.tx_id} className="bg-red-900/20 border border-red-800/30 rounded-lg px-3 py-2 flex justify-between items-center">
                <span className="text-red-300 text-xs font-mono">{tx.tx_id}</span>
                <span className="text-red-400 text-xs font-bold">
                  {Math.round(tx.fraud_probability * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
