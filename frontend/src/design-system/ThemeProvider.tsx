/**
 * ThemeProvider
 * 
 * Diese Komponente stellt das Theme im gesamten System zur Verfügung.
 * Sie unterstützt auch den Wechsel zwischen Light- und Dark-Mode.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { lightTheme, darkTheme, Theme } from './theme';

// Theme-Kontext
interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (mode: 'light' | 'dark' | 'system') => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Hook für den Zugriff auf das Theme
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// ThemeProvider-Komponente
interface ThemeProviderProps {
  children: ReactNode;
  initialTheme?: 'light' | 'dark' | 'system';
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ 
  children, 
  initialTheme = 'system' 
}) => {
  // Bestimme das initiale Theme basierend auf der Systemeinstellung oder dem gespeicherten Wert
  const getInitialTheme = (): Theme => {
    const savedTheme = localStorage.getItem('theme-mode');
    
    if (savedTheme === 'light') return lightTheme;
    if (savedTheme === 'dark') return darkTheme;
    
    // Wenn 'system' oder kein Wert gespeichert ist, verwende die Systemeinstellung
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return darkTheme;
    }
    
    return lightTheme;
  };

  const [theme, setThemeState] = useState<Theme>(getInitialTheme());

  // Wechsle zwischen Light- und Dark-Mode
  const toggleTheme = () => {
    const newTheme = theme.mode === 'light' ? darkTheme : lightTheme;
    setThemeState(newTheme);
    localStorage.setItem('theme-mode', newTheme.mode);
  };

  // Setze das Theme explizit
  const setTheme = (mode: 'light' | 'dark' | 'system') => {
    if (mode === 'system') {
      localStorage.removeItem('theme-mode');
      const systemTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
        ? darkTheme
        : lightTheme;
      setThemeState(systemTheme);
    } else {
      const newTheme = mode === 'dark' ? darkTheme : lightTheme;
      setThemeState(newTheme);
      localStorage.setItem('theme-mode', mode);
    }
  };

  // Reagiere auf Änderungen der Systemeinstellung
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      // Nur anwenden, wenn 'system' ausgewählt ist (kein gespeicherter Wert)
      if (!localStorage.getItem('theme-mode')) {
        setThemeState(e.matches ? darkTheme : lightTheme);
      }
    };
    
    // Füge den Event-Listener hinzu
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
    } else {
      // Fallback für ältere Browser
      mediaQuery.addListener(handleChange);
    }
    
    // Entferne den Event-Listener beim Aufräumen
    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handleChange);
      } else {
        // Fallback für ältere Browser
        mediaQuery.removeListener(handleChange);
      }
    };
  }, []);

  // Setze das initiale Theme basierend auf dem übergebenen Wert
  useEffect(() => {
    if (initialTheme !== 'system') {
      setTheme(initialTheme);
    }
  }, [initialTheme]);

  // Erstelle das Kontext-Objekt
  const contextValue: ThemeContextType = {
    theme,
    toggleTheme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      <StyledThemeProvider theme={theme}>
        {children}
      </StyledThemeProvider>
    </ThemeContext.Provider>
  );
};

export default ThemeProvider;