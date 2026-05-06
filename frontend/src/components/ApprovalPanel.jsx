// components/ApprovalPanel.jsx
import { useEffect, useState } from "react";
import API from "../api/axios";

export default function ApprovalPanel() {
  const [approvals, setApprovals] = useState([]);

  useEffect(() => {
    fetchApprovals();
  }, []);

  const fetchApprovals = async () => {
    const res = await API.get("/approvals/");
    setApprovals(res.data);
  };

  const handleAction = async (id, action) => {
    const comment = prompt("Enter comment");

    await API.patch(`/approvals/${id}/action`, {
      action,
      comment,
    });

    fetchApprovals();
  };

  return (
    <div className="p-4">
      <h2 className="font-bold text-xl mb-3">Approvals</h2>

      {approvals.map((a) => (
        <div key={a.id} className="bg-white p-3 shadow mb-2 rounded">
          <p className="font-semibold">{a.title}</p>
          <p>Status: {a.status}</p>

          <div className="flex gap-2 mt-2">
            <button
              onClick={() => handleAction(a.id, "approve")}
              className="bg-green-500 text-white px-3 py-1 rounded"
            >
              Approve
            </button>

            <button
              onClick={() => handleAction(a.id, "reject")}
              className="bg-red-500 text-white px-3 py-1 rounded"
            >
              Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}