import { useCallback, useMemo, useState } from "react";
import { AuthContext } from "./auth-context";
import API from "../api/axios";

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(null);

  const login = useCallback((nextToken, nextRefreshToken) => {
    localStorage.setItem("token", nextToken);
    if (nextRefreshToken) {
      localStorage.setItem("refreshToken", nextRefreshToken);
    }
    setToken(nextToken);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    setToken(null);
    setUser(null);
  }, []);

  const fetchUser = useCallback(async () => {
    if (token) {
      try {
        const res = await API.get("/auth/me");
        setUser(res.data);
      } catch (err) {
        console.error("Failed to fetch user:", err);
      }
    }
  }, [token]);

  const value = useMemo(() => ({ 
    token, 
    login, 
    logout, 
    user,
    fetchUser,
    setUser 
  }), [token, login, logout, user, fetchUser]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
