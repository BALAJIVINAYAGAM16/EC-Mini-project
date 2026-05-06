import { useState } from "react";
import Comments from "./Comments";

export default function TaskCard({ task }) {
  const [showComments, setShowComments] = useState(false);

  const getPriorityColor = (priority) => {
    switch ((priority || "").toLowerCase()) {
      case "high":
        return "bg-red-500";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-green-500";
      default:
        return "bg-gray-400";
    }
  };

  return (
    <div className="bg-white p-3 rounded-lg shadow hover:shadow-md transition">
      <h3 className="font-semibold text-gray-800">{task.title}</h3>

      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
        {task.description || "No description"}
      </p>

      <div className="flex justify-between items-center mt-3">
        <span
          className={`text-xs text-white px-2 py-1 rounded ${getPriorityColor(
            task.priority
          )}`}
        >
          {task.priority || "medium"}
        </span>

        <span className="text-xs text-gray-600">{task.status}</span>
      </div>

      <div className="mt-2 text-xs text-gray-500">
        Assigned to: {task.assigned_to_name || "Unassigned"}
      </div>

      <div className="flex justify-between items-center mt-3">
        <span className="text-xs text-gray-400">
          {task.created_at
            ? new Date(task.created_at).toLocaleDateString()
            : "No date"}
        </span>

        <button
          type="button"
          onClick={() => setShowComments((value) => !value)}
          className="text-blue-500 text-xs hover:underline"
        >
          Comments
        </button>
      </div>

      {showComments && (
        <div className="mt-3 border-t pt-2">
          <Comments taskId={task.id} />
        </div>
      )}
    </div>
  );
}
