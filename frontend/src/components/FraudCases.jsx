// src/components/FraudCases.jsx
import { useEffect, useState } from "react";
import { api } from "../api";

const SEVERITY_STYLE = {
  critical: "bg-red-900/30 text-red-300 border-red-800/40",
  high:     "bg-orange-900/30 text-orange-300 border-orange-800/40",
  medium:   "bg-yellow-900/30 text-yellow-300 border-yellow-800/40",
  low:      "bg-slate-700 text-slate-300 border-slate-600",
};

export default function FraudCases() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const res = await api.getOpenCases();
    setCases(res.data);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const resolve = async (caseId) => {
    await api.resolveCase(caseId);
    load();
  };

  const markFP = async (caseId) => {
    await api.markFalsePositive(caseId);
    load();
  };

  return (
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-white font-bold text-lg">Open Fraud Cases</h2>
        <span className="bg-red-600/20 text-red-300 border border-red-700/30 text-xs px-3 py-1 rounded-full font-semibold">
          {cases.length} open
        </span>
      </div>

      {loading ? (
        <p className="text-slate-500 text-sm text-center py-8">Loading cases...</p>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {cases.map((c) => (
            <div key={c.case_id} className={`rounded-xl p-4 border ${SEVERITY_STYLE[c.severity]}`}>
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-mono text-xs opacity-70">{c.case_id}</p>
                  <p className="text-sm font-semibold mt-0.5">{c.account_id}</p>
                </div>
                <span className="text-xs font-bold uppercase px-2 py-0.5 rounded bg-black/20">
                  {c.severity}
                </span>
              </div>
              <p className="text-xs opacity-80 mb-1">{c.reason_summary}</p>
              <p className="text-xs font-semibold">
                Action: <span className="font-mono">{c.recommended_action}</span>
              </p>
              <p className="text-xs opacity-60 mb-3">Assigned to: {c.assigned_to}</p>
              <div className="flex gap-2">
                <button
                  onClick={() => resolve(c.case_id)}
                  className="flex-1 bg-emerald-700/50 hover:bg-emerald-700 text-emerald-200 text-xs py-1 rounded-lg transition font-semibold"
                >
                  ✓ Resolve
                </button>
                <button
                  onClick={() => markFP(c.case_id)}
                  className="flex-1 bg-slate-600/50 hover:bg-slate-600 text-slate-300 text-xs py-1 rounded-lg transition font-semibold"
                >
                  False Positive
                </button>
              </div>
            </div>
          ))}
          {cases.length === 0 && (
            <p className="text-slate-500 text-sm text-center py-8">🎉 No open cases.</p>
          )}
        </div>
      )}
    </div>
  );
}
