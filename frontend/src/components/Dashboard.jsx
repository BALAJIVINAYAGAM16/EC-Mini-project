import { useEffect, useState } from "react";
import API from "../api/axios";

import Sidebar from "../components/Sidebar";
import AISummaryCard from "../components/AISummaryCard";
import ActivityFeed from "../components/ActivityFeed";

export default function Dashboard() {
  const [summary, setSummary] = useState({});
  const [taskData, setTaskData] = useState([]);
  const [approvalStats, setApprovalStats] =
    useState({});

  useEffect(() => {
    async function fetchData() {
      try {
        const [s, t, a] = await Promise.all([
          API.get("/dashboard/summary"),
          API.get(
            "/dashboard/task-distribution"
          ),
          API.get("/dashboard/approvals"),
        ]);

        setSummary(s.data);
        setTaskData(t.data);
        setApprovalStats(a.data);
      } catch (error) {
        console.error(
          "Dashboard fetch error:",
          error
        );
      }
    }

    fetchData();
  }, []);

  const total = summary.total_tasks || 1;

  return (
    <div className="flex min-h-screen bg-slate-100">
      
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 p-6">
        
        {/* Header */}
        <div className="flex items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-800">
              Dashboard
            </h1>

            <p className="text-slate-500 mt-1">
              Enterprise Workflow Overview
            </p>
          </div>
        </div>

        {/* AI INSIGHTS SECTION */}
        <div className="bg-gradient-to-r from-purple-500 to-indigo-600 p-6 rounded-2xl shadow-lg mb-8 text-white">
          <div className="flex items-start gap-4">
            <div className="text-4xl">🤖</div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-2">AI Insights</h2>
              <p className="text-purple-100 mb-3">
                {summary.ai_summary || "Analyzing your workflow..."}
              </p>
              <div className="flex gap-4 flex-wrap">
                <div className="bg-white/20 px-3 py-1 rounded-full text-sm">
                  ⚠️ {summary.delayed_tasks || 0} delayed
                </div>
                <div className="bg-white/20 px-3 py-1 rounded-full text-sm">
                  🔴 {summary.high_priority_tasks || 0} high priority
                </div>
                <div className="bg-white/20 px-3 py-1 rounded-full text-sm">
                  ⏳ {summary.pending_tasks || 0} pending
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* AI SUMMARY CARDS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <AISummaryCard
            title="📋 Pending Tasks"
            value={
              summary.pending_tasks || 0
            }
          />

          <AISummaryCard
            title="🔴 High Priority"
            value={
              summary.high_priority_tasks || 0
            }
          />

          <AISummaryCard
            title="⏰ Delayed Tasks"
            value={
              summary.delayed_tasks || 0
            }
          />
        </div>

        {/* STATISTICS CARDS */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          {[
            {
              label: "Total Tasks",
              value:
                summary.total_tasks || 0,
              color: "bg-slate-800",
              emoji: "📊"
            },
            {
              label: "Pending",
              value:
                summary.pending_tasks || 0,
              color: "bg-amber-500",
              emoji: "⏳"
            },
            {
              label: "Completed",
              value:
                summary.completed_tasks ||
                0,
              color: "bg-emerald-500",
              emoji: "✅"
            },
            // {
            //   label: "Approvals",
            //   value:
            //     summary.pending_approvals ||
            //     0,
            //   color: "bg-cyan-600",
            //   emoji: "🔔"
            // },
          ].map((card, i) => (
            <div
              key={i}
              className="bg-white/80 backdrop-blur-md p-5 rounded-2xl shadow-md hover:shadow-lg transition"
            >
              <p className="text-slate-500 text-sm flex items-center gap-2">
                <span className="text-xl">{card.emoji}</span>
                {card.label}
              </p>

              <h2 className="text-2xl font-bold text-slate-800 mb-3">
                {card.value}
              </h2>

              {/* Progress */}
              <div className="h-2 bg-slate-200 rounded">
                <div
                  className={`${card.color} h-2 rounded transition`}
                  style={{
                    width: `${
                      (card.value / total) *
                      100
                    }%`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* TASK STATUS */}
        <div className="bg-white/80 backdrop-blur-md p-6 rounded-2xl shadow-md mb-8">
          <h2 className="font-semibold text-slate-700 mb-4 text-lg">
            📈 Task Status Distribution
          </h2>

          <div className="flex flex-wrap gap-3">
            {taskData && taskData.length > 0 ? (
              taskData.map((item) => (
                <div
                  key={item.status}
                  className="px-4 py-2 rounded-full bg-slate-200 text-slate-700 text-sm flex items-center gap-2 hover:bg-slate-300 transition"
                >
                  {item.status}

                  <span className="bg-slate-800 text-white text-xs px-2 py-0.5 rounded-full">
                    {item.count}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-slate-500">No task data available</p>
            )}
          </div>
        </div>

        {/* APPROVAL STATS */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {[
            {
              label: "✅ Approved",
              value:
                approvalStats.approved || 0,
              color:
                "text-emerald-600",
              bgColor: "bg-emerald-50"
            },
            {
              label: "❌ Rejected",
              value:
                approvalStats.rejected || 0,
              color: "text-red-500",
              bgColor: "bg-red-50"
            },
            {
              label: "⏳ Pending",
              value:
                approvalStats.pending || 0,
              color:
                "text-amber-500",
              bgColor: "bg-amber-50"
            },
          ].map((stat, i) => (
            <div
              key={i}
              className={`${stat.bgColor} backdrop-blur-md p-5 rounded-2xl shadow-md text-center border border-slate-200`}
            >
              <p className="text-slate-600 font-medium">
                {stat.label}
              </p>

              <h2
                className={`text-3xl font-bold ${stat.color} mt-2`}
              >
                {stat.value}
              </h2>
            </div>
          ))}
        </div>

        {/* ACTIVITY FEED */}
        <div className="mb-8">
          <ActivityFeed />
        </div>
      </div>
    </div>
  );
}
