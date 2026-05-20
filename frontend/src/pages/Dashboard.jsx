import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import API from "../api/axios";
import { assignTask, deleteTask } from "../api/taskApi";

import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import DashboardInsights from "../components/Dashboard";
import UserSelect from "../components/UserSelect";
import CreditCard from "../components/CreditCard";

export default function Dashboard() {

  const [tasks, setTasks] = useState([]);

  const [currentUser, setCurrentUser] =
    useState(null);

  const navigate = useNavigate();

  const fetchTasks = async () => {

    try {

      const res = await API.get("/tasks");

      setTasks(
        Array.isArray(res.data)
          ? res.data
          : res.data.tasks || []
      );

    } catch (err) {

      console.error(
        "Error fetching tasks:",
        err
      );

    }
  };

  useEffect(() => {

    const loadTasks = async () => {

      try {

        const res = await API.get("/tasks");

        setTasks(
          Array.isArray(res.data)
            ? res.data
            : res.data.tasks || []
        );

      } catch (err) {

        console.error(
          "Error fetching tasks:",
          err
        );

      }
    };

    const loadCurrentUser = async () => {

      try {

        const res = await API.get("/auth/me");

        setCurrentUser(res.data);

      } catch (err) {

        console.error(
          "Error fetching current user:",
          err
        );

      }
    };

    loadCurrentUser();

    loadTasks();

  }, []);

  const canManageTasks =
    currentUser?.role === "admin" ||
    currentUser?.role === "manager";

  const handleAssign = async (
    taskId,
    userId
  ) => {

    try {

      await assignTask(
        taskId,
        Number(userId)
      );

      alert("Task assigned!");

      await fetchTasks();

    } catch (err) {

      console.error(
        "Assign error:",
        err
      );

      alert("Failed to assign task");

    }
  };

  const handleEdit = (task) => {

    navigate(`/edit/${task.id}`, {
      state: task,
    });

  };

  const handleDelete = async (id) => {

    if (
      !window.confirm(
        "Are you sure you want to delete this task?"
      )
    ) {
      return;
    }

    try {

      await deleteTask(id);

      alert("Task deleted!");

      await fetchTasks();

    } catch (err) {

      console.error(
        "Delete error:",
        err
      );

      alert("Failed to delete task");

    }
  };

  return (

    <div className="flex bg-slate-100 min-h-screen">

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">

        {/* Navbar */}
        <Navbar />

        <div className="p-6 md:p-8">

          {/* Top SaaS Cards */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">

            <CreditCard
              credits={
                currentUser?.credits || 450
              }
            />

            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">

              <h2 className="text-lg font-semibold text-slate-700">
                Current Plan
              </h2>

              <p className="mt-4 text-3xl font-bold text-indigo-600">
                {currentUser?.plan || "Silver"}
              </p>

              <p className="mt-2 text-sm text-slate-500">
                Active subscription
              </p>

            </div>

            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">

              <h2 className="text-lg font-semibold text-slate-700">
                Organization
              </h2>

              <p className="mt-4 text-2xl font-bold text-slate-800">
                {currentUser?.organization ||
                  "Acme Corp"}
              </p>

              <p className="mt-2 text-sm text-slate-500">
                Multi-tenant workspace
              </p>

            </div>

          </div>

          {/* Dashboard Insights */}
          <div className="mb-8">
            <DashboardInsights />
          </div>

          {/* Header */}
          <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">

            <div>

              <h2 className="text-3xl font-bold text-slate-800">
                Tasks
              </h2>

              <p className="text-slate-500 mt-1">
                Manage project workflows
              </p>

            </div>

            <div className="flex gap-3">

              <Link
                to="/register"
                className="rounded-xl bg-green-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-green-700 shadow"
              >
                Register User
              </Link>

              {canManageTasks && (
                <Link
                  to="/create"
                  className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-indigo-700 shadow"
                >
                  Create Task
                </Link>
              )}

            </div>

          </div>

          {/* Tasks */}
          {tasks.length === 0 ? (

            <div className="mt-16 text-center">

              <div className="bg-white rounded-2xl border border-slate-200 p-10 shadow-sm max-w-lg mx-auto">

                <h3 className="text-xl font-semibold text-slate-700">
                  No Tasks Found
                </h3>

                <p className="mt-2 text-slate-500">
                  Create your first task to get started.
                </p>

              </div>

            </div>

          ) : (

            <div className="grid gap-5">

              {tasks.map((task) => (

                <div
                  key={task.id}
                  className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition"
                >

                  {/* Title */}
                  <div className="flex justify-between items-start gap-4">

                    <div>

                      <h3 className="text-xl font-semibold text-slate-800">
                        {task.title}
                      </h3>

                      <p className="mt-2 text-sm text-slate-600">
                        {task.description ||
                          "No description"}
                      </p>

                    </div>

                    {/* Status */}
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium
                      ${
                        task.status === "todo"
                          ? "bg-yellow-100 text-yellow-700"
                          : ""
                      }
                      ${
                        task.status === "in_progress"
                          ? "bg-blue-100 text-blue-700"
                          : ""
                      }
                      ${
                        task.status === "done"
                          ? "bg-green-100 text-green-700"
                          : ""
                      }
                    `}
                    >
                      {task.status}
                    </span>

                  </div>

                  {/* Assign */}
                  <div className="mt-5">

                    <label className="block text-xs font-medium text-slate-500 mb-2">
                      Assign User
                    </label>

                    <UserSelect
                      value={task.assigned_to_id}
                      onChange={(val) =>
                        handleAssign(
                          task.id,
                          val
                        )
                      }
                    />

                  </div>

                  {/* Actions */}
                  {canManageTasks && (

                    <div className="mt-6 flex gap-3">

                      <button
                        onClick={() =>
                          handleEdit(task)
                        }
                        className="rounded-xl bg-yellow-400 px-4 py-2 text-sm font-medium text-black hover:bg-yellow-500 transition"
                      >
                        Edit
                      </button>

                      <button
                        onClick={() =>
                          handleDelete(task.id)
                        }
                        className="rounded-xl bg-red-500 px-4 py-2 text-sm font-medium text-white hover:bg-red-600 transition"
                      >
                        Delete
                      </button>

                    </div>

                  )}

                </div>

              ))}

            </div>

          )}

        </div>

      </div>

    </div>

  );
}