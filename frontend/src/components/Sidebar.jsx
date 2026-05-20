import { Link, useLocation } from "react-router-dom";

import {
  LayoutDashboard,
  FileText,
  KanbanSquare,
  Bell,
  ClipboardList,
  BrainCircuit,
  CreditCard,
  Building2,
  Settings,
} from "lucide-react";

export default function Sidebar() {

  const location = useLocation();

  const navClass = (path) =>
    `flex items-center gap-3 px-4 py-3 rounded-xl transition text-sm font-medium ${
      location.pathname === path
        ? "bg-white text-slate-900 shadow"
        : "text-slate-300 hover:bg-slate-800 hover:text-white"
    }`;

  return (
    <aside className="w-64 min-h-screen bg-slate-950 border-r border-slate-800 p-5">

      {/* Logo */}
      <div className="mb-10">

        <h1 className="text-2xl font-bold text-white tracking-tight">
          TaskFlow
        </h1>

        <p className="text-slate-400 text-sm mt-1">
          Enterprise SaaS Platform
        </p>

      </div>

      {/* Main Navigation */}
      <div className="space-y-2">

        <Link
          to="/"
          className={navClass("/")}
        >
          <LayoutDashboard size={18} />

          Dashboard
        </Link>

        <Link
          to="/documents"
          className={navClass("/documents")}
        >
          <FileText size={18} />

          Documents
        </Link>

        <Link
          to="/kanban"
          className={navClass("/kanban")}
        >
          <KanbanSquare size={18} />

          Kanban
        </Link>

        <Link
          to="/notifications"
          className={navClass("/notifications")}
        >
          <Bell size={18} />

          Notifications
        </Link>

        <Link
          to="/audit-logs"
          className={navClass("/audit-logs")}
        >
          <ClipboardList size={18} />

          Audit Logs
        </Link>

        <Link
          to="/ai-insights"
          className={navClass("/ai-insights")}
        >
          <BrainCircuit size={18} />

          AI Insights
        </Link>

      </div>

      {/* SaaS Section */}
      <div className="mt-10">

        <p className="text-xs uppercase tracking-widest text-slate-500 mb-4 px-2">
          SaaS Management
        </p>

        <div className="space-y-2">

          <Link
            to="/plans"
            className={navClass("/plans")}
          >
            <CreditCard size={18} />

            Plans
          </Link>

          <Link
            to="/billing"
            className={navClass("/billing")}
          >
            <CreditCard size={18} />

            Billing
          </Link>

          <Link
            to="/organization"
            className={navClass("/organization")}
          >
            <Building2 size={18} />

            Organization
          </Link>

          {/* <Link
            to="/settings"
            className={navClass("/settings")}
          >
            <Settings size={18} />

            Settings
          </Link> */}

        </div>

      </div>

      {/* Bottom Card */}
      <div className="mt-12 bg-slate-900 border border-slate-800 rounded-2xl p-4">

        <h3 className="text-white font-semibold">
          Current Plan
        </h3>

        <p className="text-indigo-400 text-2xl font-bold mt-2">
          Silver
        </p>

        <p className="text-slate-400 text-sm mt-1">
          1000 Credits Included
        </p>

        <Link
          to="/plans"
          className="mt-4 inline-block w-full text-center bg-indigo-600 hover:bg-indigo-500 transition text-white py-2 rounded-xl text-sm font-medium"
        >
          Upgrade Plan
        </Link>

      </div>

    </aside>
  );
}