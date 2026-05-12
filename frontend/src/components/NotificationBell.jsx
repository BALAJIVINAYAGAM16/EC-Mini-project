import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bell } from "lucide-react";
import API from "../api/axios";

export default function NotificationBell() {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    let isMounted = true;

    API.get("/notifications/")
      .then((res) => {
        if (isMounted) {
          const notifications = Array.isArray(res.data) ? res.data : [];
          setUnreadCount(
            notifications.filter((notification) => !notification.is_read)
              .length
          );
        }
      })
      .catch(() => {
        if (isMounted) {
          setUnreadCount(0);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <Link
      to="/notifications"
      aria-label="Notifications"
      className="relative inline-flex h-10 w-10 items-center justify-center rounded-full text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
    >
      <Bell size={22} />

      {unreadCount > 0 && (
        <span className="absolute right-1 top-1 min-w-5 rounded-full bg-red-500 px-1.5 text-center text-[10px] font-semibold leading-5 text-white">
          {unreadCount > 99 ? "99+" : unreadCount}
        </span>
      )}
    </Link>
  );
}
