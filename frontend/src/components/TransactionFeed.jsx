// src/components/TransactionFeed.jsx
import { useEffect, useState } from "react";
import { api } from "../api";

const SEVERITY_COLOR = {
  normal: "text-slate-400",
  flagged: "text-orange-400",
  confirmed_fraud: "text-red-400",
  false_positive: "text-slate-500",
};

export default function TransactionFeed() {
  const [transactions, setTransactions] = useState([]);
  const [showFlagged, setShowFlagged] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const res = showFlagged
        ? await api.getFlaggedTransactions()
        : await api.getTransactions(30);
      setTransactions(res.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [showFlagged]);

  return (
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-white font-bold text-lg">Transaction Feed</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setShowFlagged(false)}
            className={`text-xs px-3 py-1 rounded-lg transition font-semibold ${!showFlagged ? "bg-blue-600 text-white" : "bg-slate-700 text-slate-400"}`}
          >
            All
          </button>
          <button
            onClick={() => setShowFlagged(true)}
            className={`text-xs px-3 py-1 rounded-lg transition font-semibold ${showFlagged ? "bg-red-600 text-white" : "bg-slate-700 text-slate-400"}`}
          >
            🚩 Flagged
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm text-center py-8">Loading transactions...</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-slate-500 border-b border-slate-700">
                <th className="text-left py-2 pr-4">TX ID</th>
                <th className="text-left py-2 pr-4">Merchant</th>
                <th className="text-left py-2 pr-4">Amount</th>
                <th className="text-left py-2 pr-4">Country</th>
                <th className="text-left py-2 pr-4">Fraud %</th>
                <th className="text-left py-2">Reasons</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.tx_id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-2 pr-4 font-mono text-slate-300">{tx.tx_id}</td>
                  <td className="py-2 pr-4 text-slate-300">{tx.merchant}</td>
                  <td className="py-2 pr-4 text-white font-semibold">
                    ₹{tx.amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-2 pr-4">
                    <span className={`px-2 py-0.5 rounded-full text-xs ${tx.country === "IN" ? "bg-slate-700 text-slate-300" : "bg-orange-900/40 text-orange-300"}`}>
                      {tx.country}
                    </span>
                  </td>
                  <td className={`py-2 pr-4 font-bold ${tx.fraud_probability > 0.6 ? "text-red-400" : tx.fraud_probability > 0.3 ? "text-yellow-400" : "text-emerald-400"}`}>
                    {Math.round(tx.fraud_probability * 100)}%
                  </td>
                  <td className="py-2">
                    <div className="flex flex-wrap gap-1">
                      {tx.anomaly_reasons.slice(0, 2).map((r) => (
                        <span key={r} className="bg-red-900/30 text-red-300 border border-red-800/30 px-1.5 py-0.5 rounded text-xs">
                          {r.replace(/_/g, " ")}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {transactions.length === 0 && (
            <p className="text-slate-500 text-sm text-center py-8">No transactions found.</p>
          )}
        </div>
      )}
    </div>
  );
}
