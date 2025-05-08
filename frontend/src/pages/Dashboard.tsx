// src/pages/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import apiClient from '../api/client';
import { colors } from '../theme';

// Typen für die Dashboard-Daten
interface DashboardStats {
  mcpServers: {
    total: number;
    online: number;
    offline: number;
  };
  workflows: {
    total: number;
    active: number;
    inactive: number;
  };
  containers: {
    total: number;
    running: number;
    stopped: number;
  };
  systemResources: {
    cpuUsage: number;
    memoryUsage: number;
    diskUsage: number;
  };
}

const DashboardContainer = styled.div`
  padding: 20px;
`;

const DashboardTitle = styled.h1`
  font-size: 1.5rem;
  margin-bottom: 20px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled(Card)`
  padding: 20px;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 500;
  margin: 10px 0;
  color: ${colors.primary.main};
`;

const StatLabel = styled.div`
  font-size: 1rem;
  color: ${colors.text.secondary};
`;

const StatDetail = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 0.875rem;
`;

const StatDetailItem = styled.div<{ $color?: string }>`
  color: ${props => props.$color || colors.text.primary};
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
`;

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
        // const response = await apiClient.get('/dashboard/stats');
        // setStats(response.data);
        
        // Simulierte Daten für die Entwicklung
        setStats({
          mcpServers: {
            total: 5,
            online: 3,
            offline: 2
          },
          workflows: {
            total: 12,
            active: 8,
            inactive: 4
          },
          containers: {
            total: 15,
            running: 10,
            stopped: 5
          },
          systemResources: {
            cpuUsage: 35,
            memoryUsage: 42,
            diskUsage: 68
          }
        });
      } catch (err: any) {
        setError('Fehler beim Laden der Dashboard-Daten');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    
    // Aktualisiere die Daten alle 30 Sekunden
    const interval = setInterval(fetchDashboardData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return <div>Lade Dashboard-Daten...</div>;
  }

  if (error) {
    return <div>Fehler: {error}</div>;
  }

  if (!stats) {
    return <div>Keine Daten verfügbar</div>;
  }

  return (
    <DashboardContainer>
      <DashboardTitle>Dashboard</DashboardTitle>
      
      <ActionButtons>
        <Button variant="primary">Neuer MCP-Server</Button>
        <Button variant="secondary">Neuer Workflow</Button>
        <Button variant="outlined">System-Status</Button>
      </ActionButtons>
      
      <StatsGrid>
        <StatCard>
          <StatLabel>MCP-Server</StatLabel>
          <StatValue>{stats.mcpServers.total}</StatValue>
          <StatDetail>
            <StatDetailItem $color={colors.success.main}>
              {stats.mcpServers.online} Online
            </StatDetailItem>
            <StatDetailItem $color={colors.error.main}>
              {stats.mcpServers.offline} Offline
            </StatDetailItem>
          </StatDetail>
        </StatCard>
        
        <StatCard>
          <StatLabel>Workflows</StatLabel>
          <StatValue>{stats.workflows.total}</StatValue>
          <StatDetail>
            <StatDetailItem $color={colors.success.main}>
              {stats.workflows.active} Aktiv
            </StatDetailItem>
            <StatDetailItem $color={colors.warning.main}>
              {stats.workflows.inactive} Inaktiv
            </StatDetailItem>
          </StatDetail>
        </StatCard>
        
        <StatCard>
          <StatLabel>Container</StatLabel>
          <StatValue>{stats.containers.total}</StatValue>
          <StatDetail>
            <StatDetailItem $color={colors.success.main}>
              {stats.containers.running} Laufend
            </StatDetailItem>
            <StatDetailItem $color={colors.warning.main}>
              {stats.containers.stopped} Gestoppt
            </StatDetailItem>
          </StatDetail>
        </StatCard>
        
        <StatCard>
          <StatLabel>CPU-Auslastung</StatLabel>
          <StatValue>{stats.systemResources.cpuUsage}%</StatValue>
          <progress 
            value={stats.systemResources.cpuUsage} 
            max="100" 
            style={{ width: '100%' }}
          />
        </StatCard>
        
        <StatCard>
          <StatLabel>Speicher-Auslastung</StatLabel>
          <StatValue>{stats.systemResources.memoryUsage}%</StatValue>
          <progress 
            value={stats.systemResources.memoryUsage} 
            max="100" 
            style={{ width: '100%' }}
          />
        </StatCard>
        
        <StatCard>
          <StatLabel>Festplatten-Auslastung</StatLabel>
          <StatValue>{stats.systemResources.diskUsage}%</StatValue>
          <progress 
            value={stats.systemResources.diskUsage} 
            max="100" 
            style={{ width: '100%' }}
          />
        </StatCard>
      </StatsGrid>
    </DashboardContainer>
  );
};

export default Dashboard;