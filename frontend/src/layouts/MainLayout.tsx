// src/layouts/MainLayout.tsx
import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { Sidebar, SidebarItem } from '../components/common/Sidebar';
import Navbar from '../components/common/Navbar';
import AIAssistant from '../components/AIAssistant';
import useAuthStore from '../store/auth';

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

const LayoutContainer = styled.div`
  display: flex;
  height: 100vh;
  overflow: hidden;
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const ContentArea = styled.div`
  flex: 1;
  padding: 20px;
  overflow: auto;
`;

const UserMenu = styled.div`
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }
  
  .user-name {
    margin-left: 8px;
  }
`;

const MainLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [assistantOpen, setAssistantOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  
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
      </Sidebar>
      
      <MainContent>
        <Navbar>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center' }}>
            <button 
              style={{ 
                marginRight: '16px', 
                background: 'none', 
                border: 'none', 
                cursor: 'pointer',
                fontSize: '1.25rem'
              }}
              onClick={() => setAssistantOpen(!assistantOpen)}
              title="KI-Assistent"
            >
              🤖
            </button>
            <UserMenu onClick={() => navigate('/profile')}>
              <UserIcon />
              <span className="user-name">{user?.name || user?.username || 'Benutzer'}</span>
            </UserMenu>
            <button 
              style={{ marginLeft: '16px', background: 'none', border: 'none', cursor: 'pointer' }}
              onClick={handleLogout}
            >
              Abmelden
            </button>
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
    </LayoutContainer>
  );
};

export default MainLayout;