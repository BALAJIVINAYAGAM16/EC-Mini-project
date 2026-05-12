import { useCallback, useEffect, useState } from "react";
import { Download, FileText, Trash2, Upload } from "lucide-react";
import { toast } from "../utils/toast";
import API from "../api/axios";
import { assignTask } from "../api/taskApi";
import { fetchAssignableUsers } from "../api/userApi";

const columns = [
  { key: "todo", title: "To Do", color: "border-slate-400" },
  { key: "in_progress", title: "In Progress", color: "border-cyan-500" },
  { key: "review", title: "Review", color: "border-amber-500" },
  { key: "done", title: "Done", color: "border-emerald-500" },
];

export default function KanbanBoard() {
  const [board, setBoard] = useState(() => createEmptyBoard());
  const [dragged, setDragged] = useState(null);
  const [users, setUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [documentsByTask, setDocumentsByTask] = useState({});
  const [uploadingTaskId, setUploadingTaskId] = useState(null);

  const canAssign =
    currentUser?.role === "admin" || currentUser?.role === "manager";

  const loadDocumentsForBoard = useCallback(async (nextBoard, shouldApply = () => true) => {
    const tasks = columns.flatMap((column) => nextBoard[column.key] || []);

    await Promise.all(
      tasks.map(async (task) => {
        try {
          const res = await API.get(`/documents/task/${task.id}`);
          if (shouldApply()) {
            setDocumentsByTask((cur) => ({
              ...cur,
              [task.id]: Array.isArray(res.data) ? res.data : [],
            }));
          }
        } catch {
          if (shouldApply()) {
            setDocumentsByTask((cur) => ({
              ...cur,
              [task.id]: [],
            }));
          }
        }
      })
    );
  }, []);

  useEffect(() => {
    let isMounted = true;

    Promise.all([
      API.get("/tasks/kanban"),
      API.get("/auth/me"),
    ])
      .then(([boardRes, userRes]) => {
        if (!isMounted) {
          return;
        }

        const nextBoard = normalizeBoard(boardRes.data);
        setBoard(nextBoard);
        setCurrentUser(userRes.data);
        loadDocumentsForBoard(nextBoard, () => isMounted);

        if (["admin", "manager"].includes(userRes.data.role)) {
          fetchAssignableUsers()
            .then((data) => {
              if (isMounted) {
                setUsers(Array.isArray(data) ? data : data.users || []);
              }
            })
            .catch(() => {
              toast.error("Failed to load assignable users");
            });
        }
      })
      .catch(() => {
        toast.error("Failed to load Kanban tasks");
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [loadDocumentsForBoard]);

  const refreshTaskDocuments = async (taskId) => {
    try {
      const res = await API.get(`/documents/task/${taskId}`);
      setDocumentsByTask((cur) => ({
        ...cur,
        [taskId]: Array.isArray(res.data) ? res.data : [],
      }));
    } catch {
      toast.error("Failed to load task documents");
    }
  };

  const handleDocumentUpload = async (taskId, file) => {
    if (!file) {
      return;
    }

    try {
      setUploadingTaskId(taskId);
      const formData = new FormData();
      formData.append("file", file);
      formData.append("task_id", taskId);

      await API.post("/documents/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      toast.success("Document uploaded");
      refreshTaskDocuments(taskId);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Document upload failed");
    } finally {
      setUploadingTaskId(null);
    }
  };

  const handleDocumentDownload = async (documentId, fileName) => {
    try {
      const res = await API.get(`/documents/${documentId}/download`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", fileName);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success("Document downloaded");
    } catch {
      toast.error("Document download failed");
    }
  };

  const handleDocumentDelete = async (taskId, documentId) => {
    if (!window.confirm("Delete this document?")) {
      return;
    }

    try {
      await API.delete(`/documents/${documentId}`);
      toast.success("Document deleted");
      refreshTaskDocuments(taskId);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Document delete failed");
    }
  };

  const handleDrop = async (status) => {
    if (!dragged || dragged.status === status) {
      setDragged(null);
      return;
    }

    const prev = board;
    const movedTask = { ...dragged, status };

    setBoard((cur) => {
      const updated = normalizeBoard(cur);
      updated[dragged.status] = updated[dragged.status].filter(
        (task) => task.id !== dragged.id
      );

      updated[status].unshift(movedTask);

      return updated;
    });

    try {
      await API.patch(`/tasks/${dragged.id}/status`, {
        status,
      });
    } catch {
      setBoard(prev);
      toast.error("Task status could not be updated");
    } finally {
      setDragged(null);
    }
  };

  const handleAssign = async (task, userId) => {
    if (!userId) {
      return;
    }

    const prev = board;
    const assignedToId = Number(userId);
    const assignedUser = users.find((user) => user.id === assignedToId);

    setBoard((cur) => updateTaskInBoard(cur, task.id, {
      assigned_to_id: assignedToId,
      assigned_to_name: assignedUser?.name || assignedUser?.email || null,
    }));

    try {
      const updatedTask = await assignTask(task.id, assignedToId);
      setBoard((cur) => updateTaskInBoard(cur, task.id, updatedTask));
      toast.success("Task assigned");
    } catch {
      setBoard(prev);
      toast.error("Failed to assign task");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 p-6">
        <p className="text-slate-500">Loading Kanban board...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 p-6">
      <h1 className="text-3xl font-bold text-slate-700 mb-6">
        Kanban Board
      </h1>

      <div className="flex gap-6 overflow-x-auto pb-4">

        {columns.map((col) => (
          <div
            key={col.key}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => handleDrop(col.key)}
            className={`min-w-[280px] bg-white/70 backdrop-blur-md 
            rounded-2xl shadow-md border-t-4 ${col.color}`}
          >
            {/* HEADER */}
            <div className="p-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-700">
                {col.title}
              </h2>
              <p className="text-xs text-slate-400">
                {board[col.key]?.length || 0} tasks
              </p>
            </div>

            {/* TASKS */}
            <div className="p-3 space-y-3 min-h-[400px]">
              {board[col.key]?.map((task) => (
                <div
                  key={task.id}
                  draggable
                  onDragStart={() => setDragged(task)}
                  className="p-3 rounded-xl bg-white shadow-sm border 
                  hover:shadow-md transition cursor-grab"
                >
                  <h3 className="font-semibold text-sm text-slate-700">
                    {task.title}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    {task.description || "No description"}
                  </p>

                  <div className="mt-3 flex items-center justify-between gap-2 text-xs text-slate-500">
                    <span>Priority: {task.priority}</span>
                    <span>#{task.id}</span>
                  </div>

                  <p className="mt-2 text-xs text-slate-500">
                    Assigned to:{" "}
                    <span className="font-medium text-slate-700">
                      {task.assigned_to_name ||
                        users.find((user) => user.id === task.assigned_to_id)
                          ?.email ||
                        "Unassigned"}
                    </span>
                  </p>

                  {canAssign && (
                    <label className="mt-3 block text-xs text-slate-500">
                      Assign task
                      <select
                        value={task.assigned_to_id || ""}
                        disabled={users.length === 0}
                        onMouseDown={(event) => event.stopPropagation()}
                        onClick={(event) => event.stopPropagation()}
                        onChange={(event) =>
                          handleAssign(task, event.target.value)
                        }
                        className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-2 py-2 text-sm text-slate-700"
                      >
                        <option value="">Unassigned</option>
                        {users.map((user) => (
                          <option key={user.id} value={user.id}>
                            {user.email} ({user.role})
                          </option>
                        ))}
                      </select>
                    </label>
                  )}

                  <div className="mt-4 border-t border-slate-100 pt-3">
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-600">
                        <FileText size={14} />
                        Documents
                      </div>
                      <label
                        onMouseDown={(event) => event.stopPropagation()}
                        onClick={(event) => event.stopPropagation()}
                        className={`inline-flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-600 transition hover:bg-slate-100 ${
                          uploadingTaskId === task.id
                            ? "cursor-wait opacity-60"
                            : "cursor-pointer"
                        }`}
                        title="Upload document"
                      >
                        <Upload size={15} />
                        <input
                          type="file"
                          className="hidden"
                          disabled={uploadingTaskId === task.id}
                          onChange={(event) => {
                            handleDocumentUpload(
                              task.id,
                              event.target.files?.[0]
                            );
                            event.target.value = "";
                          }}
                        />
                      </label>
                    </div>

                    <div className="space-y-2">
                      {(documentsByTask[task.id] || []).length === 0 ? (
                        <p className="text-xs text-slate-400">
                          No documents
                        </p>
                      ) : (
                        documentsByTask[task.id].map((doc) => (
                          <div
                            key={doc.id}
                            className="flex items-center justify-between gap-2 rounded-lg bg-slate-50 px-2 py-2"
                          >
                            <div className="min-w-0">
                              <p className="truncate text-xs font-medium text-slate-700">
                                {doc.file_name}
                              </p>
                              <p className="text-[11px] text-slate-500">
                                v{doc.version}
                              </p>
                            </div>
                            <div className="flex shrink-0 items-center gap-1">
                              <button
                                type="button"
                                onMouseDown={(event) => event.stopPropagation()}
                                onClick={(event) => {
                                  event.stopPropagation();
                                  handleDocumentDownload(doc.id, doc.file_name);
                                }}
                                className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-blue-600 transition hover:bg-blue-50"
                                title="Download document"
                              >
                                <Download size={15} />
                              </button>
                              <button
                                type="button"
                                onMouseDown={(event) => event.stopPropagation()}
                                onClick={(event) => {
                                  event.stopPropagation();
                                  handleDocumentDelete(task.id, doc.id);
                                }}
                                className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-red-600 transition hover:bg-red-50"
                                title="Delete document"
                              >
                                <Trash2 size={15} />
                              </button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

      </div>
    </div>
  );
}

function createEmptyBoard() {
  return columns.reduce((acc, column) => {
    acc[column.key] = [];
    return acc;
  }, {});
}

function normalizeBoard(data) {
  const board = createEmptyBoard();

  if (Array.isArray(data)) {
    data.forEach((task) => {
      const status = board[task.status] ? task.status : "todo";
      board[status].push(task);
    });
    return board;
  }

  columns.forEach((column) => {
    board[column.key] = Array.isArray(data?.[column.key])
      ? data[column.key]
      : [];
  });

  return board;
}

function updateTaskInBoard(board, taskId, changes) {
  const updated = normalizeBoard(board);

  columns.forEach((column) => {
    updated[column.key] = updated[column.key].map((task) =>
      task.id === taskId ? { ...task, ...changes } : task
    );
  });

  return updated;
}
