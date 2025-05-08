// src/theme.ts
import { createGlobalStyle } from 'styled-components';

// Definiere die Farbpalette
export const colors = {
  primary: {
    main: '#3f51b5',
    light: '#757de8',
    dark: '#002984',
    contrastText: '#ffffff'
  },
  secondary: {
    main: '#f50057',
    light: '#ff5983',
    dark: '#bb002f',
    contrastText: '#ffffff'
  },
  success: {
    main: '#4caf50',
    light: '#80e27e',
    dark: '#087f23',
    contrastText: '#ffffff'
  },
  warning: {
    main: '#ff9800',
    light: '#ffc947',
    dark: '#c66900',
    contrastText: '#000000'
  },
  error: {
    main: '#f44336',
    light: '#ff7961',
    dark: '#ba000d',
    contrastText: '#ffffff'
  },
  info: {
    main: '#2196f3',
    light: '#6ec6ff',
    dark: '#0069c0',
    contrastText: '#ffffff'
  },
  text: {
    primary: '#212121',
    secondary: '#757575',
    disabled: '#9e9e9e',
    hint: '#9e9e9e'
  },
  background: {
    default: '#f5f5f5',
    paper: '#ffffff',
    dark: '#121212'
  },
  divider: 'rgba(0, 0, 0, 0.12)'
};

// Definiere die Typografie
export const typography = {
  fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  fontSize: 14,
  fontWeightLight: 300,
  fontWeightRegular: 400,
  fontWeightMedium: 500,
  fontWeightBold: 700,
  h1: {
    fontSize: '2.5rem',
    fontWeight: 300,
    lineHeight: 1.2
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 300,
    lineHeight: 1.2
  },
  h3: {
    fontSize: '1.75rem',
    fontWeight: 400,
    lineHeight: 1.2
  },
  h4: {
    fontSize: '1.5rem',
    fontWeight: 400,
    lineHeight: 1.2
  },
  h5: {
    fontSize: '1.25rem',
    fontWeight: 400,
    lineHeight: 1.2
  },
  h6: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.2
  },
  body1: {
    fontSize: '1rem',
    fontWeight: 400,
    lineHeight: 1.5
  },
  body2: {
    fontSize: '0.875rem',
    fontWeight: 400,
    lineHeight: 1.5
  },
  button: {
    fontSize: '0.875rem',
    fontWeight: 500,
    lineHeight: 1.75,
    textTransform: 'uppercase'
  },
  caption: {
    fontSize: '0.75rem',
    fontWeight: 400,
    lineHeight: 1.66
  },
  overline: {
    fontSize: '0.75rem',
    fontWeight: 400,
    lineHeight: 2.66,
    textTransform: 'uppercase'
  }
};

// Definiere die Abstände
export const spacing = {
  unit: 8,
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48
};

// Definiere die Schatten
export const shadows = {
  none: 'none',
  sm: '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
  md: '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
  lg: '0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)',
  xl: '0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22)',
  xxl: '0 19px 38px rgba(0,0,0,0.30), 0 15px 12px rgba(0,0,0,0.22)'
};

// Definiere die Übergänge
export const transitions = {
  easing: {
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    sharp: 'cubic-bezier(0.4, 0, 0.6, 1)'
  },
  duration: {
    shortest: 150,
    shorter: 200,
    short: 250,
    standard: 300,
    complex: 375,
    enteringScreen: 225,
    leavingScreen: 195
  }
};

// Definiere die Abrundungen
export const shape = {
  borderRadius: {
    none: 0,
    sm: 2,
    md: 4,
    lg: 8,
    xl: 12,
    xxl: 16,
    full: 9999
  }
};

// Definiere die Z-Indizes
export const zIndex = {
  mobileStepper: 1000,
  speedDial: 1050,
  appBar: 1100,
  drawer: 1200,
  modal: 1300,
  snackbar: 1400,
  tooltip: 1500
};

// Exportiere das Theme-Objekt
export const theme = {
  colors,
  typography,
  spacing,
  shadows,
  transitions,
  shape,
  zIndex
};

// Globale Styles
export const GlobalStyles = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  html, body {
    height: 100%;
    font-family: ${typography.fontFamily};
    font-size: ${typography.fontSize}px;
    line-height: 1.5;
    color: ${colors.text.primary};
    background-color: ${colors.background.default};
  }

  #root {
    height: 100%;
  }

  a {
    color: ${colors.primary.main};
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }

  button {
    font-family: ${typography.fontFamily};
    font-size: ${typography.button.fontSize};
    font-weight: ${typography.button.fontWeight};
  }

  h1, h2, h3, h4, h5, h6 {
    margin-bottom: ${spacing.md}px;
  }

  p {
    margin-bottom: ${spacing.md}px;
  }
`;

export default theme;