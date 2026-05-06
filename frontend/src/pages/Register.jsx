import { useState } from "react";
import API from "../api/axios";
import { Link, useNavigate } from "react-router-dom";

const PASSWORD_MAX_BYTES = 72;

const getByteLength = (value) => new TextEncoder().encode(value).length;

export default function Register() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "employee",
  });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (getByteLength(form.password) > PASSWORD_MAX_BYTES) {
      setError("Password cannot be longer than 72 bytes.");
      return;
    }

    setIsSubmitting(true);

    try {
      await API.post("/auth/register", form);
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to create your account.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg space-y-5"
      >
        <div className="space-y-1 text-center">
          <h1 className="text-2xl font-bold text-slate-900">Create account</h1>
          <p className="text-sm text-slate-500">Register with your project role.</p>
        </div>

        {error && (
          <p className="rounded-lg border border-red-200 bg-red-50 p-2 text-sm text-red-600">
            {error}
          </p>
        )}

        <input
          placeholder="Name"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <input
          type="email"
          placeholder="Email"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <input
          type="password"
          placeholder="Password"
          maxLength={PASSWORD_MAX_BYTES}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <select
          className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
          onChange={(e) => setForm({ ...form, role: e.target.value })}
          value={form.role}
        >
          <option value="employee">Employee</option>
          <option value="manager">Manager</option>
          <option value="admin">Admin</option>
        </select>

        <button
          disabled={isSubmitting}
          className="w-full rounded-lg bg-blue-600 py-2 text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
        >
          {isSubmitting ? "Creating account..." : "Register"}
        </button>

        <p className="text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-blue-600 hover:text-blue-700">
            Login
          </Link>
        </p>
      </form>
    </div>
  );
}
