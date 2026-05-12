import { useEffect, useState } from "react";
import API from "../api/axios";
import Sidebar from "../components/Sidebar";
import { toast } from "../utils/toast";

export default function Notifications() {
  const [notifications, setNotifications] =
    useState([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    try {
      const res = await API.get("/notifications/");
      setNotifications(Array.isArray(res.data) ? res.data : []);
    } catch {
      toast.error("Failed to fetch notifications");
    }
  };

  useEffect(() => {
    let isMounted = true;

    API.get("/notifications/")
      .then((res) => {
        if (isMounted) {
          setNotifications(Array.isArray(res.data) ? res.data : []);
        }
      })
      .catch(() => {
        toast.error("Failed to fetch notifications");
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const markAsRead = async (id) => {
    try {
      await API.patch(
        `/notifications/${id}/read`
      );

      fetchNotifications();
    } catch {
      toast.error("Failed to update notification");
    }
  };

  return (
    <div className="flex">
      <Sidebar />

      <div className="flex-1 p-6">
        <h1 className="text-3xl font-bold mb-6">
          Notifications
        </h1>

        <div className="space-y-4">
          {loading ? (
            <div className="rounded-xl bg-white p-4 shadow text-slate-500">
              Loading notifications...
            </div>
          ) : notifications.length === 0 ? (
            <div className="rounded-xl bg-white p-4 shadow text-slate-500">
              No notifications found
            </div>
          ) : notifications.map((notification) => (
            <div
              key={notification.id}
              className={`p-4 rounded-xl shadow bg-white ${
                notification.is_read
                  ? ""
                  : "border-l-4 border-blue-500"
              }`}
            >
              <p>{notification.message}</p>

              {!notification.is_read && (
                <button
                  onClick={() =>
                    markAsRead(notification.id)
                  }
                  className="mt-2 text-blue-600"
                >
                  Mark as Read
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
