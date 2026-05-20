import { useState, useEffect } from "react";
import API from "../api/axios";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

export default function Billing() {

  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchSubscription();
  }, []);

  const fetchSubscription = async () => {
    try {
      const res = await API.get("/billing/subscription");
      setSubscription(res.data);
    } catch (err) {
      console.error(err);
      setMessage("Failed to load subscription details");
    } finally {
      setLoading(false);
    }
  };

  const startCheckout = async () => {
    try {
      const res = await API.post("/billing/checkout");
      window.location.href = res.data.checkout_url;
    } catch (err) {
      console.error(err);
      setMessage(err.response?.data?.detail || "Failed to start checkout");
    }
  };

  if (loading) {
    return (
      <div className="flex">
        <Sidebar />
        <div className="flex-1 bg-gray-100 min-h-screen">
          <Navbar />
          <div className="p-10">
            <p>Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex">
      <Sidebar />

      <div className="flex-1 bg-gray-100 min-h-screen">
        <Navbar />

        <div className="p-10">

          {/* Header */}
          <div className="mb-10">
            <h1 className="text-4xl font-bold text-gray-800">Billing</h1>
            <p className="text-gray-600 mt-2">Manage your subscription and payments.</p>
          </div>

          {/* Message */}
          {message && (
            <div className="mb-6 p-4 bg-red-100 text-red-800 rounded-lg">
              {message}
            </div>
          )}

          {/* Current Subscription */}
          {subscription && (
            <div className="grid md:grid-cols-2 gap-8">

              {/* Subscription Details */}
              <div className="bg-white rounded-2xl shadow-lg p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">Current Plan</h2>

                <div className="space-y-4">
                  <div>
                    <p className="text-gray-600">Plan</p>
                    <p className="text-3xl font-bold text-indigo-600">{subscription.plan}</p>
                  </div>

                  <div>
                    <p className="text-gray-600">Available Credits</p>
                    <p className="text-3xl font-bold text-green-600">{subscription.credits}</p>
                  </div>

                  <div>
                    <p className="text-gray-600">Status</p>
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${subscription.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                      {subscription.is_active ? "Active" : "Inactive"}
                    </span>
                  </div>

                  <div>
                    <p className="text-gray-600">Billing Cycle Start</p>
                    <p className="text-sm text-gray-800">{new Date(subscription.billing_cycle_start).toLocaleDateString()}</p>
                  </div>
                </div>

                <button
                  onClick={startCheckout}
                  className="mt-8 w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg"
                >
                  Upgrade Subscription
                </button>
              </div>

              {/* Plan Features */}
              {subscription.plan_details && (
                <div className="bg-white rounded-2xl shadow-lg p-8">
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">Plan Features</h2>

                  <div className="mb-6">
                    <p className="text-gray-600">Description</p>
                    <p className="text-lg text-gray-800">{subscription.plan_details.description}</p>
                  </div>

                  <div>
                    <p className="text-gray-600 mb-4">Includes:</p>
                    <ul className="space-y-3">
                      {subscription.plan_details.features && subscription.plan_details.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center text-gray-800">
                          <span className="text-green-500 mr-3">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

            </div>
          )}

        </div>
      </div>
    </div>
  );
}