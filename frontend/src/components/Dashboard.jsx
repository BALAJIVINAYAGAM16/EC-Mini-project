// components/Dashboard.jsx
import { useEffect, useState } from "react";
import API from "../api/axios";

export default function Dashboard() {
  const [data, setData] = useState({});

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    const res = await API.get("/dashboard/summary");
    setData(res.data);
  };

  return (
    <div className="grid grid-cols-4 gap-4 p-4">
      <div className="bg-blue-500 text-white p-4 rounded">
        Total Tasks: {data.total_tasks}
      </div>

      <div className="bg-yellow-500 text-white p-4 rounded">
        Pending: {data.pending}
      </div>

      <div className="bg-green-500 text-white p-4 rounded">
        Completed: {data.completed}
      </div>

      <div className="bg-purple-500 text-white p-4 rounded">
        Approvals: {data.approvals}
      </div>
    </div>
  );
}