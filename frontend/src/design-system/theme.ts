/**
 * Theme-System
 * 
 * Diese Datei definiert das Theme-System, das auf den Design-Tokens basiert.
 * Es unterstützt sowohl Light- als auch Dark-Mode.
 */

import { tokens } from './tokens';

// Theme-Interface
export interface Theme {
  mode: 'light' | 'dark';
  colors: {
    primary: string;
    primaryLight: string;
    primaryDark: string;
    secondary: string;
    secondaryLight: string;
    secondaryDark: string;
    background: string;
    surface: string;
    error: string;
    warning: string;
    success: string;
    info: string;
    text: {
      primary: string;
      secondary: string;
      disabled: string;
      hint: string;
    };
    divider: string;
  };
  typography: typeof tokens.typography;
  spacing: typeof tokens.spacing;
  borderRadius: typeof tokens.borderRadius;
  shadows: typeof tokens.shadows;
  transitions: typeof tokens.transitions;
  zIndex: typeof tokens.zIndex;
  breakpoints: typeof tokens.breakpoints;
}

// Light-Theme
export const lightTheme: Theme = {
  mode: 'light',
  colors: {
    primary: tokens.colors.primary[500],
    primaryLight: tokens.colors.primary[300],
    primaryDark: tokens.colors.primary[700],
    secondary: tokens.colors.secondary[500],
    secondaryLight: tokens.colors.secondary[300],
    secondaryDark: tokens.colors.secondary[700],
    background: tokens.colors.background.default,
    surface: tokens.colors.background.paper,
    error: tokens.colors.error.main,
    warning: tokens.colors.warning.main,
    success: tokens.colors.success.main,
    info: tokens.colors.info.main,
    text: {
      primary: tokens.colors.text.primary,
      secondary: tokens.colors.text.secondary,
      disabled: tokens.colors.text.disabled,
      hint: tokens.colors.text.hint,
    },
    divider: tokens.colors.divider,
  },
  typography: tokens.typography,
  spacing: tokens.spacing,
  borderRadius: tokens.borderRadius,
  shadows: tokens.shadows,
  transitions: tokens.transitions,
  zIndex: tokens.zIndex,
  breakpoints: tokens.breakpoints,
};

// Dark-Theme
export const darkTheme: Theme = {
  mode: 'dark',
  colors: {
    primary: tokens.colors.primary[400], // Etwas heller im Dark-Mode
    primaryLight: tokens.colors.primary[300],
    primaryDark: tokens.colors.primary[600],
    secondary: tokens.colors.secondary[400], // Etwas heller im Dark-Mode
    secondaryLight: tokens.colors.secondary[300],
    secondaryDark: tokens.colors.secondary[600],
    background: tokens.colors.background.dark,
    surface: tokens.colors.neutral[800],
    error: tokens.colors.error.light, // Heller im Dark-Mode
    warning: tokens.colors.warning.light, // Heller im Dark-Mode
    success: tokens.colors.success.light, // Heller im Dark-Mode
    info: tokens.colors.info.light, // Heller im Dark-Mode
    text: {
      primary: tokens.colors.text.primaryDark,
      secondary: tokens.colors.text.secondaryDark,
      disabled: tokens.colors.text.disabledDark,
      hint: tokens.colors.text.hintDark,
    },
    divider: tokens.colors.dividerDark,
  },
  typography: tokens.typography,
  spacing: tokens.spacing,
  borderRadius: tokens.borderRadius,
  shadows: tokens.shadows,
  transitions: tokens.transitions,
  zIndex: tokens.zIndex,
  breakpoints: tokens.breakpoints,
};

// Standardtheme
export const defaultTheme = lightTheme;

export default {
  light: lightTheme,
  dark: darkTheme,
};