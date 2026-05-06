// components/Comments.jsx
import { useEffect, useState } from "react";
import API from "../api/axios";

export default function Comments({ taskId }) {
  const [comments, setComments] = useState([]);
  const [text, setText] = useState("");

  useEffect(() => {
    fetchComments();
  }, []);

  const fetchComments = async () => {
    const res = await API.get(`/tasks/${taskId}/comments`);
    setComments(res.data);
  };

  const addComment = async () => {
    await API.post(`/tasks/${taskId}/comments`, {
      content: text,
      is_internal: false,
    });
    setText("");
    fetchComments();
  };

  return (
    <div className="p-4">
      <h3 className="font-bold mb-2">Comments</h3>

      <div className="space-y-2">
        {comments.map((c) => (
          <div key={c.id} className="bg-gray-100 p-2 rounded">
            <p>{c.content}</p>
            <small>{c.created_at}</small>
          </div>
        ))}
      </div>

      <div className="mt-3 flex gap-2">
        <input
          className="border p-2 w-full"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button
          onClick={addComment}
          className="bg-blue-500 text-white px-3 rounded"
        >
          Add
        </button>
      </div>
    </div>
  );
}