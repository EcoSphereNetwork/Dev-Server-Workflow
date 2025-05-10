/**
 * DashboardOverview Component
 * 
 * A component for displaying an overview of the system status and key metrics
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Card, Badge, Spinner, Button } from '../../design-system';
// Import the ServicesContext if it exists, otherwise use a mock
let useServices: () => { refreshServices: () => void };
try {
  useServices = require('../../context/ServicesContext').useServices;
} catch (error) {
  // Mock implementation if the context doesn't exist
  useServices = () => ({
    refreshServices: () => console.log('Mock refreshServices called'),
    services: [],
    loading: false,
    error: null,
    getServiceById: async () => ({}),
    getServiceLogs: async () => ([]),
    startService: async () => ({}),
    stopService: async () => ({}),
    restartService: async () => ({}),
    updateService: async () => ({}),
    deleteService: async () => {},
  });
}

// Types for dashboard data
interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  uptime: string;
  lastUpdated: Date;
}

interface ServiceMetric {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'error';
  count: number;
}

interface WorkflowMetric {
  total: number;
  active: number;
  executions: {
    today: number;
    week: number;
    month: number;
  };
  success: number;
  error: number;
}

interface AlertItem {
  id: string;
  type: 'info' | 'warning' | 'error';
  message: string;
  timestamp: Date;
  source: string;
  acknowledged: boolean;
}

// Styled components
const OverviewContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
`;

const OverviewHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const OverviewTitle = styled.h2`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.xl};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const LastUpdated = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.md};
`;

const MetricCard = styled(Card)`
  padding: ${props => props.theme.spacing.md};
`;

const MetricHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const MetricTitle = styled.h3`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const MetricContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const MetricRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const MetricLabel = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
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

const ServiceList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
`;

const ServiceItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  background-color: ${props => props.theme.colors.background.default};
`;

const ServiceName = styled.div`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const ServiceCount = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
  margin-left: ${props => props.theme.spacing.sm};
`;

const ServiceStatus = styled(Badge)<{ $status: string }>`
  text-transform: capitalize;
`;

const AlertsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
  max-height: 300px;
  overflow-y: auto;
`;

const AlertItem = styled.div<{ $type: string; $acknowledged: boolean }>`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  background-color: ${props => {
    if (props.$acknowledged) return props.theme.colors.background.default;
    switch (props.$type) {
      case 'error':
        return props.theme.colors.error + '10';
      case 'warning':
        return props.theme.colors.warning.main + '10';
      case 'info':
        return props.theme.colors.info + '10';
      default:
        return props.theme.colors.background.default;
    }
  }};
  border-left: 3px solid ${props => {
    switch (props.$type) {
      case 'error':
        return props.theme.colors.error;
      case 'warning':
        return props.theme.colors.warning.main;
      case 'info':
        return props.theme.colors.info;
      default:
        return props.theme.colors.divider;
    }
  }};
  opacity: ${props => props.$acknowledged ? 0.7 : 1};
`;

const AlertContent = styled.div`
  flex: 1;
`;

const AlertMessage = styled.div`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const AlertMeta = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.text.secondary};
  margin-top: ${props => props.theme.spacing.xs};
`;

const AlertActions = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.xs};
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.theme.spacing.xl};
`;

const StatCard = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.md};
  background-color: ${props => props.theme.colors.background.default};
  border-radius: ${props => props.theme.borderRadius.md};
  text-align: center;
`;

const StatValue = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xl};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
  color: ${props => props.theme.colors.primary};
`;

const StatLabel = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
  margin-top: ${props => props.theme.spacing.xs};
`;

// Mock API function to fetch system metrics
const fetchSystemMetrics = async (): Promise<SystemMetrics> => {
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

// Mock API function to fetch service metrics
const fetchServiceMetrics = async (): Promise<ServiceMetric[]> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 700));
  
  // Mock data
  return [
    {
      id: 'docker',
      name: 'Docker Containers',
      status: 'running',
      count: 12
    },
    {
      id: 'n8n',
      name: 'n8n Workflows',
      status: 'running',
      count: 8
    },
    {
      id: 'mcp',
      name: 'MCP Servers',
      status: 'running',
      count: 5
    },
    {
      id: 'monitoring',
      name: 'Monitoring Services',
      status: 'running',
      count: 2
    }
  ];
};

// Mock API function to fetch workflow metrics
const fetchWorkflowMetrics = async (): Promise<WorkflowMetric> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // Mock data
  return {
    total: 15,
    active: 8,
    executions: {
      today: 42,
      week: 187,
      month: 843
    },
    success: 792,
    error: 51
  };
};

// Mock API function to fetch alerts
const fetchAlerts = async (): Promise<AlertItem[]> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Mock data
  return [
    {
      id: 'alert-1',
      type: 'error',
      message: 'LLM Cost Analyzer MCP server is not responding',
      timestamp: new Date(Date.now() - 1800000),
      source: 'MCP Hub',
      acknowledged: false
    },
    {
      id: 'alert-2',
      type: 'warning',
      message: 'High CPU usage detected (75%)',
      timestamp: new Date(Date.now() - 3600000),
      source: 'System Monitor',
      acknowledged: false
    },
    {
      id: 'alert-3',
      type: 'info',
      message: 'n8n workflow "GitHub to OpenProject" executed successfully',
      timestamp: new Date(Date.now() - 7200000),
      source: 'n8n MCP',
      acknowledged: true
    },
    {
      id: 'alert-4',
      type: 'warning',
      message: 'Disk usage approaching threshold (70%)',
      timestamp: new Date(Date.now() - 86400000),
      source: 'System Monitor',
      acknowledged: true
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

// DashboardOverview component
export const DashboardOverview: React.FC = () => {
  // State
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [serviceMetrics, setServiceMetrics] = useState<ServiceMetric[]>([]);
  const [workflowMetrics, setWorkflowMetrics] = useState<WorkflowMetric | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  
  // Services context
  const { refreshServices } = useServices();
  
  // Load dashboard data
  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      try {
        const [system, services, workflows, alertsData] = await Promise.all([
          fetchSystemMetrics(),
          fetchServiceMetrics(),
          fetchWorkflowMetrics(),
          fetchAlerts()
        ]);
        
        setSystemMetrics(system);
        setServiceMetrics(services);
        setWorkflowMetrics(workflows);
        setAlerts(alertsData);
        setLastUpdated(new Date());
        
        // Refresh services in the global context
        refreshServices();
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadDashboardData();
    
    // Set up refresh interval
    const intervalId = setInterval(async () => {
      try {
        const [system, services, workflows, alertsData] = await Promise.all([
          fetchSystemMetrics(),
          fetchServiceMetrics(),
          fetchWorkflowMetrics(),
          fetchAlerts()
        ]);
        
        setSystemMetrics(system);
        setServiceMetrics(services);
        setWorkflowMetrics(workflows);
        setAlerts(alertsData);
        setLastUpdated(new Date());
        
        // Refresh services in the global context
        refreshServices();
      } catch (error) {
        console.error('Error updating dashboard data:', error);
      }
    }, 30000); // Update every 30 seconds
    
    // Cleanup
    return () => {
      clearInterval(intervalId);
    };
  }, [refreshServices]);
  
  // Handle alert acknowledgement
  const handleAcknowledgeAlert = (alertId: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, acknowledged: true } : alert
    ));
  };
  
  // Get status color
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'running':
        return 'success';
      case 'stopped':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'primary';
    }
  };
  
  // Calculate success rate
  const calculateSuccessRate = (): number => {
    if (!workflowMetrics) return 0;
    const total = workflowMetrics.success + workflowMetrics.error;
    return total > 0 ? Math.round((workflowMetrics.success / total) * 100) : 0;
  };
  
  return (
    <OverviewContainer>
      <OverviewHeader>
        <OverviewTitle>Dashboard Overview</OverviewTitle>
        {lastUpdated && (
          <LastUpdated>
            Last updated: {formatRelativeTime(lastUpdated)}
          </LastUpdated>
        )}
      </OverviewHeader>
      
      {loading ? (
        <LoadingContainer>
          <Spinner size="lg" />
        </LoadingContainer>
      ) : (
        <>
          <MetricsGrid>
            {/* System Resources */}
            {systemMetrics && (
              <MetricCard>
                <MetricHeader>
                  <MetricTitle>System Resources</MetricTitle>
                </MetricHeader>
                
                <MetricContent>
                  <div>
                    <MetricRow>
                      <MetricLabel>CPU Usage</MetricLabel>
                      <MetricValue>{systemMetrics.cpu}%</MetricValue>
                    </MetricRow>
                    <ProgressBar>
                      <Progress $value={systemMetrics.cpu} />
                    </ProgressBar>
                  </div>
                  
                  <div>
                    <MetricRow>
                      <MetricLabel>Memory Usage</MetricLabel>
                      <MetricValue>{systemMetrics.memory}%</MetricValue>
                    </MetricRow>
                    <ProgressBar>
                      <Progress $value={systemMetrics.memory} />
                    </ProgressBar>
                  </div>
                  
                  <div>
                    <MetricRow>
                      <MetricLabel>Disk Usage</MetricLabel>
                      <MetricValue>{systemMetrics.disk}%</MetricValue>
                    </MetricRow>
                    <ProgressBar>
                      <Progress $value={systemMetrics.disk} />
                    </ProgressBar>
                  </div>
                  
                  <MetricRow>
                    <MetricLabel>System Uptime</MetricLabel>
                    <MetricValue>{systemMetrics.uptime}</MetricValue>
                  </MetricRow>
                </MetricContent>
              </MetricCard>
            )}
            
            {/* Services Status */}
            <MetricCard>
              <MetricHeader>
                <MetricTitle>Services Status</MetricTitle>
              </MetricHeader>
              
              <ServiceList>
                {serviceMetrics.map(service => (
                  <ServiceItem key={service.id}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <ServiceName>{service.name}</ServiceName>
                      <ServiceCount>({service.count})</ServiceCount>
                    </div>
                    <ServiceStatus 
                      color={getStatusColor(service.status)}
                      $status={service.status}
                    >
                      {service.status}
                    </ServiceStatus>
                  </ServiceItem>
                ))}
              </ServiceList>
            </MetricCard>
            
            {/* Workflow Stats */}
            {workflowMetrics && (
              <MetricCard>
                <MetricHeader>
                  <MetricTitle>Workflow Statistics</MetricTitle>
                </MetricHeader>
                
                <MetricContent>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                    <StatCard>
                      <StatValue>{workflowMetrics.total}</StatValue>
                      <StatLabel>Total Workflows</StatLabel>
                    </StatCard>
                    
                    <StatCard>
                      <StatValue>{workflowMetrics.active}</StatValue>
                      <StatLabel>Active Workflows</StatLabel>
                    </StatCard>
                    
                    <StatCard>
                      <StatValue>{workflowMetrics.executions.today}</StatValue>
                      <StatLabel>Executions Today</StatLabel>
                    </StatCard>
                    
                    <StatCard>
                      <StatValue>{calculateSuccessRate()}%</StatValue>
                      <StatLabel>Success Rate</StatLabel>
                    </StatCard>
                  </div>
                  
                  <div>
                    <MetricRow>
                      <MetricLabel>Success / Error</MetricLabel>
                      <MetricValue>{workflowMetrics.success} / {workflowMetrics.error}</MetricValue>
                    </MetricRow>
                    <ProgressBar>
                      <Progress 
                        $value={calculateSuccessRate()} 
                        $color={workflowMetrics.theme?.colors.success.main}
                      />
                    </ProgressBar>
                  </div>
                </MetricContent>
              </MetricCard>
            )}
            
            {/* Recent Alerts */}
            <MetricCard>
              <MetricHeader>
                <MetricTitle>Recent Alerts</MetricTitle>
                <Button
                  variant="text"
                  size="sm"
                >
                  View All
                </Button>
              </MetricHeader>
              
              {alerts.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
                  No alerts to display
                </div>
              ) : (
                <AlertsList>
                  {alerts.map(alert => (
                    <AlertItem 
                      key={alert.id} 
                      $type={alert.type}
                      $acknowledged={alert.acknowledged}
                    >
                      <AlertContent>
                        <AlertMessage>{alert.message}</AlertMessage>
                        <AlertMeta>
                          <div>{alert.source}</div>
                          <div>{formatRelativeTime(alert.timestamp)}</div>
                        </AlertMeta>
                      </AlertContent>
                      
                      {!alert.acknowledged && (
                        <AlertActions>
                          <Button
                            variant="text"
                            size="sm"
                            onClick={() => handleAcknowledgeAlert(alert.id)}
                          >
                            Acknowledge
                          </Button>
                        </AlertActions>
                      )}
                    </AlertItem>
                  ))}
                </AlertsList>
              )}
            </MetricCard>
          </MetricsGrid>
        </>
      )}
    </OverviewContainer>
  );
};

export default DashboardOverview;