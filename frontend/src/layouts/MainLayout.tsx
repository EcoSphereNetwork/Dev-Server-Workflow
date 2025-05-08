// src/layouts/MainLayout.tsx
import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { Sidebar, SidebarItem } from '../components/common/Sidebar';
import Navbar from '../components/common/Navbar';
import useAuthStore from '../store/auth';

// Icons (simplified for this example)
const DashboardIcon = () => <span>📊</span>;
const MCPIcon = () => <span>🖥️</span>;
const WorkflowIcon = () => <span>🔄</span>;
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
          icon={<WorkflowIcon />} 
          label="Workflows" 
          active={location.pathname.startsWith('/workflows')} 
          onClick={() => navigate('/workflows')} 
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
    </LayoutContainer>
  );
};

export default MainLayout;