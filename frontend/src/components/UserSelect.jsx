import { useEffect, useState } from "react";
import { fetchAssignableUsers } from "../api/userApi";

export default function UserSelect({ value, onChange }) {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetchAssignableUsers()
      .then((data) => {
        setUsers(Array.isArray(data) ? data : data.users || []);
      })
      .catch((err) => console.error("Error fetching users:", err));
  }, []);

  return (
    <select
      value={value || ""}
      onChange={(e) => onChange(e.target.value)}
      className="border p-2 rounded w-full"
    >
      <option value="">Select User</option>

      {users.map((user) => (
        <option key={user.id} value={user.id}>
          {user.email} ({user.role})
        </option>
      ))}
    </select>
  );
}
