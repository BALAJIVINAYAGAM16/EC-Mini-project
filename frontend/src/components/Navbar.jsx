import { useContext, useEffect, useState } from "react";
import { AuthContext } from "../context/auth-context";
import API from "../api/axios";
import { Link, useNavigate, useLocation } from "react-router-dom";

export default function Navbar() {
  const { logout } = useContext(AuthContext);
  const [user, setUser] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    API.get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => setUser(null));
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const linkClass = (path) =>
    `px-3 py-1 rounded-full text-sm transition ${
      location.pathname === path
        ? "bg-slate-800 text-white"
        : "text-slate-600 hover:bg-slate-200"
    }`;

  return (
    <nav className="sticky top-0 z-50 backdrop-blur-md bg-white/70 border-b border-slate-200">
      <div className="flex justify-between items-center px-6 py-3">

        {/* 🔷 Logo */}
        <h2 className="text-lg font-bold text-slate-700 tracking-wide">
          TaskFlow
        </h2>

        {/* 💻 Menu */}
        <div className="flex items-center gap-4">

          <Link to="/" className={linkClass("/")}>
            Dashboard
          </Link>

          {user && (
            <>
              <Link to="/kanban" className={linkClass("/kanban")}>
                Kanban
              </Link>

              <Link to="/approvals" className={linkClass("/approvals")}>
                Approvals
              </Link>
            </>
          )}

          {(user?.role === "admin" || user?.role === "manager") && (
            <>
              <Link to="/create" className={linkClass("/create")}>
                Create
              </Link>

              <Link to="/users" className={linkClass("/users")}>
                Users
              </Link>
            </>
          )}

          {/* 🔔 Notification */}
          {user && (
            <button className="relative text-slate-600 hover:text-slate-800">
              🔔
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] px-1 rounded-full">
                2
              </span>
            </button>
          )}

          {/* 👤 User */}
          {user ? (
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 hover:bg-slate-200"
              >
                <div className="w-8 h-8 rounded-full bg-slate-800 text-white flex items-center justify-center text-sm">
                  {user.email[0].toUpperCase()}
                </div>
                <span className="text-xs text-slate-600">
                  {user.role}
                </span>
              </button>

              {/* Dropdown */}
              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-40 bg-white border border-slate-200 rounded-xl shadow-lg overflow-hidden">
                  <button
                    onClick={() => navigate("/profile")}
                    className="w-full text-left px-4 py-2 text-sm hover:bg-slate-100"
                  >
                    Profile
                  </button>

                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-slate-100"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <>
              <Link
                to="/login"
                className="px-3 py-1 rounded-full bg-slate-800 text-white text-sm"
              >
                Login
              </Link>

              <Link
                to="/register"
                className="px-3 py-1 rounded-full border border-slate-300 text-sm"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}