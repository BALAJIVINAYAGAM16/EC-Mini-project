import { useEffect, useState } from "react";
import API from "../api/axios";

export default function Comments({ taskId }) {
  const [comments, setComments] = useState([]);
  const [content, setContent] = useState("");
  const [isInternal, setIsInternal] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!taskId) return;
    let ignore = false;

    async function fetchComments() {
      try {
        const res = await API.get(`/tasks/${taskId}/comments`);
        if (!ignore) setComments(res.data);
      } catch (err) {
        console.error(err);
        if (!ignore) setError("Unable to load comments.");
      }
    }

    fetchComments();
    return () => {
      ignore = true;
    };
  }, [taskId]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!content.trim()) return;

    try {
      const res = await API.post(`/tasks/${taskId}/comments`, {
        content,
        is_internal: isInternal,
      });

      setComments((current) => [res.data, ...current]);
      setContent("");
      setIsInternal(false);
      setError("");
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Unable to add comment.");
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow w-full">
      <h2 className="text-lg font-semibold mb-4">Comments</h2>
      {error && <p className="mb-3 text-sm text-red-600">{error}</p>}

      <div className="space-y-3 max-h-80 overflow-y-auto mb-4">
        {comments.map((comment) => (
          <div
            key={comment.id}
            className={`p-3 rounded-lg ${
              comment.is_internal
                ? "bg-yellow-100 border-l-4 border-yellow-500"
                : "bg-gray-100"
            }`}
          >
            <p className="text-sm">{comment.content}</p>

            <div className="text-xs text-gray-500 mt-1">
              User: {comment.user_id} |{" "}
              {new Date(comment.created_at).toLocaleString()}
            </div>

            {comment.is_internal && (
              <span className="text-xs text-yellow-700 font-semibold">
                Internal Note
              </span>
            )}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <textarea
          className="w-full border p-2 rounded mb-2"
          placeholder="Write a comment..."
          value={content}
          onChange={(event) => setContent(event.target.value)}
        />

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={isInternal}
              onChange={(event) => setIsInternal(event.target.checked)}
            />
            Internal
          </label>

          <button className="bg-blue-500 text-white px-4 py-2 rounded">
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
