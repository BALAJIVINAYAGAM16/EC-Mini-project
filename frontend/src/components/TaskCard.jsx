// src/components/TaskCard.jsx
import { useState } from "react";
import Comments from "./Comments";

export default function TaskCard({ task }) {
  const [showComments, setShowComments] = useState(false);

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "HIGH":
        return "bg-red-500";
      case "MEDIUM":
        return "bg-yellow-500";
      case "LOW":
        return "bg-green-500";
      default:
        return "bg-gray-400";
    }
  };

  return (
    <div className="bg-white p-3 mb-3 rounded-xl shadow hover:shadow-md transition">
      
      {/* Title */}
      <h3 className="font-semibold text-gray-800">{task.title}</h3>

      {/* Description */}
      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
        {task.description}
      </p>

      {/* Priority + Status */}
      <div className="flex justify-between items-center mt-3">
        
        {/* Priority Badge */}
        <span
          className={`text-xs text-white px-2 py-1 rounded ${getPriorityColor(
            task.priority
          )}`}
        >
          {task.priority || "NORMAL"}
        </span>

        {/* Status */}
        <span className="text-xs text-gray-600">
          {task.status}
        </span>
      </div>

      {/* Assigned User */}
      <div className="mt-2 text-xs text-gray-500">
        👤 {task.assigned_to || "Unassigned"}
      </div>

      {/* Footer */}
      <div className="flex justify-between items-center mt-3">
        
        {/* Created Date */}
        <span className="text-xs text-gray-400">
          {new Date(task.created_at).toLocaleDateString()}
        </span>

        {/* Comments Button */}
        <button
          onClick={() => setShowComments(!showComments)}
          className="text-blue-500 text-xs hover:underline"
        >
          💬 Comments
        </button>
      </div>

      {/* Comments Section */}
      {showComments && (
        <div className="mt-3 border-t pt-2">
          <Comments taskId={task.id} />
        </div>
      )}
    </div>
  );
}