/**
 * Settings Context
 * 
 * Kontext für Benutzereinstellungen, der in der gesamten Anwendung verfügbar ist.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserSettings, ColorScheme, UIDensity, Language } from '../types/settings';

// Standard-Einstellungen
const defaultSettings: UserSettings = {
  appearance: {
    colorScheme: 'system',
    density: 'comfortable',
    fontSize: 100,
    animations: true,
  },
  language: 'de',
  dashboard: {
    layout: {
      widgets: [],
    },
    autoRefresh: true,
    refreshInterval: 30,
  },
  notifications: {
    enabled: true,
    desktop: true,
    email: false,
    types: {
      system: true,
      services: true,
      workflows: true,
      security: true,
    },
  },
  assistant: {
    enabled: true,
    suggestions: true,
    autoComplete: true,
    voice: false,
  },
  services: {
    defaultView: 'grid',
    favorites: [],
  },
  security: {
    sessionTimeout: 30,
    twoFactorAuth: false,
  },
  advanced: {
    developerMode: false,
    experimentalFeatures: false,
    logging: false,
  },
};

// Settings Context Typ
interface SettingsContextType {
  settings: UserSettings;
  updateSettings: (newSettings: Partial<UserSettings>) => void;
  updateAppearance: (appearance: Partial<UserSettings['appearance']>) => void;
  updateDashboard: (dashboard: Partial<UserSettings['dashboard']>) => void;
  updateNotifications: (notifications: Partial<UserSettings['notifications']>) => void;
  updateAssistant: (assistant: Partial<UserSettings['assistant']>) => void;
  updateServices: (services: Partial<UserSettings['services']>) => void;
  updateSecurity: (security: Partial<UserSettings['security']>) => void;
  updateAdvanced: (advanced: Partial<UserSettings['advanced']>) => void;
  resetSettings: () => void;
  setColorScheme: (colorScheme: ColorScheme) => void;
  setDensity: (density: UIDensity) => void;
  setLanguage: (language: Language) => void;
  toggleFavoriteService: (serviceId: string) => void;
}

// Settings Context
const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

// Settings Provider Props
interface SettingsProviderProps {
  children: ReactNode;
}

// Settings Provider
export const SettingsProvider: React.FC<SettingsProviderProps> = ({ children }) => {
  // State für Einstellungen
  const [settings, setSettings] = useState<UserSettings>(() => {
    // Lade Einstellungen aus dem localStorage
    const savedSettings = localStorage.getItem('user-settings');
    if (savedSettings) {
      try {
        return JSON.parse(savedSettings);
      } catch (error) {
        console.error('Fehler beim Laden der Einstellungen:', error);
        return defaultSettings;
      }
    }
    return defaultSettings;
  });
  
  // Speichere Einstellungen im localStorage, wenn sie sich ändern
  useEffect(() => {
    localStorage.setItem('user-settings', JSON.stringify(settings));
  }, [settings]);
  
  // Aktualisiere Einstellungen
  const updateSettings = (newSettings: Partial<UserSettings>) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      ...newSettings,
    }));
  };
  
  // Aktualisiere Erscheinungsbild
  const updateAppearance = (appearance: Partial<UserSettings['appearance']>) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      appearance: {
        ...prevSettings.appearance,
        ...appearance,
      },
    }));
  };
  
  // Aktualisiere Dashboard
  const updateDashboard = (dashboard: Partial<UserSettings['dashboard']>) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      dashboard: {
        ...prevSettings.dashboard,
        ...dashboard,
      },
    }));
  };
  
  // Aktualisiere Benachrichtigungen
  const updateNotifications = (notifications: Partial<UserSettings['notifications']>) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      notifications: {
        ...prevSettings.notifications,
        ...notifications,
      },
    }));
  };
  
  // Aktualisiere Assistent
  const updateAssistant = (assistant: Partial<UserSettings['assistant']>) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      assistant: {
        ...prevSettings.assistant,
        ...assistant,
      },
    }));
  };
  
  // Aktualisiere Dienste
  const updateServices = (services: Partial<UserSettings['services']>) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      services: {
        ...prevSettings.services,
        ...services,
      },
    }));
  };
  
  // Aktualisiere Sicherheit
  const updateSecurity = (security: Partial<UserSettings['security']>) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      security: {
        ...prevSettings.security,
        ...security,
      },
    }));
  };
  
  // Aktualisiere Erweitert
  const updateAdvanced = (advanced: Partial<UserSettings['advanced']>) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      advanced: {
        ...prevSettings.advanced,
        ...advanced,
      },
    }));
  };
  
  // Setze Einstellungen zurück
  const resetSettings = () => {
    setSettings(defaultSettings);
  };
  
  // Setze Farbschema
  const setColorScheme = (colorScheme: ColorScheme) => {
    updateAppearance({ colorScheme });
  };
  
  // Setze Dichte
  const setDensity = (density: UIDensity) => {
    updateAppearance({ density });
  };
  
  // Setze Sprache
  const setLanguage = (language: Language) => {
    updateSettings({ language });
  };
  
  // Favorisiere/Entfavorisiere einen Dienst
  const toggleFavoriteService = (serviceId: string) => {
    setSettings(prevSettings => {
      const favorites = [...prevSettings.services.favorites];
      const index = favorites.indexOf(serviceId);
      
      if (index === -1) {
        favorites.push(serviceId);
      } else {
        favorites.splice(index, 1);
      }
      
      return {
        ...prevSettings,
        services: {
          ...prevSettings.services,
          favorites,
        },
      };
    });
  };
  
  // Kontext-Wert
  const contextValue: SettingsContextType = {
    settings,
    updateSettings,
    updateAppearance,
    updateDashboard,
    updateNotifications,
    updateAssistant,
    updateServices,
    updateSecurity,
    updateAdvanced,
    resetSettings,
    setColorScheme,
    setDensity,
    setLanguage,
    toggleFavoriteService,
  };
  
  return (
    <SettingsContext.Provider value={contextValue}>
      {children}
    </SettingsContext.Provider>
  );
};

// Hook für den Zugriff auf den Settings Context
export const useSettings = (): SettingsContextType => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

export default SettingsContext;