import { useState, useEffect } from "react";
import API from "../api/axios";
import { useParams, useNavigate } from "react-router-dom";
import UserSelect from "../components/UserSelect";
import { assignTask } from "../api/taskApi";
import Navbar from "../components/Navbar";

export default function EditTask() {
  const { id } = useParams();
  const [form, setForm] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    API.get(`/tasks/${id}`).then(res => setForm(res.data));
  }, [id]);

  const handleUpdate = async (e) => {
    e.preventDefault();
    await API.put(`/tasks/${id}`, form);
    navigate("/");
  };

  const handleAssign = async () => {
    if (!form.assigned_to_id) {
      alert("Select a user first");
      return;
    }

    await assignTask(id, form.assigned_to_id);
    alert("Task assigned successfully");
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
        <form onSubmit={handleUpdate} className="rounded-2xl bg-white p-6 shadow-md space-y-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Edit task</h1>
            <p className="text-sm text-slate-500">Update task details and progress.</p>
          </div>

          <input
            value={form.title || ""}
            onChange={(e) =>
              setForm({ ...form, title: e.target.value })
            }
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-green-500"
          />

          <textarea
            value={form.description || ""}
            onChange={(e) =>
              setForm({ ...form, description: e.target.value })
            }
            className="min-h-32 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-green-500"
          />

          <div className="grid gap-4 md:grid-cols-2">
            <select
              value={form.status || "todo"}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-green-500"
            >
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="done">Done</option>
            </select>

            <select
              value={form.priority || "medium"}
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-green-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <button className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700 transition">
            Update Task
          </button>
        </form>

        <div className="rounded-2xl bg-white p-6 shadow-md">
          <h3 className="mb-3 text-lg font-bold text-slate-900">Assign task</h3>

          <UserSelect
            value={form.assigned_to_id}
            onChange={(val) =>
              setForm({ ...form, assigned_to_id: val })
            }
          />

          <button
            onClick={handleAssign}
            className="mt-3 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 transition"
          >
            Assign
          </button>
        </div>
      </div>
    </div>
  );
}
