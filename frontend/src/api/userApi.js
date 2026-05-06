import API from "./axios";

export const fetchUsers = async () => {
  const res = await API.get("/users/");
  return res.data;
};

export const fetchAssignableUsers = async () => {
  const res = await API.get("/users/assignable");
  return res.data;
};
