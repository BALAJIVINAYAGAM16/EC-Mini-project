import { useContext, useEffect, useState } from "react";
import { AuthContext } from "../context/auth-context";
import API from "../api/axios";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const { logout } = useContext(AuthContext);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    API.get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => setUser(null)); // ❗ don't auto logout here
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex justify-between items-center p-4 bg-gray-800 text-white">
      <h2 className="text-xl font-bold">Task Manager</h2>

      <div className="flex gap-4 items-center">

        {/* Always visible */}
        <Link to="/">Dashboard</Link>

        {/* 🔐 If user logged in */}
        {user ? (
          <>
            {(user.role === "admin" || user.role === "manager") && (
              <>
                <Link to="/create">Create Task</Link>
                <Link to="/users">Users</Link>
              </>
            )}

            <span className="text-sm">
              {user.email} ({user.role})
            </span>

            <button
              onClick={handleLogout}
              className="bg-red-500 px-3 py-1 rounded hover:bg-red-600"
            >
              Logout
            </button>
          </>
        ) : (
          /* 🚀 If NOT logged in */
          <>
            <Link
              to="/login"
              className="bg-blue-500 px-3 py-1 rounded hover:bg-blue-600"
            >
              Login
            </Link>

            <Link
              to="/register"
              className="bg-green-500 px-3 py-1 rounded hover:bg-green-600"
            >
              Register
            </Link>
          </>
        )}

      </div>
    </div>
  );
}