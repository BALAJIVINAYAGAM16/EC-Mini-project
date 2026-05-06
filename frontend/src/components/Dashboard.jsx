import { useEffect, useState } from "react";
import API from "../api/axios";

export default function Dashboard() {
  const [summary, setSummary] = useState({});
  const [taskData, setTaskData] = useState([]);
  const [approvalStats, setApprovalStats] = useState({});

  useEffect(() => {
    async function fetchData() {
      const [s, t, a] = await Promise.all([
        API.get("/dashboard/summary"),
        API.get("/dashboard/task-distribution"),
        API.get("/dashboard/approvals"),
      ]);

      setSummary(s.data);
      setTaskData(t.data);
      setApprovalStats(a.data);
    }
    fetchData();
  }, []);

  const total = summary.total_tasks || 1;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 p-6">
      <h1 className="text-3xl font-bold text-slate-700 mb-8">
        Dashboard
      </h1>

      {/* 🔷 STAT CARDS */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        {[
          {
            label: "Total Tasks",
            value: summary.total_tasks || 0,
            color: "bg-slate-800",
          },
          {
            label: "Pending",
            value: summary.pending_tasks || 0,
            color: "bg-amber-500",
          },
          {
            label: "Completed",
            value: summary.completed_tasks || 0,
            color: "bg-emerald-500",
          },
          {
            label: "Approvals",
            value: summary.pending_approvals || 0,
            color: "bg-cyan-600",
          },
        ].map((card, i) => (
          <div
            key={i}
            className="bg-white/70 backdrop-blur-md p-5 rounded-2xl shadow-md"
          >
            <p className="text-slate-500 text-sm">{card.label}</p>

            <h2 className="text-2xl font-bold text-slate-800 mb-3">
              {card.value}
            </h2>

            {/* progress */}
            <div className="h-2 bg-slate-200 rounded">
              <div
                className={`${card.color} h-2 rounded`}
                style={{ width: `${(card.value / total) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* 📊 TASK STATUS */}
      <div className="bg-white/70 backdrop-blur-md p-6 rounded-2xl shadow-md mb-8">
        <h2 className="font-semibold text-slate-700 mb-4">
          Task Status
        </h2>

        <div className="flex flex-wrap gap-3">
          {taskData.map((item) => (
            <div
              key={item.status}
              className="px-4 py-2 rounded-full bg-slate-200 text-slate-700 text-sm flex items-center gap-2"
            >
              {item.status}
              <span className="bg-slate-800 text-white text-xs px-2 py-0.5 rounded-full">
                {item.count}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* 📋 APPROVAL STATS */}
      <div className="grid md:grid-cols-3 gap-6">
        {[
          { label: "Approved", value: approvalStats.approved, color: "text-emerald-600" },
          { label: "Rejected", value: approvalStats.rejected, color: "text-red-500" },
          { label: "Pending", value: approvalStats.pending, color: "text-amber-500" },
        ].map((stat, i) => (
          <div
            key={i}
            className="bg-white/70 backdrop-blur-md p-5 rounded-2xl shadow-md text-center"
          >
            <p className="text-slate-500">{stat.label}</p>
            <h2 className={`text-2xl font-bold ${stat.color}`}>
              {stat.value || 0}
            </h2>
          </div>
        ))}
      </div>
    </div>
  );
}