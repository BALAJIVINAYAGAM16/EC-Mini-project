const TOAST_EVENT = "app-toast";

function notify(type, message) {
  window.dispatchEvent(
    new CustomEvent(TOAST_EVENT, {
      detail: {
        id: Date.now(),
        message,
        type,
      },
    })
  );
}

export const toast = {
  error: (message) => notify("error", message),
  success: (message) => notify("success", message),
  warning: (message) => notify("warning", message),
};

export { TOAST_EVENT };
