/**
 * AuthContext
 * React Context for managing global authentication state
 *
 * Features:
 * - Global auth state management (user, token, isAuthenticated)
 * - Secure localStorage token storage
 * - Login/Logout functions
 * - Automatic token recovery on app load
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

/**
 * User object structure
 */
export interface User {
  id: string;
  name: string;
  email: string;
  created_at: string;
}

/**
 * AuthContext shape
 */
interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: User, token: string, refreshToken?: string) => void;
  logout: () => void;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
}

/**
 * Create Auth Context with default values
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider Component
 * Wraps the app and provides auth state to all children
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // ===== STATE MANAGEMENT =====
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // ===== LOGOUT HANDLER =====
  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setToken(null);
    console.log('User logged out');
  };

  // ===== INITIALIZE AUTH STATE ON APP LOAD =====
  // Recover token from localStorage if it exists
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = localStorage.getItem('auth_token');

        if (storedToken) {
          setToken(storedToken);

          const apiBase = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');
          const response = await fetch(`${apiBase}/auth/me`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${storedToken}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const data = await response.json();
            setUser(data.user);
          } else {
            // Attempt auto-refresh if access token failed
            const storedRefreshToken = localStorage.getItem('refresh_token');
            if (storedRefreshToken) {
              const refreshRes = await fetch(`${apiBase}/auth/refresh`, {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${storedRefreshToken}`,
                  'Content-Type': 'application/json'
                }
              });
              if (refreshRes.ok) {
                const refreshData = await refreshRes.json();
                if (refreshData.access_token) {
                  localStorage.setItem('auth_token', refreshData.access_token);
                  setToken(refreshData.access_token);
                  const meRes = await fetch(`${apiBase}/auth/me`, {
                    headers: { 'Authorization': `Bearer ${refreshData.access_token}` }
                  });
                  if (meRes.ok) {
                    const meData = await meRes.json();
                    setUser(meData.user);
                    return;
                  }
                }
              }
            }
            logout();
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        logout();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // ===== AUTO-REFRESH ON TOKEN EXPIRY EVENT =====
  useEffect(() => {
    const handleExpiry = async () => {
      const storedRefreshToken = localStorage.getItem('refresh_token');
      if (!storedRefreshToken) {
        logout();
        return;
      }
      try {
        const apiBase = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');
        const res = await fetch(`${apiBase}/auth/refresh`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${storedRefreshToken}`,
            'Content-Type': 'application/json',
          },
        });
        if (res.ok) {
          const data = await res.json();
          if (data.access_token) {
            localStorage.setItem('auth_token', data.access_token);
            setToken(data.access_token);
            return;
          }
        }
        logout();
      } catch (err) {
        console.error('Failed to refresh auth token:', err);
        logout();
      }
    };

    window.addEventListener('auth-token-expired', handleExpiry);
    return () => window.removeEventListener('auth-token-expired', handleExpiry);
  }, []);

  // ===== LOGIN HANDLER =====
  const login = (user: User, newToken: string, refreshToken?: string) => {
    localStorage.setItem('auth_token', newToken);
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }
    setUser(user);
    setToken(newToken);
    console.log('User logged in:', user.email);
  };

  // ===== CONTEXT VALUE =====
  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    logout,
    setUser,
    setToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * useAuth Hook
 * Access auth context from any component
 *
 * @returns AuthContextType with user, token, login, logout, etc.
 *
 * Usage:
 * const { user, isAuthenticated, login, logout } = useAuth();
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};
