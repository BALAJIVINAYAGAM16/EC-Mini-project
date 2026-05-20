import { useState, useContext } from "react";
import API from "../api/axios";
import { AuthContext } from "../context/auth-context";
import { useNavigate } from "react-router-dom";

const PASSWORD_MAX_BYTES = 72;

const getByteLength = (value) => new TextEncoder().encode(value).length;

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (getByteLength(form.password) > PASSWORD_MAX_BYTES) {
      setError("Password cannot be longer than 72 bytes.");
      return;
    }

    setIsSubmitting(true);

    const formData = new URLSearchParams();
    formData.append("username", form.email);
    formData.append("password", form.password);

    try {
      const res = await API.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      login(res.data.access_token, res.data.refresh_token);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to connect to the login server.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">

      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-xl shadow-md w-full max-w-sm space-y-5"
      >

        {/* Title */}
        <h2 className="text-2xl font-bold text-center text-gray-800">
          Login
        </h2>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">
            {error}
          </p>
        )}

        {/* Email */}
        <div>
          <label className="block text-sm text-gray-600 mb-1">
            Email
          </label>
          <input
            type="email"
            placeholder="Enter your email"
            className="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            onChange={(e) =>
              setForm({ ...form, email: e.target.value })
            }
          />
        </div>

        {/* Password */}
        <div>
          <label className="block text-sm text-gray-600 mb-1">
            Password
          </label>
          <input
            type="password"
            placeholder="Enter your password"
            maxLength={PASSWORD_MAX_BYTES}
            className="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            onChange={(e) =>
              setForm({ ...form, password: e.target.value })
            }
          />
        </div>

        {/* Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition"
        >
          {isSubmitting ? "Logging in..." : "Login"}
        </button>

      </form>
    </div>
  );
}
