import { useEffect, useState } from "react";
import { TOAST_EVENT } from "../utils/toast";

const styles = {
  error: "border-red-200 bg-red-50 text-red-800",
  success: "border-emerald-200 bg-emerald-50 text-emerald-800",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
};

export default function ToastContainer() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    const handleToast = (event) => {
      const toast = event.detail;

      setItems((current) => [...current, toast]);
      window.setTimeout(() => {
        setItems((current) => current.filter((item) => item.id !== toast.id));
      }, 3000);
    };

    window.addEventListener(TOAST_EVENT, handleToast);

    return () => {
      window.removeEventListener(TOAST_EVENT, handleToast);
    };
  }, []);

  return (
    <div className="fixed right-4 top-4 z-[100] w-80 space-y-3">
      {items.map((item) => (
        <div
          key={item.id}
          className={`rounded-lg border px-4 py-3 text-sm shadow-md ${
            styles[item.type] || styles.success
          }`}
        >
          {item.message}
        </div>
      ))}
    </div>
  );
}
