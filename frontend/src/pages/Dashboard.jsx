import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api/axios";
import { assignTask, deleteTask } from "../api/taskApi";
import Navbar from "../components/Navbar";
import UserSelect from "../components/UserSelect";

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const navigate = useNavigate();

  const fetchTasks = async () => {
    try {
      const res = await API.get("/tasks");
      setTasks(Array.isArray(res.data) ? res.data : res.data.tasks || []);
    } catch (err) {
      console.error("Error fetching tasks:", err);
    }
  };

  useEffect(() => {
    const loadTasks = async () => {
      try {
        const res = await API.get("/tasks");
        setTasks(Array.isArray(res.data) ? res.data : res.data.tasks || []);
      } catch (err) {
        console.error("Error fetching tasks:", err);
      }
    };

    const loadCurrentUser = async () => {
      try {
        const res = await API.get("/auth/me");
        setCurrentUser(res.data);
      } catch (err) {
        console.error("Error fetching current user:", err);
      }
    };

    loadCurrentUser();
    loadTasks();
  }, []);

  const canManageTasks =
    currentUser?.role === "admin" || currentUser?.role === "manager";

  const handleAssign = async (taskId, userId) => {
    try {
      await assignTask(taskId, Number(userId));
      alert("Task assigned!");
      await fetchTasks();
    } catch (err) {
      console.error("Assign error:", err);
      alert("Failed to assign task");
    }
  };

  const handleEdit = (task) => {
    navigate(`/edit/${task.id}`, { state: task });
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this task?")) {
      return;
    }

    try {
      await deleteTask(id);
      alert("Task deleted!");
      await fetchTasks();
    } catch (err) {
      console.error("Delete error:", err);
      alert("Failed to delete task");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />

      <div className="p-6">
        <div className="mb-6 flex items-center justify-between gap-4">
          <h2 className="text-2xl font-bold text-gray-800">Tasks</h2>
          <Link
            to="/register"
            className="rounded bg-green-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-700"
          >
            Register
          </Link>
        </div>

        {tasks.length === 0 ? (
          <div className="mt-10 text-center text-gray-500">No tasks found</div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className="mb-4 rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition hover:shadow-md"
            >
              <h3 className="text-lg font-semibold text-gray-800">{task.title}</h3>

              <p className="mt-1 text-sm text-gray-600">
                {task.description || "No description"}
              </p>

              <p className="mt-2 text-sm">
                <span className="font-medium text-gray-700">Status:</span>{" "}
                <span
                  className={`ml-1 rounded px-2 py-1 text-xs
                    ${task.status === "todo" ? "bg-yellow-100 text-yellow-700" : ""}
                    ${task.status === "in_progress" ? "bg-blue-100 text-blue-700" : ""}
                    ${task.status === "done" ? "bg-green-100 text-green-700" : ""}
                  `}
                >
                  {task.status}
                </span>
              </p>

              <div className="mt-4">
                <label className="mb-1 block text-xs text-gray-500">Assign User</label>
                <UserSelect
                  value={task.assigned_to_id}
                  onChange={(val) => handleAssign(task.id, val)}
                />
              </div>

              {canManageTasks && (
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={() => handleEdit(task)}
                    className="rounded bg-yellow-400 px-3 py-1 text-black hover:bg-yellow-500"
                  >
                    Edit
                  </button>

                  <button
                    onClick={() => handleDelete(task.id)}
                    className="rounded bg-red-500 px-3 py-1 text-white hover:bg-red-600"
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
