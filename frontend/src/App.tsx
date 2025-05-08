import React from 'react';
import { ThemeProvider, GlobalStyles } from './design-system';
import { SettingsProvider } from './context/SettingsContext';
import { ServicesProvider } from './context/ServicesContext';
import AppRoutes from './routes';

function App() {
  return (
    <SettingsProvider>
      <ServicesProvider>
        <ThemeProvider initialTheme="system">
          <GlobalStyles />
          <div className="skip-link" tabIndex={0}>
            Skip to main content
          </div>
          <AppRoutes />
        </ThemeProvider>
      </ServicesProvider>
    </SettingsProvider>
  );
}

export default App;
