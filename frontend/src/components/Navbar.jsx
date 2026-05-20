import { useContext, useEffect, useState } from "react";
import {
  Link,
  useNavigate,
  useLocation,
} from "react-router-dom";

import { CreditCard } from "lucide-react";

import { AuthContext } from "../context/auth-context";
import API from "../api/axios";

import NotificationBell from "./NotificationBell";

export default function Navbar() {

  const { logout } = useContext(AuthContext);

  const [user, setUser] = useState(null);

  const [dropdownOpen, setDropdownOpen] =
    useState(false);

  const [credits, setCredits] =
    useState(0);

  const navigate = useNavigate();

  const location = useLocation();

  useEffect(() => {

    API.get("/auth/me")
      .then((res) => {

        setUser(res.data);

        /*
          Example backend response:
          {
            email,
            role,
            credits
          }
        */

        setCredits(res.data.credits || 0);

      })
      .catch(() => setUser(null));

  }, []);

  const handleLogout = () => {

    logout();

    navigate("/login");

  };

  const linkClass = (path) =>
    `px-3 py-2 rounded-xl text-sm font-medium transition ${
      location.pathname === path
        ? "bg-slate-900 text-white shadow"
        : "text-slate-600 hover:bg-slate-100"
    }`;

  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm">

      <div className="flex justify-between items-center px-6 py-4">

        {/* LEFT */}
        <div className="flex items-center gap-8">

          {/* Logo */}
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">
            TaskFlow SaaS
          </h1>

          {/* Menu */}
          <div className="hidden md:flex items-center gap-2">

            <Link
              to="/"
              className={linkClass("/")}
            >
              Dashboard
            </Link>

            {user && (
              <>
                <Link
                  to="/kanban"
                  className={linkClass("/kanban")}
                >
                  Kanban
                </Link>

                <Link
                  to="/approvals"
                  className={linkClass("/approvals")}
                >
                  Approvals
                </Link>

                <Link
                  to="/plans"
                  className={linkClass("/plans")}
                >
                  Plans
                </Link>

                <Link
                  to="/billing"
                  className={linkClass("/billing")}
                >
                  Billing
                </Link>
              </>
            )}

            {(user?.role === "admin" ||
              user?.role === "manager") && (
              <>
                <Link
                  to="/create"
                  className={linkClass("/create")}
                >
                  Create
                </Link>

                <Link
                  to="/users"
                  className={linkClass("/users")}
                >
                  Users
                </Link>
              </>
            )}
          </div>

        </div>

        {/* RIGHT */}
        <div className="flex items-center gap-4">

          {/* Credits */}
          {user && (
            <div className="flex items-center gap-2 bg-indigo-50 text-indigo-700 px-4 py-2 rounded-xl border border-indigo-100">

              <CreditCard size={18} />

              <span className="text-sm font-semibold">
                {credits} Credits
              </span>

            </div>
          )}

          {/* Notifications */}
          {user && <NotificationBell />}

          {/* User Dropdown */}
          {user ? (

            <div className="relative">

              <button
                onClick={() =>
                  setDropdownOpen(!dropdownOpen)
                }
                className="flex items-center gap-3 bg-slate-100 hover:bg-slate-200 px-3 py-2 rounded-xl transition"
              >

                <div className="w-9 h-9 rounded-full bg-slate-900 text-white flex items-center justify-center font-semibold">
                  {user.email?.[0]?.toUpperCase()}
                </div>

                <div className="hidden sm:block text-left">
                  <p className="text-sm font-semibold text-slate-700">
                    {user.email}
                  </p>

                  <p className="text-xs text-slate-500 capitalize">
                    {user.role}
                  </p>
                </div>

              </button>

              {/* Dropdown */}
              {dropdownOpen && (

                <div className="absolute right-0 mt-3 w-52 bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden">

                  <button
                    onClick={() =>
                      navigate("/profile")
                    }
                    className="w-full text-left px-5 py-3 text-sm hover:bg-slate-50 transition"
                  >
                    Profile
                  </button>

                  <button
                    onClick={() =>
                      navigate("/organization")
                    }
                    className="w-full text-left px-5 py-3 text-sm hover:bg-slate-50 transition"
                  >
                    Organization
                  </button>

                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-5 py-3 text-sm text-red-500 hover:bg-red-50 transition"
                  >
                    Logout
                  </button>

                </div>

              )}

            </div>

          ) : (

            <div className="flex items-center gap-3">

              <Link
                to="/login"
                className="px-4 py-2 rounded-xl bg-slate-900 text-white text-sm font-medium hover:bg-slate-800 transition"
              >
                Login
              </Link>

              <Link
                to="/register"
                className="px-4 py-2 rounded-xl border border-slate-300 text-sm font-medium hover:bg-slate-100 transition"
              >
                Register
              </Link>

            </div>

          )}

        </div>

      </div>

    </nav>
  );
}