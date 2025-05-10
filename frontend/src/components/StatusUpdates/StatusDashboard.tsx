/**
 * StatusDashboard Component
 * 
 * A component for displaying real-time status updates for all services and components
 */

import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { Card, Badge, Spinner, Button } from '../../design-system';
import { useServices } from '../../context/ServicesContext';

// Types for system status
interface SystemStatus {
  cpu: number;
  memory: number;
  disk: number;
  uptime: string;
  lastUpdated: Date;
}

interface ServiceStatus {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'error';
  uptime?: string;
  cpu?: number;
  memory?: number;
  version?: string;
  lastUpdated: Date;
}

interface WorkflowStatus {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'error';
  lastExecution?: Date;
  executionCount: number;
  errorCount: number;
  lastUpdated: Date;
}

// Styled components
const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
`;

const DashboardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const DashboardTitle = styled.h2`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.xl};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const LastUpdated = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const StatusGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.md};
`;

const StatusCard = styled(Card)<{ $status?: string }>`
  padding: ${props => props.theme.spacing.md};
  border-top: 4px solid ${props => {
    if (!props.$status) return props.theme.colors.primary;
    switch (props.$status) {
      case 'running':
      case 'active':
        return props.theme.colors.success.main;
      case 'stopped':
      case 'inactive':
        return props.theme.colors.warning.main;
      case 'error':
        return props.theme.colors.error;
      default:
        return props.theme.colors.primary;
    }
  }};
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const CardTitle = styled.h3`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const StatusBadge = styled(Badge)<{ $status?: string }>`
  text-transform: capitalize;
`;

const MetricGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${props => props.theme.spacing.md};
`;

const Metric = styled.div`
  display: flex;
  flex-direction: column;
`;

const MetricLabel = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const MetricValue = styled.div`
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const ProgressBar = styled.div`
  height: 8px;
  background-color: ${props => props.theme.colors.background.default};
  border-radius: ${props => props.theme.borderRadius.full};
  overflow: hidden;
  margin-top: ${props => props.theme.spacing.xs};
`;

const Progress = styled.div<{ $value: number; $color?: string }>`
  height: 100%;
  width: ${props => `${props.$value}%`};
  background-color: ${props => {
    if (props.$color) return props.$color;
    if (props.$value < 50) return props.theme.colors.success.main;
    if (props.$value < 80) return props.theme.colors.warning.main;
    return props.theme.colors.error;
  }};
  transition: width 0.3s ease;
`;

const SystemMetrics = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const MetricRow = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xs};
`;

const MetricHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.theme.spacing.xl};
`;

const ConnectionStatus = styled.div<{ $connected: boolean }>`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.$connected ? props.theme.colors.success.main : props.theme.colors.error};
`;

const StatusDot = styled.div<{ $connected: boolean }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${props => props.$connected ? props.theme.colors.success.main : props.theme.colors.error};
`;

// Mock API function to fetch system status
const fetchSystemStatus = async (): Promise<SystemStatus> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Mock data
  return {
    cpu: Math.floor(Math.random() * 60) + 10, // 10-70%
    memory: Math.floor(Math.random() * 50) + 30, // 30-80%
    disk: Math.floor(Math.random() * 30) + 40, // 40-70%
    uptime: '3d 7h 22m',
    lastUpdated: new Date()
  };
};

// Mock API function to fetch service statuses
const fetchServiceStatuses = async (): Promise<ServiceStatus[]> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 700));
  
  // Mock data
  return [
    {
      id: 'n8n',
      name: 'n8n',
      status: 'running',
      uptime: '3d 5h 12m',
      cpu: Math.floor(Math.random() * 30) + 5, // 5-35%
      memory: Math.floor(Math.random() * 40) + 20, // 20-60%
      version: '0.219.0',
      lastUpdated: new Date()
    },
    {
      id: 'mcp-hub',
      name: 'MCP Hub',
      status: 'running',
      uptime: '3d 5h 10m',
      cpu: Math.floor(Math.random() * 20) + 5, // 5-25%
      memory: Math.floor(Math.random() * 30) + 10, // 10-40%
      version: '0.1.0',
      lastUpdated: new Date()
    },
    {
      id: 'docker-mcp',
      name: 'Docker MCP',
      status: 'running',
      uptime: '3d 5h 8m',
      cpu: Math.floor(Math.random() * 15) + 3, // 3-18%
      memory: Math.floor(Math.random() * 25) + 10, // 10-35%
      version: '0.1.0',
      lastUpdated: new Date()
    },
    {
      id: 'n8n-mcp',
      name: 'n8n MCP',
      status: Math.random() > 0.8 ? 'error' : 'running', // Occasionally show error
      uptime: '1d 2h 45m',
      cpu: Math.floor(Math.random() * 25) + 5, // 5-30%
      memory: Math.floor(Math.random() * 35) + 15, // 15-50%
      version: '0.1.0',
      lastUpdated: new Date()
    },
    {
      id: 'prometheus',
      name: 'Prometheus',
      status: 'running',
      uptime: '3d 5h 5m',
      cpu: Math.floor(Math.random() * 20) + 5, // 5-25%
      memory: Math.floor(Math.random() * 40) + 30, // 30-70%
      version: '2.43.0',
      lastUpdated: new Date()
    },
    {
      id: 'grafana',
      name: 'Grafana',
      status: 'running',
      uptime: '3d 5h 3m',
      cpu: Math.floor(Math.random() * 15) + 3, // 3-18%
      memory: Math.floor(Math.random() * 30) + 10, // 10-40%
      version: '9.5.1',
      lastUpdated: new Date()
    }
  ];
};

// Mock API function to fetch workflow statuses
const fetchWorkflowStatuses = async (): Promise<WorkflowStatus[]> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // Mock data
  return [
    {
      id: '1',
      name: 'GitHub to OpenProject',
      status: 'active',
      lastExecution: new Date(Date.now() - 3600000),
      executionCount: 127,
      errorCount: 3,
      lastUpdated: new Date()
    },
    {
      id: '2',
      name: 'Document Synchronization',
      status: 'active',
      lastExecution: new Date(Date.now() - 7200000),
      executionCount: 84,
      errorCount: 5,
      lastUpdated: new Date()
    },
    {
      id: '3',
      name: 'OpenHands Integration',
      status: 'inactive',
      executionCount: 42,
      errorCount: 8,
      lastUpdated: new Date()
    },
    {
      id: '4',
      name: 'Discord Notifications',
      status: Math.random() > 0.8 ? 'error' : 'active', // Occasionally show error
      lastExecution: new Date(Date.now() - 1800000),
      executionCount: 215,
      errorCount: 12,
      lastUpdated: new Date()
    }
  ];
};

// Format date to relative time
const formatRelativeTime = (date: Date): string => {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  
  if (diffDay > 0) {
    return `${diffDay} ${diffDay === 1 ? 'day' : 'days'} ago`;
  } else if (diffHour > 0) {
    return `${diffHour} ${diffHour === 1 ? 'hour' : 'hours'} ago`;
  } else if (diffMin > 0) {
    return `${diffMin} ${diffMin === 1 ? 'minute' : 'minutes'} ago`;
  } else {
    return 'just now';
  }
};

// StatusDashboard component
export const StatusDashboard: React.FC = () => {
  // State
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [serviceStatuses, setServiceStatuses] = useState<ServiceStatus[]>([]);
  const [workflowStatuses, setWorkflowStatuses] = useState<WorkflowStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  
  // WebSocket reference
  const wsRef = useRef<WebSocket | null>(null);
  
  // Services context
  const { refreshServices } = useServices();
  
  // Initialize WebSocket connection
  useEffect(() => {
    // In a real application, this would connect to a real WebSocket server
    // For this demo, we'll simulate WebSocket updates with setInterval
    
    // Simulate initial data loading
    const loadInitialData = async () => {
      setLoading(true);
      try {
        const [system, services, workflows] = await Promise.all([
          fetchSystemStatus(),
          fetchServiceStatuses(),
          fetchWorkflowStatuses()
        ]);
        
        setSystemStatus(system);
        setServiceStatuses(services);
        setWorkflowStatuses(workflows);
        setLastUpdated(new Date());
        setConnected(true);
        
        // Refresh services in the global context
        refreshServices();
      } catch (error) {
        console.error('Error loading status data:', error);
        setConnected(false);
      } finally {
        setLoading(false);
      }
    };
    
    loadInitialData();
    
    // Simulate WebSocket updates
    const intervalId = setInterval(async () => {
      try {
        // Simulate occasional connection issues
        if (Math.random() > 0.95) {
          setConnected(false);
          return;
        }
        
        const [system, services, workflows] = await Promise.all([
          fetchSystemStatus(),
          fetchServiceStatuses(),
          fetchWorkflowStatuses()
        ]);
        
        setSystemStatus(system);
        setServiceStatuses(services);
        setWorkflowStatuses(workflows);
        setLastUpdated(new Date());
        setConnected(true);
        
        // Refresh services in the global context
        refreshServices();
      } catch (error) {
        console.error('Error updating status data:', error);
        setConnected(false);
      }
    }, 10000); // Update every 10 seconds
    
    // Cleanup
    return () => {
      clearInterval(intervalId);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [refreshServices]);
  
  // Handle reconnect
  const handleReconnect = async () => {
    setLoading(true);
    try {
      const [system, services, workflows] = await Promise.all([
        fetchSystemStatus(),
        fetchServiceStatuses(),
        fetchWorkflowStatuses()
      ]);
      
      setSystemStatus(system);
      setServiceStatuses(services);
      setWorkflowStatuses(workflows);
      setLastUpdated(new Date());
      setConnected(true);
      
      // Refresh services in the global context
      refreshServices();
    } catch (error) {
      console.error('Error reconnecting:', error);
      setConnected(false);
    } finally {
      setLoading(false);
    }
  };
  
  // Get status color
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'running':
      case 'active':
        return 'success';
      case 'stopped':
      case 'inactive':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'primary';
    }
  };
  
  return (
    <DashboardContainer>
      <DashboardHeader>
        <DashboardTitle>System Status</DashboardTitle>
        <LastUpdated>
          {connected ? (
            <ConnectionStatus $connected={true}>
              <StatusDot $connected={true} />
              Connected
            </ConnectionStatus>
          ) : (
            <ConnectionStatus $connected={false}>
              <StatusDot $connected={false} />
              Disconnected
              <Button
                variant="text"
                size="sm"
                onClick={handleReconnect}
              >
                Reconnect
              </Button>
            </ConnectionStatus>
          )}
          {lastUpdated && (
            <div>Last updated: {formatRelativeTime(lastUpdated)}</div>
          )}
        </LastUpdated>
      </DashboardHeader>
      
      {loading ? (
        <LoadingContainer>
          <Spinner size="lg" />
        </LoadingContainer>
      ) : (
        <>
          {systemStatus && (
            <StatusCard>
              <CardHeader>
                <CardTitle>System Overview</CardTitle>
              </CardHeader>
              
              <SystemMetrics>
                <MetricRow>
                  <MetricHeader>
                    <MetricLabel>CPU Usage</MetricLabel>
                    <MetricValue>{systemStatus.cpu}%</MetricValue>
                  </MetricHeader>
                  <ProgressBar>
                    <Progress $value={systemStatus.cpu} />
                  </ProgressBar>
                </MetricRow>
                
                <MetricRow>
                  <MetricHeader>
                    <MetricLabel>Memory Usage</MetricLabel>
                    <MetricValue>{systemStatus.memory}%</MetricValue>
                  </MetricHeader>
                  <ProgressBar>
                    <Progress $value={systemStatus.memory} />
                  </ProgressBar>
                </MetricRow>
                
                <MetricRow>
                  <MetricHeader>
                    <MetricLabel>Disk Usage</MetricLabel>
                    <MetricValue>{systemStatus.disk}%</MetricValue>
                  </MetricHeader>
                  <ProgressBar>
                    <Progress $value={systemStatus.disk} />
                  </ProgressBar>
                </MetricRow>
                
                <MetricRow>
                  <MetricHeader>
                    <MetricLabel>System Uptime</MetricLabel>
                    <MetricValue>{systemStatus.uptime}</MetricValue>
                  </MetricHeader>
                </MetricRow>
              </SystemMetrics>
            </StatusCard>
          )}
          
          <h3>Services</h3>
          <StatusGrid>
            {serviceStatuses.map(service => (
              <StatusCard key={service.id} $status={service.status}>
                <CardHeader>
                  <CardTitle>{service.name}</CardTitle>
                  <StatusBadge 
                    color={getStatusColor(service.status)}
                    $status={service.status}
                  >
                    {service.status}
                  </StatusBadge>
                </CardHeader>
                
                <MetricGrid>
                  {service.uptime && (
                    <Metric>
                      <MetricLabel>Uptime</MetricLabel>
                      <MetricValue>{service.uptime}</MetricValue>
                    </Metric>
                  )}
                  
                  {service.version && (
                    <Metric>
                      <MetricLabel>Version</MetricLabel>
                      <MetricValue>{service.version}</MetricValue>
                    </Metric>
                  )}
                  
                  {service.cpu !== undefined && (
                    <Metric>
                      <MetricLabel>CPU</MetricLabel>
                      <MetricValue>{service.cpu}%</MetricValue>
                      <ProgressBar>
                        <Progress $value={service.cpu} />
                      </ProgressBar>
                    </Metric>
                  )}
                  
                  {service.memory !== undefined && (
                    <Metric>
                      <MetricLabel>Memory</MetricLabel>
                      <MetricValue>{service.memory}%</MetricValue>
                      <ProgressBar>
                        <Progress $value={service.memory} />
                      </ProgressBar>
                    </Metric>
                  )}
                </MetricGrid>
              </StatusCard>
            ))}
          </StatusGrid>
          
          <h3>Workflows</h3>
          <StatusGrid>
            {workflowStatuses.map(workflow => (
              <StatusCard key={workflow.id} $status={workflow.status}>
                <CardHeader>
                  <CardTitle>{workflow.name}</CardTitle>
                  <StatusBadge 
                    color={getStatusColor(workflow.status)}
                    $status={workflow.status}
                  >
                    {workflow.status}
                  </StatusBadge>
                </CardHeader>
                
                <MetricGrid>
                  {workflow.lastExecution && (
                    <Metric>
                      <MetricLabel>Last Execution</MetricLabel>
                      <MetricValue>{formatRelativeTime(workflow.lastExecution)}</MetricValue>
                    </Metric>
                  )}
                  
                  <Metric>
                    <MetricLabel>Executions</MetricLabel>
                    <MetricValue>{workflow.executionCount}</MetricValue>
                  </Metric>
                  
                  <Metric>
                    <MetricLabel>Errors</MetricLabel>
                    <MetricValue>{workflow.errorCount}</MetricValue>
                  </Metric>
                  
                  <Metric>
                    <MetricLabel>Success Rate</MetricLabel>
                    <MetricValue>
                      {workflow.executionCount > 0
                        ? `${Math.round(((workflow.executionCount - workflow.errorCount) / workflow.executionCount) * 100)}%`
                        : 'N/A'}
                    </MetricValue>
                    {workflow.executionCount > 0 && (
                      <ProgressBar>
                        <Progress 
                          $value={Math.round(((workflow.executionCount - workflow.errorCount) / workflow.executionCount) * 100)}
                          $color={workflow.theme?.colors.success.main}
                        />
                      </ProgressBar>
                    )}
                  </Metric>
                </MetricGrid>
              </StatusCard>
            ))}
          </StatusGrid>
        </>
      )}
    </DashboardContainer>
  );
};

export default StatusDashboard;