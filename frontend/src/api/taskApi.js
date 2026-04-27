import API from "./axios";

export const assignTask = async (taskId, userId) => {
  const res = await API.patch(`/tasks/${taskId}/assign`, {
    assigned_to_id: userId,
  });
  return res.data;
};
export const createTask = (data) => API.post("/tasks", data);

export const updateTask = (id, data) => API.put(`/tasks/${id}`, data);

export const deleteTask = (id) => API.delete(`/tasks/${id}`);
