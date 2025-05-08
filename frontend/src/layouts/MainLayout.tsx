// src/layouts/MainLayout.tsx
import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { Sidebar, SidebarItem } from '../components/common/Sidebar';
import Navbar from '../components/common/Navbar';
import AIAssistant from '../components/AIAssistant';
import { ServiceSidebar, ServiceWebView, ServiceMenu } from '../components/ServiceIntegration';
import useAuthStore from '../store/auth';
import { useTheme, Button } from '../design-system';

// Icons (simplified for this example)
const DashboardIcon = () => <span>📊</span>;
const MCPIcon = () => <span>🖥️</span>;
const MCPManagerIcon = () => <span>🔌</span>;
const WorkflowIcon = () => <span>🔄</span>;
const ServicesIcon = () => <span>🌐</span>;
const MonitoringIcon = () => <span>📈</span>;
const DockerIcon = () => <span>🐳</span>;
const SettingsIcon = () => <span>⚙️</span>;
const UserIcon = () => <span>👤</span>;
const ThemeIcon = () => <span>{useTheme().theme.mode === 'dark' ? '🌙' : '☀️'}</span>;

const LayoutContainer = styled.div`
  display: flex;
  height: 100vh;
  overflow: hidden;
  background-color: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.text.primary};
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const ContentArea = styled.div`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  overflow: auto;
`;

const UserMenu = styled.div`
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: ${props => props.theme.spacing.xs};
  border-radius: ${props => props.theme.borderRadius.sm};
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }
  
  .user-name {
    margin-left: ${props => props.theme.spacing.xs};
  }
`;

const IconButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  padding: ${props => props.theme.spacing.xs};
  border-radius: ${props => props.theme.borderRadius.full};
  color: ${props => props.theme.colors.text.primary};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const MainLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [serviceSidebarOpen, setServiceSidebarOpen] = useState(false);
  const [serviceWebViewOpen, setServiceWebViewOpen] = useState(false);
  const [selectedServiceId, setSelectedServiceId] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { toggleTheme, theme } = useTheme();
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <LayoutContainer>
      <Sidebar 
        open={sidebarOpen} 
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      >
        <SidebarItem 
          icon={<DashboardIcon />} 
          label="Dashboard" 
          active={location.pathname === '/'} 
          onClick={() => navigate('/')} 
        />
        <SidebarItem 
          icon={<MCPIcon />} 
          label="MCP-Server" 
          active={location.pathname.startsWith('/mcp-servers')} 
          onClick={() => navigate('/mcp-servers')} 
        />
        <SidebarItem 
          icon={<MCPManagerIcon />} 
          label="MCP-Manager" 
          active={location.pathname.startsWith('/mcp-manager')} 
          onClick={() => navigate('/mcp-manager')} 
        />
        <SidebarItem 
          icon={<WorkflowIcon />} 
          label="Workflows" 
          active={location.pathname.startsWith('/workflows')} 
          onClick={() => navigate('/workflows')} 
        />
        <SidebarItem 
          icon={<ServicesIcon />} 
          label="Dienste" 
          active={location.pathname.startsWith('/services')} 
          onClick={() => navigate('/services')} 
        />
        <SidebarItem 
          icon={<MonitoringIcon />} 
          label="Monitoring" 
          active={location.pathname.startsWith('/monitoring')} 
          onClick={() => navigate('/monitoring')} 
        />
        <SidebarItem 
          icon={<DockerIcon />} 
          label="Docker" 
          active={location.pathname.startsWith('/docker')} 
          onClick={() => navigate('/docker')} 
        />
        <SidebarItem 
          icon={<SettingsIcon />} 
          label="Einstellungen" 
          active={location.pathname.startsWith('/settings')} 
          onClick={() => navigate('/settings')} 
        />
        
        <ServiceMenu 
          onSelectService={(serviceId) => {
            setSelectedServiceId(serviceId);
            setServiceWebViewOpen(true);
          }} 
        />
      </Sidebar>
      
      <MainContent>
        <Navbar>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: theme.spacing.md }}>
            <IconButton
              onClick={toggleTheme}
              title={`Zum ${theme.mode === 'dark' ? 'Light' : 'Dark'}-Mode wechseln`}
              aria-label={`Zum ${theme.mode === 'dark' ? 'Light' : 'Dark'}-Mode wechseln`}
            >
              <ThemeIcon />
            </IconButton>
            
            <IconButton
              onClick={() => setServiceSidebarOpen(true)}
              title="Dienste"
              aria-label="Dienste öffnen"
            >
              🌐
            </IconButton>
            
            <IconButton
              onClick={() => setAssistantOpen(!assistantOpen)}
              title="KI-Assistent"
              aria-label="KI-Assistent öffnen"
            >
              🤖
            </IconButton>
            
            <UserMenu 
              onClick={() => navigate('/user-settings')}
              role="button"
              tabIndex={0}
              aria-label="Benutzereinstellungen öffnen"
            >
              <UserIcon />
              <span className="user-name">{user?.name || user?.username || 'Benutzer'}</span>
            </UserMenu>
            
            <Button 
              variant="text" 
              size="sm"
              onClick={handleLogout}
              aria-label="Abmelden"
            >
              Abmelden
            </Button>
          </div>
        </Navbar>
        
        <ContentArea>
          <Outlet />
        </ContentArea>
      </MainContent>
      
      <AIAssistant 
        isOpen={assistantOpen} 
        onClose={() => setAssistantOpen(!assistantOpen)} 
      />
      
      <ServiceSidebar
        isOpen={serviceSidebarOpen}
        onClose={() => setServiceSidebarOpen(false)}
      />
      
      {selectedServiceId && (
        <ServiceWebView
          serviceId={selectedServiceId}
          isOpen={serviceWebViewOpen}
          onClose={() => {
            setServiceWebViewOpen(false);
            setSelectedServiceId(null);
          }}
        />
      )}
    </LayoutContainer>
  );
};

export default MainLayout;