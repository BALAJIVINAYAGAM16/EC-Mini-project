import { useCallback, useEffect, useMemo, useState } from "react";
import API from "../api/axios";
import Sidebar from "../components/Sidebar";
import { toast } from "../utils/toast";

export default function AuditLog() {

  const [logs, setLogs] = useState([]);

  const [loading, setLoading] = useState(true);

  const [filter, setFilter] = useState("all");

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);

  const logsPerPage = 10;

  const fetchAuditLogs = useCallback(async () => {

    try {

      setLoading(true);

      const res = await API.get("/audit-logs/");

      setLogs(res.data);

    } catch {

      toast.error("Failed to fetch audit logs");

    } finally {

      setLoading(false);
    }
  }, []);

  useEffect(() => {

    fetchAuditLogs();

  }, [fetchAuditLogs]);

  const formatDate = (dateString) => {

    const date = new Date(dateString);

    return (
      date.toLocaleDateString() +
      " " +
      date.toLocaleTimeString()
    );
  };

  const getActionBadgeColor = (action) => {

    switch (action) {

      case "create":
        return "bg-green-100 text-green-800";

      case "update":
        return "bg-blue-100 text-blue-800";

      case "delete":
        return "bg-red-100 text-red-800";

      case "download":
        return "bg-yellow-100 text-yellow-800";

      case "upload":
        return "bg-purple-100 text-purple-800";

      case "assign":
        return "bg-indigo-100 text-indigo-800";

      case "approval_approve":
      case "approval_reject":
        return "bg-pink-100 text-pink-800";

      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getEntityIcon = (entity) => {

    switch (entity) {

      case "task":
        return "📝";

      case "document":
        return "📄";

      case "approval":
        return "✅";

      case "notification":
        return "🔔";

      case "comment":
        return "💬";

      default:
        return "🔄";
    }
  };

  // Filtered Logs
  const filteredLogs = useMemo(() => {

    return filter === "all"
      ? logs
      : logs.filter((log) => log.entity === filter);

  }, [logs, filter]);

  // Pagination Logic
  const totalPages = Math.ceil(
    filteredLogs.length / logsPerPage
  );

  const startIndex =
    (currentPage - 1) * logsPerPage;

  const endIndex =
    startIndex + logsPerPage;

  const paginatedLogs =
    filteredLogs.slice(startIndex, endIndex);

  // Reset page on filter change
  useEffect(() => {

    setCurrentPage(1);

  }, [filter]);

  return (
    <div className="flex">

      <Sidebar />

      <div className="flex-1 p-6 bg-gray-50 min-h-screen">

        {/* Header */}
        <h1 className="text-3xl font-bold mb-6">
          📊 Audit Logs
        </h1>

        {/* Filters */}
        <div className="bg-white p-4 rounded-xl shadow-md mb-6 flex flex-wrap gap-4">

          <div className="flex flex-wrap gap-2">

            {[
              "all",
              "task",
              "document",
              "approval",
            ].map((item) => (

              <button
                key={item}
                onClick={() => setFilter(item)}
                className={`px-4 py-2 rounded-lg transition capitalize ${
                  filter === item
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                {item}
              </button>
            ))}

          </div>

          {/* Refresh */}
          <div className="ml-auto">

            <button
              onClick={fetchAuditLogs}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              🔄 Refresh
            </button>

          </div>

        </div>

        {/* Table */}
        <div className="bg-white rounded-xl shadow-md overflow-hidden">

          <div className="px-6 py-4 bg-gray-100 border-b">

            <h2 className="text-lg font-semibold">
              Activity Log
            </h2>

            <p className="text-sm text-gray-600">
              Total: {filteredLogs.length}
            </p>

          </div>

          {loading ? (

            <div className="p-6 text-center">

              <p className="text-gray-500">
                Loading logs...
              </p>

            </div>

          ) : paginatedLogs.length === 0 ? (

            <div className="p-6 text-center">

              <p className="text-gray-500">
                No audit logs found
              </p>

            </div>

          ) : (

            <>
              <div className="overflow-x-auto">

                <table className="w-full">

                  <thead className="bg-gray-50 border-b">

                    <tr>

                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Timestamp
                      </th>

                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        User
                      </th>

                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Action
                      </th>

                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        Entity
                      </th>

                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                        ID
                      </th>

                    </tr>

                  </thead>

                  <tbody>

                    {paginatedLogs.map((log, idx) => (

                      <tr
                        key={idx}
                        className="border-b hover:bg-gray-50 transition"
                      >

                        <td className="px-6 py-4 text-sm font-medium">
                          {formatDate(log.timestamp)}
                        </td>

                        <td className="px-6 py-4 text-sm text-gray-600">
                          User #{log.user_id}
                        </td>

                        <td className="px-6 py-4 text-sm">

                          <span
                            className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getActionBadgeColor(log.action)}`}
                          >
                            {log.action.toUpperCase()}
                          </span>

                        </td>

                        <td className="px-6 py-4 text-sm">

                          <span className="flex items-center gap-2">
                            {getEntityIcon(log.entity)}
                            {log.entity}
                          </span>

                        </td>

                        <td className="px-6 py-4 text-sm text-blue-600 font-mono">
                          #{log.entity_id}
                        </td>

                      </tr>
                    ))}

                  </tbody>

                </table>

              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between px-6 py-4 border-t bg-gray-50">

                <p className="text-sm text-gray-600">

                  Showing{" "}
                  <span className="font-semibold">
                    {startIndex + 1}
                  </span>{" "}
                  to{" "}
                  <span className="font-semibold">
                    {Math.min(endIndex, filteredLogs.length)}
                  </span>{" "}
                  of{" "}
                  <span className="font-semibold">
                    {filteredLogs.length}
                  </span>{" "}
                  logs

                </p>

                <div className="flex gap-2">

                  {/* Previous */}
                  <button
                    disabled={currentPage === 1}
                    onClick={() =>
                      setCurrentPage((prev) => prev - 1)
                    }
                    className="px-4 py-2 rounded-lg border bg-white hover:bg-gray-100 disabled:opacity-50"
                  >
                    Previous
                  </button>

                  {/* Page Numbers */}
                  {[...Array(totalPages)].map((_, idx) => (

                    <button
                      key={idx}
                      onClick={() =>
                        setCurrentPage(idx + 1)
                      }
                      className={`px-4 py-2 rounded-lg ${
                        currentPage === idx + 1
                          ? "bg-blue-600 text-white"
                          : "bg-white border hover:bg-gray-100"
                      }`}
                    >
                      {idx + 1}
                    </button>
                  ))}

                  {/* Next */}
                  <button
                    disabled={currentPage === totalPages}
                    onClick={() =>
                      setCurrentPage((prev) => prev + 1)
                    }
                    className="px-4 py-2 rounded-lg border bg-white hover:bg-gray-100 disabled:opacity-50"
                  >
                    Next
                  </button>

                </div>

              </div>
            </>
          )}

        </div>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">

          {[
            {
              label: "Total Actions",
              value: logs.length,
              color: "bg-blue-500",
            },
            {
              label: "Tasks",
              value: logs.filter(
                (l) => l.entity === "task"
              ).length,
              color: "bg-green-500",
            },
            {
              label: "Documents",
              value: logs.filter(
                (l) => l.entity === "document"
              ).length,
              color: "bg-purple-500",
            },
            {
              label: "Approvals",
              value: logs.filter(
                (l) => l.entity === "approval"
              ).length,
              color: "bg-pink-500",
            },
          ].map((stat, idx) => (

            <div
              key={idx}
              className="bg-white p-4 rounded-xl shadow-md"
            >

              <p className="text-gray-600 text-sm">
                {stat.label}
              </p>

              <p
                className={`text-3xl font-bold text-white mt-2 ${stat.color} inline-block px-3 py-1 rounded-lg`}
              >
                {stat.value}
              </p>

            </div>
          ))}

        </div>

      </div>

    </div>
  );
}