// src/components/RiskChart.jsx
import { useEffect, useState } from "react";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { api } from "../api";

const TIER_COLOR = {
  low:      "#34d399",
  medium:   "#fbbf24",
  high:     "#f97316",
  critical: "#f87171",
};

export default function RiskChart({ onSelectAccount }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    api.getRiskChart().then((r) => {
      setData(r.data.map((a, i) => ({
        ...a,
        x: i + 1,
        y: a.fraud_score,
      })));
    });
  }, []);

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
      <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 text-xs">
        <p className="text-white font-semibold">{d.user_name}</p>
        <p className="text-slate-400">{d.account_id}</p>
        <p style={{ color: TIER_COLOR[d.risk_tier] }} className="font-bold">
          {d.risk_tier.toUpperCase()} — {d.fraud_score}
        </p>
      </div>
    );
  };

  return (
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-white font-bold text-lg">Account Risk Distribution</h2>
        <div className="flex gap-3">
          {Object.entries(TIER_COLOR).map(([t, c]) => (
            <span key={t} className="flex items-center gap-1 text-xs text-slate-400">
              <span className="w-2 h-2 rounded-full" style={{ background: c }} />
              {t}
            </span>
          ))}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="x" hide />
          <YAxis dataKey="y" domain={[0, 100]} tick={{ fill: "#94a3b8", fontSize: 11 }} label={{ value: "Fraud Score", angle: -90, position: "insideLeft", fill: "#94a3b8", fontSize: 11 }} />
          <Tooltip content={<CustomTooltip />} />
          <Scatter
            data={data}
            onClick={(d) => onSelectAccount?.(d.account_id)}
            style={{ cursor: "pointer" }}
          >
            {data.map((d, i) => (
              <Cell key={i} fill={TIER_COLOR[d.risk_tier]} fillOpacity={0.85} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      <p className="text-slate-500 text-xs text-center mt-2">Click a dot to select an account and run Jac walkers</p>
    </div>
  );
}
