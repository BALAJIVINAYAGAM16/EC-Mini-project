import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div className="w-64 h-screen bg-gray-900 text-white p-5">
      <h1 className="text-2xl font-bold mb-10">
        Enterprise System
      </h1>

      <div className="space-y-4">
        <Link to="/" className="block hover:text-blue-400">
          Dashboard
        </Link>

        <Link to="/documents" className="block hover:text-blue-400">
          Documents
        </Link>

        <Link to="/kanban" className="block hover:text-blue-400">
          Kanban
        </Link>

        <Link to="/notifications" className="block hover:text-blue-400">
          Notifications
        </Link>

        <Link to="/audit-logs" className="block hover:text-blue-400">
          Audit Logs
        </Link>

        <Link to="/ai-insights" className="block hover:text-blue-400">
          AI Insights
        </Link>
      </div>
    </div>
  );
}
