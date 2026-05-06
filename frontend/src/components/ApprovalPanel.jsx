import { useEffect, useState } from "react";
import API from "../api/axios";
import Navbar from "./Navbar";

export default function ApprovalPanel() {
  const [approvals, setApprovals] = useState([]);
  const [form, setForm] = useState({ title: "", description: "" });
  const [selectedHistory, setSelectedHistory] = useState([]);
  const [actionComments, setActionComments] = useState({});
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;

    async function fetchApprovals() {
      try {
        const res = await API.get("/approvals/");
        if (!ignore) setApprovals(res.data);
      } catch (err) {
        console.error(err);
        if (!ignore) setError("Unable to load approvals.");
      }
    }

    fetchApprovals();
    return () => {
      ignore = true;
    };
  }, []);

  const refreshApprovals = async () => {
    const res = await API.get("/approvals/");
    setApprovals(res.data);
  };

  const handleCreate = async (event) => {
    event.preventDefault();
    try {
      await API.post("/approvals/", form);
      setForm({ title: "", description: "" });
      setError("");
      await refreshApprovals();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Unable to create approval.");
    }
  };

  const handleAction = async (id, action) => {
    try {
      await API.patch(`/approvals/${id}/action`, {
        action,
        comment: actionComments[id] || null,
      });
      setActionComments((current) => ({ ...current, [id]: "" }));
      setError("");
      await refreshApprovals();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Unable to update approval.");
    }
  };

  const fetchHistory = async (id) => {
    try {
      const res = await API.get(`/approvals/${id}/history`);
      setSelectedHistory(res.data);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Unable to load approval history.");
    }
  };

  return (
    <div className="bg-gray-100 min-h-screen">
      <Navbar />
      <main className="p-6">
        <h1 className="text-2xl font-bold mb-6">Approval System</h1>
        {error && <div className="mb-4 rounded bg-red-100 p-3 text-sm text-red-700">{error}</div>}

        <form onSubmit={handleCreate} className="bg-white p-4 rounded-lg shadow mb-6">
        <h2 className="font-semibold mb-3">Create Approval</h2>

        <input
          type="text"
          placeholder="Title"
          className="w-full p-2 border rounded mb-3"
          value={form.title}
          onChange={(event) => setForm({ ...form, title: event.target.value })}
          required
        />

        <textarea
          placeholder="Description"
          className="w-full p-2 border rounded mb-3"
          value={form.description}
          onChange={(event) =>
            setForm({ ...form, description: event.target.value })
          }
        />

        <button className="bg-blue-500 text-white px-4 py-2 rounded">
          Submit
        </button>
        </form>

        <div className="grid gap-4">
        {approvals.map((item) => (
          <div key={item.id} className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold">{item.title}</h3>
            <p className="text-gray-600">{item.description || "No description"}</p>

            <div className="mt-2 text-sm">
              <span className="font-medium">Status:</span> {item.status}
              <span className="ml-4 font-medium">Level:</span> {item.current_level}
            </div>

            <textarea
              placeholder="Action comment"
              className="mt-3 w-full rounded border p-2 text-sm"
              value={actionComments[item.id] || ""}
              onChange={(event) =>
                setActionComments({
                  ...actionComments,
                  [item.id]: event.target.value,
                })
              }
            />

            <div className="flex flex-wrap gap-2 mt-3">
              <button
                type="button"
                onClick={() => handleAction(item.id, "approve")}
                className="bg-green-500 text-white px-3 py-1 rounded"
              >
                Approve
              </button>

              <button
                type="button"
                onClick={() => handleAction(item.id, "reject")}
                className="bg-red-500 text-white px-3 py-1 rounded"
              >
                Reject
              </button>

              <button
                type="button"
                onClick={() => handleAction(item.id, "hold")}
                className="bg-yellow-500 text-white px-3 py-1 rounded"
              >
                Hold
              </button>

              <button
                type="button"
                onClick={() => fetchHistory(item.id)}
                className="bg-gray-500 text-white px-3 py-1 rounded"
              >
                History
              </button>
            </div>
          </div>
        ))}
        </div>

        {selectedHistory.length > 0 && (
          <div className="mt-6 bg-white p-4 rounded-lg shadow">
          <h2 className="font-semibold mb-3">Approval History</h2>

          {selectedHistory.map((history) => (
            <div key={history.id} className="border-b py-2">
              <p>Action: {history.action}</p>
              <p className="text-sm text-gray-500">By: {history.action_by}</p>
              {history.comment && (
                <p className="text-sm text-gray-600">{history.comment}</p>
              )}
              <p className="text-xs text-gray-400">
                {new Date(history.created_at).toLocaleString()}
              </p>
            </div>
          ))}
          </div>
        )}
      </main>
    </div>
  );
}
