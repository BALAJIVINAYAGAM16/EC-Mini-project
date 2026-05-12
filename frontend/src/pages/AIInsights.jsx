import { useEffect, useState } from "react";
import API from "../api/axios";
import Sidebar from "../components/Sidebar";

export default function AIInsights() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;

    API.get("/dashboard/ai-summary")
      .then((res) => {
        if (isMounted) {
          setSummary(res.data);
          setError("");
        }
      })
      .catch(() => {
        if (isMounted) {
          setError("Unable to load AI insights.");
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="flex">
      <Sidebar />

      <div className="flex-1 p-6">
        <h1 className="text-3xl font-bold mb-6">
          AI Insights
        </h1>

        <div className="bg-white p-6 rounded-xl shadow-md">
          {error ? (
            <p className="text-red-600">{error}</p>
          ) : (
            <>
              <p className="text-lg text-slate-700">
                {summary?.ai_summary || "Analyzing your workflow..."}
              </p>

              <div className="mt-6 grid gap-4 md:grid-cols-3">
                <div className="rounded-lg bg-amber-50 p-4">
                  <p className="text-sm text-amber-700">Pending tasks</p>
                  <p className="text-2xl font-bold text-amber-900">
                    {summary?.pending_tasks || 0}
                  </p>
                </div>
                <div className="rounded-lg bg-red-50 p-4">
                  <p className="text-sm text-red-700">High priority</p>
                  <p className="text-2xl font-bold text-red-900">
                    {summary?.high_priority_tasks || 0}
                  </p>
                </div>
                <div className="rounded-lg bg-blue-50 p-4">
                  <p className="text-sm text-blue-700">Delayed tasks</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {summary?.delayed_tasks || 0}
                  </p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
