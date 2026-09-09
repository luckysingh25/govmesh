import React, { createContext, useContext, useEffect, useState } from 'react';
import { clearStoredToken, fetchCurrentUser, getStoredToken, login as loginRequest } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getStoredToken()));

  useEffect(() => {
    if (!getStoredToken()) return;
    fetchCurrentUser().then(setUser).catch(clearStoredToken).finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    await loginRequest(email, password);
    const current = await fetchCurrentUser();
    setUser(current);
    return current;
  };
  const logout = () => { clearStoredToken(); setUser(null); };
  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>;
};

export const useAuth = () => useContext(AuthContext);
