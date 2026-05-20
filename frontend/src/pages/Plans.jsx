import { useState, useEffect } from "react";
import API from "../api/axios";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import PlanCard from "../components/PlanCard";

export default function Plans() {

  const [plans, setPlans] = useState([]);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchPlans();
    fetchSubscription();
  }, []);

  const fetchPlans = async () => {
    try {
      const res = await API.get("/billing/plans");
      setPlans(res.data);
    } catch (err) {
      console.error(err);
      setMessage("Failed to load plans");
    }
  };

  const fetchSubscription = async () => {
    try {
      const res = await API.get("/billing/subscription");
      setCurrentPlan(res.data.plan);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const upgradePlan = async (planName) => {
    try {
      const res = await API.post(`/billing/upgrade/${planName}`);
      setMessage(res.data.message);
      setCurrentPlan(planName);
      setTimeout(() => setMessage(""), 3000);
    } catch (err) {
      console.error(err);
      setMessage(err.response?.data?.detail || `Failed to upgrade to ${planName}`);
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
            <h1 className="text-4xl font-bold text-gray-800">Subscription Plans</h1>
            <p className="text-gray-600 mt-2">Choose the perfect plan for your organization</p>
          </div>

          {/* Message */}
          {message && (
            <div className={`mb-6 p-4 rounded-lg ${message.includes("successfully") || message.includes("Successfully") ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
              {message}
            </div>
          )}

          {/* Plans Grid */}
          <div className="grid md:grid-cols-3 gap-8">
            {plans.map((plan) => (
              <div key={plan.name} className={`bg-white rounded-2xl shadow-lg overflow-hidden transform transition hover:scale-105 ${currentPlan === plan.name ? "ring-2 ring-indigo-600" : ""}`}>
                
                {currentPlan === plan.name && (
                  <div className="bg-indigo-600 text-white py-2 px-4 text-center font-semibold">
                    Current Plan
                  </div>
                )}

                <div className="p-8">
                  {/* Plan Name */}
                  <h3 className="text-2xl font-bold text-gray-800 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 text-sm mb-6">{plan.description}</p>

                  {/* Price */}
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-indigo-600">${(plan.price / 100).toFixed(2)}</span>
                    <span className="text-gray-600">/month</span>
                  </div>

                  {/* Credits */}
                  <div className="bg-indigo-50 rounded-lg p-4 mb-6">
                    <p className="text-sm text-gray-600">Monthly Credits</p>
                    <p className="text-2xl font-bold text-indigo-600">{plan.credits}</p>
                  </div>

                  {/* Features */}
                  <div className="mb-8">
                    <p className="text-sm font-semibold text-gray-700 mb-4">Includes:</p>
                    <ul className="space-y-3">
                      {plan.features && plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center text-gray-800 text-sm">
                          <span className="text-green-500 mr-2">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Button */}
                  <button
                    onClick={() => upgradePlan(plan.name)}
                    disabled={currentPlan === plan.name}
                    className={`w-full py-3 px-6 rounded-lg font-semibold transition ${currentPlan === plan.name ? "bg-gray-100 text-gray-500 cursor-not-allowed" : "bg-indigo-600 hover:bg-indigo-700 text-white"}`}
                  >
                    {currentPlan === plan.name ? "Current Plan" : `Upgrade to ${plan.name}`}
                  </button>
                </div>

              </div>
            ))}
          </div>

        </div>
      </div>
    </div>
  );
}