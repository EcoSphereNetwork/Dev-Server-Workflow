import React from 'react';
import { ThemeProvider, GlobalStyles } from './design-system';
import AppRoutes from './routes';

function App() {
  return (
    <ThemeProvider initialTheme="system">
      <GlobalStyles />
      <div className="skip-link" tabIndex={0}>
        Skip to main content
      </div>
      <AppRoutes />
    </ThemeProvider>
  );
}

export default App;
