// src/pages/Dashboard.jsx — FraudGraph
// Adapted from FinFlow360's Dashboard.jsx
import { useEffect, useState } from "react";
import { api } from "../api";
import FraudScore from "../components/FraudScore";
import AgentPanel from "../components/AgentPanel";
import TransactionFeed from "../components/TransactionFeed";
import FraudCases from "../components/FraudCases";
import RiskChart from "../components/RiskChart";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [accounts, setAccounts] = useState([]);

  useEffect(() => {
    api.getDashboardSummary().then((r) => setSummary(r.data));
    api.getAccounts().then((r) => {
      setAccounts(r.data);
      // Auto-select first flagged account
      const flagged = r.data.find((a) => a.flagged);
      if (flagged) setSelectedAccount(flagged.account_id);
    });
  }, []);

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-red-600 flex items-center justify-center text-white font-bold text-sm">
              FG
            </div>
            <div>
              <h1 className="text-white font-bold text-lg leading-none">FraudGraph</h1>
              <p className="text-slate-500 text-xs">Agentic Fraud Detection · Powered by Jac Walkers</p>
            </div>
          </div>

          {/* Account Selector */}
          <div className="flex items-center gap-3">
            <label className="text-slate-400 text-xs">Active Account:</label>
            <select
              value={selectedAccount || ""}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="bg-slate-700 border border-slate-600 text-white text-xs rounded-lg px-3 py-1.5 focus:outline-none"
            >
              <option value="">Select account...</option>
              {accounts.map((a) => (
                <option key={a.account_id} value={a.account_id}>
                  {a.user_name} ({a.risk_tier.toUpperCase()}) — {a.account_id}
                </option>
              ))}
            </select>
            {selectedAccount && (
              <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                accounts.find(a => a.account_id === selectedAccount)?.risk_tier === "critical" ? "bg-red-600/20 text-red-300" :
                accounts.find(a => a.account_id === selectedAccount)?.risk_tier === "high" ? "bg-orange-600/20 text-orange-300" :
                "bg-slate-700 text-slate-300"
              }`}>
                {accounts.find(a => a.account_id === selectedAccount)?.risk_tier?.toUpperCase()}
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Stat Bar */}
      {summary && (
        <div className="border-b border-slate-800 bg-slate-800/50">
          <div className="max-w-7xl mx-auto px-6 py-3 flex items-center gap-8 text-xs">
            {[
              { label: "Total Accounts", value: summary.accounts.total, color: "text-white" },
              { label: "Flagged",        value: summary.accounts.flagged, color: "text-red-400" },
              { label: "Transactions",   value: summary.transactions.total, color: "text-white" },
              { label: "Suspicious Tx",  value: summary.transactions.flagged, color: "text-orange-400" },
              { label: "Flag Rate",      value: `${summary.transactions.flag_rate}%`, color: "text-yellow-400" },
              { label: "Open Cases",     value: summary.cases.open, color: "text-red-400" },
              { label: "Critical Cases", value: summary.cases.critical, color: "text-red-500 font-black" },
            ].map(({ label, value, color }) => (
              <div key={label} className="flex flex-col">
                <span className={`font-bold text-sm ${color}`}>{value}</span>
                <span className="text-slate-500">{label}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Grid */}
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* Row 1: Score + Agent Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <FraudScore accountId={selectedAccount} />
          </div>
          <div className="lg:col-span-3">
            <AgentPanel accountId={selectedAccount} />
          </div>
        </div>

        {/* Row 2: Risk Chart */}
        <RiskChart onSelectAccount={setSelectedAccount} />

        {/* Row 3: Transactions + Cases */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <TransactionFeed />
          </div>
          <div className="lg:col-span-1">
            <FraudCases />
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-800 mt-8 py-4 text-center">
        <p className="text-slate-600 text-xs">
          FraudGraph · Agentic Fraud Detection Engine · Built with Jac + Jaseci for JacHacks 2026
        </p>
      </footer>
    </div>
  );
}
