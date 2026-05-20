import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import API from "../api/axios";

export default function Organization() {

  const [organization, setOrganization] = useState({
    organization_name: "",
    active_plan: "",
  });

  const [loading, setLoading] = useState(true);

  const [saving, setSaving] = useState(false);

  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchOrganization();
  }, []);

  const fetchOrganization = async () => {

    try {

      const res = await API.get("/organization");

      setOrganization({
        organization_name: res.data.organization_name || "",
        active_plan: res.data.active_plan || "Basic",
      });

    } catch (error) {

      console.error(error);

      setMessage("Failed to load organization details.");

    } finally {

      setLoading(false);
    }
  };

  const handleChange = (e) => {

    setOrganization({
      ...organization,
      [e.target.name]: e.target.value,
    });
  };

  const handleSave = async () => {

    try {

      setSaving(true);

      setMessage("");

      await API.put(
        "/organization/update",
        {
          organization_name: organization.organization_name,
        }
      );

      setMessage("Organization updated successfully.");

      setTimeout(() => {
        setMessage("");
      }, 3000);

    } catch (error) {

      console.error(error);

      setMessage(
        error.response?.data?.detail ||
        "Failed to update organization."
      );

    } finally {

      setSaving(false);
    }
  };

  if (loading) {

    return (
      <div className="flex bg-gray-100 min-h-screen">

        <Sidebar />

        <div className="flex-1">

          <Navbar />

          <div className="p-8">
            <p className="text-lg font-medium">
              Loading...
            </p>
          </div>

        </div>

      </div>
    );
  }

  return (
    <div className="flex bg-gray-100 min-h-screen">

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1">

        {/* Navbar */}
        <Navbar />

        {/* Content */}
        <div className="p-8">

          {/* Header */}
          <div className="mb-8">

            <h1 className="text-4xl font-bold text-gray-800">
              Organization Settings
            </h1>

            <p className="text-gray-500 mt-2">
              Manage your organization information.
            </p>

          </div>

          {/* Message */}
          {message && (

            <div
              className={`mb-6 p-4 rounded-lg ${
                message.includes("successfully")
                  ? "bg-green-100 text-green-700"
                  : "bg-red-100 text-red-700"
              }`}
            >
              {message}
            </div>
          )}

          {/* Card */}
          <div className="bg-white rounded-2xl shadow-lg p-8 max-w-2xl">

            <div className="space-y-6">

              {/* Organization Name */}
              <div>

                <label className="block font-semibold text-gray-700">
                  Organization Name
                </label>

                <input
                  type="text"
                  name="organization_name"
                  value={organization.organization_name}
                  onChange={handleChange}
                  placeholder="Enter organization name"
                  className="w-full border border-gray-300 rounded-xl p-3 mt-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />

              </div>

              {/* Active Plan */}
              <div>

                <label className="block font-semibold text-gray-700">
                  Active Plan
                </label>

                <div className="mt-2 flex items-center justify-between border border-gray-300 rounded-xl p-4 bg-gray-50">

                  <span className="text-lg font-semibold text-indigo-600">
                    {organization.active_plan}
                  </span>

                  <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
                    Active
                  </span>

                </div>

              </div>

            </div>

            {/* Buttons */}
            <div className="flex gap-4 mt-8">

              <button
                onClick={handleSave}
                disabled={saving}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-xl font-semibold transition disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save Changes"}
              </button>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}