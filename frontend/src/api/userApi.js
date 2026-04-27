import API from "./axios";

export const fetchUsers = async () => {
  const res = await API.get("/auth/users");
  return res.data;
};
