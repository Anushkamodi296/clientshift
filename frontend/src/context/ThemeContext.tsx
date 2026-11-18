import React, { createContext, useContext, useEffect, useState } from 'react';

export type ThemeMode = 'dark' | 'light' | 'system_auto';

interface ThemeContextType {
  theme: ThemeMode;
  resolvedTheme: 'dark' | 'light';
  setTheme: (mode: ThemeMode) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<ThemeMode>(() => {
    const saved = localStorage.getItem('clientshift_theme') as ThemeMode;
    return saved || 'dark';
  });

  const getSystemAutoTheme = (): 'dark' | 'light' => {
    const hour = new Date().getHours();
    // 06:00 to 18:59 -> Light Mode, 19:00 to 05:59 -> Dark Mode
    return (hour >= 6 && hour < 19) ? 'light' : 'dark';
  };

  const [resolvedTheme, setResolvedTheme] = useState<'dark' | 'light'>(() => {
    if (theme === 'system_auto') {
      return getSystemAutoTheme();
    }
    return theme;
  });

  useEffect(() => {
    const updateResolved = () => {
      let current: 'dark' | 'light';
      if (theme === 'system_auto') {
        current = getSystemAutoTheme();
      } else {
        current = theme;
      }
      setResolvedTheme(current);

      const root = document.documentElement;
      if (current === 'dark') {
        root.classList.add('dark');
        root.classList.remove('light');
      } else {
        root.classList.add('light');
        root.classList.remove('dark');
      }
    };

    updateResolved();
    localStorage.setItem('clientshift_theme', theme);

    // If in system_auto, poll every minute to automatically switch at 06:00 or 19:00
    if (theme === 'system_auto') {
      const interval = setInterval(updateResolved, 60000);
      return () => clearInterval(interval);
    }
  }, [theme]);

  const setTheme = (mode: ThemeMode) => {
    setThemeState(mode);
  };

  const toggleTheme = () => {
    if (theme === 'dark') setTheme('light');
    else if (theme === 'light') setTheme('system_auto');
    else setTheme('dark');
  };

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
};
