import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

import { clearStoredAuth, getStoredAuth, setStoredAuth } from '@/lib/authStorage';

interface AuthContextValue {
  isLoading: boolean;
  isLoggedIn: boolean;
  login: (accessToken?: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    getStoredAuth()
      .then(({ isLoggedIn: stored }) => setIsLoggedIn(stored))
      .finally(() => setIsLoading(false));
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      isLoading,
      isLoggedIn,
      login: async (accessToken?: string) => {
        await setStoredAuth(accessToken);
        setIsLoggedIn(true);
      },
      logout: async () => {
        await clearStoredAuth();
        setIsLoggedIn(false);
      },
    }),
    [isLoading, isLoggedIn],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
