import React from 'react';
import { ThemeProvider } from 'styled-components';
import { GlobalStyles, theme } from './theme';
import AppRoutes from './routes';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyles />
      <AppRoutes />
    </ThemeProvider>
  );
}

export default App;
