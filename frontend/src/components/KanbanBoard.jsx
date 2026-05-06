import { useEffect, useState } from "react";
import API from "../api/axios";

const columns = [
  { key: "todo", title: "To Do", color: "border-slate-400" },
  { key: "in_progress", title: "In Progress", color: "border-cyan-500" },
  { key: "review", title: "Review", color: "border-amber-500" },
  { key: "done", title: "Done", color: "border-emerald-500" },
];

export default function KanbanBoard() {
  const [board, setBoard] = useState({});
  const [dragged, setDragged] = useState(null);

  useEffect(() => {
    API.get("/tasks/kanban").then((res) =>
      setBoard(res.data)
    );
  }, []);

  const handleDrop = async (status) => {
    if (!dragged) return;

    const prev = board;

    setBoard((cur) => {
      const updated = { ...cur };
      updated[dragged.status] = updated[
        dragged.status
      ].filter((t) => t.id !== dragged.id);

      dragged.status = status;
      updated[status].unshift(dragged);

      return updated;
    });

    try {
      await API.patch(`/tasks/${dragged.id}/status`, {
        status,
      });
    } catch {
      setBoard(prev);
    }
  };

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
                    {task.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ))}

      </div>
    </div>
  );
}