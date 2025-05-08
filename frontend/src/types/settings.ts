/**
 * Benutzereinstellungen-Typen
 */

// Farbschema
export type ColorScheme = 'light' | 'dark' | 'system';

// Dichte der Benutzeroberfläche
export type UIDensity = 'compact' | 'comfortable' | 'spacious';

// Sprache
export type Language = 'de' | 'en' | 'fr' | 'es';

// Dashboard-Layout
export interface DashboardLayout {
  widgets: Array<{
    id: string;
    position: { x: number; y: number; w: number; h: number };
    type: string;
    config?: Record<string, any>;
  }>;
}

// Benachrichtigungseinstellungen
export interface NotificationSettings {
  enabled: boolean;
  desktop: boolean;
  email: boolean;
  types: {
    system: boolean;
    services: boolean;
    workflows: boolean;
    security: boolean;
  };
}

// Benutzereinstellungen
export interface UserSettings {
  // Erscheinungsbild
  appearance: {
    colorScheme: ColorScheme;
    density: UIDensity;
    fontSize: number; // in Prozent (100 = Standard)
    animations: boolean;
  };
  
  // Sprache
  language: Language;
  
  // Dashboard
  dashboard: {
    layout: DashboardLayout;
    autoRefresh: boolean;
    refreshInterval: number; // in Sekunden
  };
  
  // Benachrichtigungen
  notifications: NotificationSettings;
  
  // KI-Assistent
  assistant: {
    enabled: boolean;
    suggestions: boolean;
    autoComplete: boolean;
    voice: boolean;
  };
  
  // Dienste
  services: {
    defaultView: 'grid' | 'list';
    favorites: string[]; // IDs der favorisierten Dienste
  };
  
  // Sicherheit
  security: {
    sessionTimeout: number; // in Minuten
    twoFactorAuth: boolean;
  };
  
  // Erweitert
  advanced: {
    developerMode: boolean;
    experimentalFeatures: boolean;
    logging: boolean;
  };
}