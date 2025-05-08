/**
 * Globale Styles
 * 
 * Diese Datei definiert globale Styles für die Anwendung,
 * einschließlich Barrierefreiheits-Verbesserungen.
 */

import { createGlobalStyle } from 'styled-components';
import { Theme } from '../theme';

export const GlobalStyles = createGlobalStyle<{ theme: Theme }>`
  /* Basis-Styles */
  *, *::before, *::after {
    box-sizing: border-box;
  }
  
  html {
    font-size: 16px;
    line-height: 1.5;
    -webkit-text-size-adjust: 100%;
  }
  
  body {
    margin: 0;
    font-family: ${props => props.theme.typography.fontFamily.primary};
    font-size: ${props => props.theme.typography.fontSize.md};
    font-weight: ${props => props.theme.typography.fontWeight.regular};
    line-height: ${props => props.theme.typography.lineHeight.md};
    color: ${props => props.theme.colors.text.primary};
    background-color: ${props => props.theme.colors.background};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  /* Barrierefreiheits-Verbesserungen */
  
  /* Verbesserte Fokus-Styles */
  :focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
  
  /* Verbesserte Kontraste für Text */
  .text-high-contrast {
    color: ${props => props.theme.mode === 'dark' ? '#ffffff' : '#000000'};
  }
  
  /* Skip-Link für Tastatur-Navigation */
  .skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: ${props => props.theme.colors.primary};
    color: white;
    padding: 8px;
    z-index: 100;
    
    &:focus {
      top: 0;
    }
  }
  
  /* Reduzierte Bewegung für Benutzer, die Animationen deaktiviert haben */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
  
  /* Verbesserte Lesbarkeit für Screenreader */
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
  }
  
  /* Verbesserte Lesbarkeit für Benutzer mit Sehbehinderungen */
  @media (prefers-contrast: more) {
    :root {
      --color-primary: #0000ff;
      --color-error: #ff0000;
    }
    
    a {
      text-decoration: underline !important;
    }
    
    button, [role="button"] {
      border: 1px solid currentColor !important;
    }
  }
  
  /* Verbesserte Interaktivität für Touch-Geräte */
  @media (hover: none) {
    button, [role="button"], a {
      min-height: 44px;
      min-width: 44px;
    }
  }
`;

export default GlobalStyles;