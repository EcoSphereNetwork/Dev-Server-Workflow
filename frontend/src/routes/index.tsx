// src/routes/index.tsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import Login from '../pages/Login';
import Dashboard from '../pages/Dashboard';
import MCPServers from '../pages/MCPServers';
import MCPServerManager from '../pages/MCPServerManager';
import Workflows from '../pages/Workflows';
import Settings from '../pages/Settings';
import UserSettings from '../pages/UserSettings';
import Services from '../pages/Services';
import ServiceDetail from '../pages/ServiceDetail';
import Monitoring from '../pages/Monitoring';
import DockerManager from '../pages/DockerManager';
import useAuthStore from '../store/auth';

// Geschützte Route-Komponente
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

const AppRoutes: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Dashboard />} />
          <Route path="mcp-servers" element={<MCPServers />} />
          <Route path="mcp-manager" element={<MCPServerManager />} />
          <Route path="workflows" element={<Workflows />} />
          <Route path="services" element={<Services />} />
          <Route path="services/:id" element={<ServiceDetail />} />
          <Route path="monitoring" element={<Monitoring />} />
          <Route path="docker" element={<DockerManager />} />
          <Route path="settings" element={<Settings />} />
          <Route path="user-settings" element={<UserSettings />} />
        </Route>
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRoutes;