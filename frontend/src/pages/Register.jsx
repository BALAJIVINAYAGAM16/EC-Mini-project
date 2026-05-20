import { useState } from "react";
import API from "../api/axios";
import { Link, useNavigate } from "react-router-dom";

const PASSWORD_MAX_BYTES = 72;

const getByteLength = (value) =>
  new TextEncoder().encode(value).length;

export default function Register() {

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "employee",
    organization_name: "",
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

      await API.post(
        "/auth/register",
        form
      );

      navigate("/login");

    } catch (err) {

      setError(
        err.response?.data?.detail ||
        "Unable to create your account."
      );

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

        {/* Header */}
        <div className="space-y-1 text-center">

          <h1 className="text-2xl font-bold text-slate-900">
            Create Account
          </h1>

          <p className="text-sm text-slate-500">
            Register with your organization and role.
          </p>

        </div>

        {/* Error */}
        {error && (

          <p className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600">
            {error}
          </p>
        )}

        {/* Name */}
        <div>

          <label className="block text-sm font-medium text-slate-700 mb-1">
            Full Name
          </label>

          <input
            type="text"
            placeholder="Enter your name"
            value={form.name}
            onChange={(e) =>
              setForm({
                ...form,
                name: e.target.value,
              })
            }
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
            required
          />

        </div>

        {/* Organization */}
        <div>

          <label className="block text-sm font-medium text-slate-700 mb-1">
            Organization Name
          </label>

          <input
            type="text"
            placeholder="Enter organization name"
            value={form.organization_name}
            onChange={(e) =>
              setForm({
                ...form,
                organization_name: e.target.value,
              })
            }
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
            required
          />

        </div>

        {/* Email */}
        <div>

          <label className="block text-sm font-medium text-slate-700 mb-1">
            Email Address
          </label>

          <input
            type="email"
            placeholder="Enter your email"
            value={form.email}
            onChange={(e) =>
              setForm({
                ...form,
                email: e.target.value,
              })
            }
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
            required
          />

        </div>

        {/* Password */}
        <div>

          <label className="block text-sm font-medium text-slate-700 mb-1">
            Password
          </label>

          <input
            type="password"
            placeholder="Enter password"
            value={form.password}
            maxLength={PASSWORD_MAX_BYTES}
            onChange={(e) =>
              setForm({
                ...form,
                password: e.target.value,
              })
            }
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
            required
          />

          <p className="mt-1 text-xs text-slate-400">
            Maximum 72 bytes allowed.
          </p>

        </div>

        {/* Role */}
        <div>

          <label className="block text-sm font-medium text-slate-700 mb-1">
            Role
          </label>

          <select
            value={form.role}
            onChange={(e) =>
              setForm({
                ...form,
                role: e.target.value,
              })
            }
            className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-blue-500"
          >
            <option value="employee">
              Employee
            </option>

            <option value="manager">
              Manager
            </option>

            <option value="admin">
              Admin
            </option>

          </select>

        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-lg bg-blue-600 py-3 text-white font-medium transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
        >
          {isSubmitting
            ? "Creating account..."
            : "Register"}
        </button>

        {/* Footer */}
        <p className="text-center text-sm text-slate-500">

          Already have an account?{" "}

          <Link
            to="/login"
            className="font-medium text-blue-600 hover:text-blue-700"
          >
            Login
          </Link>

        </p>

      </form>

    </div>
  );
}