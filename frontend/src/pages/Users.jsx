import { useEffect, useState } from "react";
import { fetchUsers } from "../api/userApi";
import Navbar from "../components/Navbar";

export default function Users() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetchUsers()
      .then((data) => {
        setUsers(Array.isArray(data) ? data : data.users || []);
      })
      .catch(() => alert("Failed to load users"));
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />

      <div className="p-6">
        <h2 className="text-xl font-bold mb-4">Users</h2>

        {users.length === 0 ? (
          <p>No users found</p>
        ) : (
          users.map((user) => (
            <div
              key={user.id}
              className="bg-white p-4 mb-3 rounded shadow"
            >
              <p><b>Email:</b> {user.email}</p>
              <p><b>Role:</b> {user.role}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
