import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  api,
  UserProfile,
  UserStats,
  AuthTokenResponse,
  getAuthToken,
  setAuthToken
} from '../services/api';

interface AuthContextType {
  user: UserProfile | null;
  stats: UserStats | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isAuthModalOpen: boolean;
  openAuthModal: () => void;
  closeAuthModal: () => void;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<void>;
  googleLogin: (payload: { credential?: string; email?: string; full_name?: string; avatar_url?: string }) => Promise<void>;
  guestLogin: () => Promise<void>;
  logout: () => void;
  refreshUserStats: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [token, setTokenState] = useState<string | null>(getAuthToken());
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const initAuth = async () => {
    const existingToken = getAuthToken();
    if (existingToken) {
      try {
        const data = await api.getMe();
        setUser(data.user);
        setStats(data.stats);
        setTokenState(existingToken);
      } catch (err) {
        console.warn('Session expired, initializing default guest session...');
        // Auto-initialize demo guest session
        await handleGuestLogin();
      }
    } else {
      // Default to guest session for immediate interactive use
      await handleGuestLogin();
    }
    setIsLoading(false);
  };

  useEffect(() => {
    initAuth();
  }, []);

  const handleGuestLogin = async () => {
    try {
      const res: AuthTokenResponse = await api.guestLogin();
      setUser(res.user);
      setStats(res.stats);
      setTokenState(res.access_token);
    } catch (e) {
      console.error('Failed to initialize guest session', e);
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await api.login({ email, password });
      setUser(res.user);
      setStats(res.stats);
      setTokenState(res.access_token);
      setIsAuthModalOpen(false);
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email: string, password: string, fullName: string) => {
    setIsLoading(true);
    try {
      const res = await api.signup({ email, password, full_name: fullName });
      setUser(res.user);
      setStats(res.stats);
      setTokenState(res.access_token);
      setIsAuthModalOpen(false);
    } finally {
      setIsLoading(false);
    }
  };

  const googleLogin = async (payload: { credential?: string; email?: string; full_name?: string; avatar_url?: string }) => {
    setIsLoading(true);
    try {
      const res = await api.googleAuth(payload);
      setUser(res.user);
      setStats(res.stats);
      setTokenState(res.access_token);
      setIsAuthModalOpen(false);
    } finally {
      setIsLoading(false);
    }
  };

  const guestLogin = async () => {
    setIsLoading(true);
    try {
      await handleGuestLogin();
      setIsAuthModalOpen(false);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setAuthToken(null);
    setTokenState(null);
    setUser(null);
    setStats(null);
    // Switch to clean guest session
    handleGuestLogin();
  };

  const refreshUserStats = async () => {
    if (token) {
      try {
        const data = await api.getMe();
        setStats(data.stats);
      } catch (e) {
        // ignore
      }
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        stats,
        token,
        isAuthenticated: !!user && user.provider !== 'guest',
        isLoading,
        isAuthModalOpen,
        openAuthModal: () => setIsAuthModalOpen(true),
        closeAuthModal: () => setIsAuthModalOpen(false),
        login,
        signup,
        googleLogin,
        guestLogin,
        logout,
        refreshUserStats
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
