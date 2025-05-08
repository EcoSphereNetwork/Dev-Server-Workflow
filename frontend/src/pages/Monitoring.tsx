// src/pages/Monitoring.tsx
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { colors } from '../theme';

// Typen für Monitoring-Daten
interface SystemMetrics {
  cpu: {
    usage: number;
    cores: number;
    temperature: number;
  };
  memory: {
    total: number;
    used: number;
    free: number;
    usage: number;
  };
  disk: {
    total: number;
    used: number;
    free: number;
    usage: number;
  };
  network: {
    rx: number;
    tx: number;
    connections: number;
  };
  uptime: number;
}

interface ContainerMetrics {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'paused' | 'restarting' | 'created';
  cpu: number;
  memory: {
    usage: number;
    limit: number;
    percentage: number;
  };
  network: {
    rx: number;
    tx: number;
  };
  restarts: number;
  uptime: number;
}

interface Alert {
  id: string;
  level: 'info' | 'warning' | 'critical';
  message: string;
  source: string;
  timestamp: string;
  acknowledged: boolean;
}

// Dummy-Daten für Monitoring
const dummySystemMetrics: SystemMetrics = {
  cpu: {
    usage: 35,
    cores: 8,
    temperature: 45
  },
  memory: {
    total: 16384,
    used: 8192,
    free: 8192,
    usage: 50
  },
  disk: {
    total: 512000,
    used: 256000,
    free: 256000,
    usage: 50
  },
  network: {
    rx: 1024,
    tx: 512,
    connections: 42
  },
  uptime: 604800 // 7 Tage in Sekunden
};

const dummyContainerMetrics: ContainerMetrics[] = [
  {
    id: 'container-1',
    name: 'n8n',
    status: 'running',
    cpu: 5,
    memory: {
      usage: 256,
      limit: 1024,
      percentage: 25
    },
    network: {
      rx: 512,
      tx: 256
    },
    restarts: 0,
    uptime: 604800 // 7 Tage in Sekunden
  },
  {
    id: 'container-2',
    name: 'mcp-server',
    status: 'running',
    cpu: 10,
    memory: {
      usage: 512,
      limit: 1024,
      percentage: 50
    },
    network: {
      rx: 1024,
      tx: 512
    },
    restarts: 2,
    uptime: 86400 // 1 Tag in Sekunden
  },
  {
    id: 'container-3',
    name: 'postgres',
    status: 'running',
    cpu: 15,
    memory: {
      usage: 768,
      limit: 1024,
      percentage: 75
    },
    network: {
      rx: 2048,
      tx: 1024
    },
    restarts: 0,
    uptime: 604800 // 7 Tage in Sekunden
  },
  {
    id: 'container-4',
    name: 'redis',
    status: 'running',
    cpu: 2,
    memory: {
      usage: 128,
      limit: 512,
      percentage: 25
    },
    network: {
      rx: 256,
      tx: 128
    },
    restarts: 0,
    uptime: 604800 // 7 Tage in Sekunden
  },
  {
    id: 'container-5',
    name: 'nginx',
    status: 'running',
    cpu: 1,
    memory: {
      usage: 64,
      limit: 256,
      percentage: 25
    },
    network: {
      rx: 4096,
      tx: 8192
    },
    restarts: 0,
    uptime: 604800 // 7 Tage in Sekunden
  },
  {
    id: 'container-6',
    name: 'broken-service',
    status: 'restarting',
    cpu: 0,
    memory: {
      usage: 0,
      limit: 512,
      percentage: 0
    },
    network: {
      rx: 0,
      tx: 0
    },
    restarts: 5,
    uptime: 300 // 5 Minuten in Sekunden
  }
];

const dummyAlerts: Alert[] = [
  {
    id: 'alert-1',
    level: 'critical',
    message: 'Container broken-service hat 5 Neustarts in den letzten 5 Minuten',
    source: 'Docker',
    timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    acknowledged: false
  },
  {
    id: 'alert-2',
    level: 'warning',
    message: 'Hohe CPU-Auslastung (>80%) für Container postgres',
    source: 'System',
    timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    acknowledged: false
  },
  {
    id: 'alert-3',
    level: 'info',
    message: 'Container n8n wurde gestartet',
    source: 'Docker',
    timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    acknowledged: true
  },
  {
    id: 'alert-4',
    level: 'warning',
    message: 'Festplattennutzung über 80%',
    source: 'System',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    acknowledged: true
  },
  {
    id: 'alert-5',
    level: 'info',
    message: 'Backup erfolgreich abgeschlossen',
    source: 'Backup',
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    acknowledged: true
  }
];

// Styled Components
const Container = styled.div`
  padding: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const Title = styled.h1`
  font-size: 1.5rem;
  margin: 0;
`;

const TimeRangeSelector = styled.div`
  display: flex;
  gap: 10px;
`;

const TimeRangeButton = styled.button<{ $active: boolean }>`
  padding: 8px 16px;
  border: 1px solid ${props => props.$active ? colors.primary.main : colors.divider};
  border-radius: 20px;
  background-color: ${props => props.$active ? colors.primary.main : 'transparent'};
  color: ${props => props.$active ? 'white' : colors.text.primary};
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease-in-out;
  
  &:hover {
    background-color: ${props => props.$active ? colors.primary.dark : colors.background.default};
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px ${colors.primary.light}40;
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const MetricCard = styled(Card)`
  padding: 20px;
`;

const MetricTitle = styled.h2`
  font-size: 1.25rem;
  margin: 0 0 15px;
  display: flex;
  align-items: center;
`;

const MetricIcon = styled.span`
  font-size: 1.5rem;
  margin-right: 10px;
`;

const MetricValue = styled.div`
  font-size: 2.5rem;
  font-weight: 500;
  margin-bottom: 10px;
  color: ${colors.primary.main};
`;

const MetricDetails = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 15px;
`;

const MetricDetail = styled.div`
  flex: 1;
  min-width: 100px;
`;

const MetricDetailLabel = styled.div`
  font-size: 0.75rem;
  color: ${colors.text.secondary};
  margin-bottom: 5px;
`;

const MetricDetailValue = styled.div`
  font-size: 1.25rem;
  font-weight: 500;
`;

const ProgressBar = styled.div`
  height: 8px;
  background-color: ${colors.background.default};
  border-radius: 4px;
  overflow: hidden;
  margin-top: 10px;
`;

const ProgressBarFill = styled.div<{ $value: number; $color?: string }>`
  height: 100%;
  width: ${props => `${props.$value}%`};
  background-color: ${props => {
    if (props.$color) return props.$color;
    if (props.$value < 50) return colors.success.main;
    if (props.$value < 80) return colors.warning.main;
    return colors.error.main;
  }};
  transition: width 0.3s ease-in-out;
`;

const TabsContainer = styled.div`
  margin-bottom: 20px;
`;

const TabList = styled.div`
  display: flex;
  border-bottom: 1px solid ${colors.divider};
`;

const Tab = styled.button<{ $active: boolean }>`
  padding: 10px 20px;
  background-color: ${props => props.$active ? colors.primary.main : 'transparent'};
  color: ${props => props.$active ? 'white' : colors.text.primary};
  border: none;
  border-bottom: 3px solid ${props => props.$active ? colors.primary.main : 'transparent'};
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease-in-out;
  
  &:hover {
    background-color: ${props => props.$active ? colors.primary.main : colors.background.default};
  }
  
  &:focus {
    outline: none;
  }
`;

const TabPanel = styled.div<{ $active: boolean }>`
  display: ${props => props.$active ? 'block' : 'none'};
  padding: 20px 0;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHead = styled.thead`
  background-color: ${colors.background.default};
`;

const TableRow = styled.tr`
  border-bottom: 1px solid ${colors.divider};
  
  &:last-child {
    border-bottom: none;
  }
`;

const TableHeaderCell = styled.th`
  padding: 12px 16px;
  text-align: left;
  font-weight: 500;
  color: ${colors.text.secondary};
  font-size: 0.875rem;
`;

const TableCell = styled.td`
  padding: 12px 16px;
  font-size: 0.875rem;
`;

const StatusBadge = styled.span<{ $status: 'running' | 'stopped' | 'paused' | 'restarting' | 'created' }>`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  background-color: ${props => {
    switch (props.$status) {
      case 'running': return colors.success.light;
      case 'stopped': return colors.error.light;
      case 'paused': return colors.warning.light;
      case 'restarting': return colors.info.light;
      case 'created': return colors.background.default;
      default: return colors.background.default;
    }
  }};
  color: ${props => {
    switch (props.$status) {
      case 'running': return colors.success.main;
      case 'stopped': return colors.error.main;
      case 'paused': return colors.warning.main;
      case 'restarting': return colors.info.main;
      case 'created': return colors.text.secondary;
      default: return colors.text.secondary;
    }
  }};
`;

const AlertBadge = styled.span<{ $level: 'info' | 'warning' | 'critical' }>`
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  background-color: ${props => {
    switch (props.$level) {
      case 'info': return colors.info.light;
      case 'warning': return colors.warning.light;
      case 'critical': return colors.error.light;
      default: return colors.background.default;
    }
  }};
  color: ${props => {
    switch (props.$level) {
      case 'info': return colors.info.main;
      case 'warning': return colors.warning.main;
      case 'critical': return colors.error.main;
      default: return colors.text.secondary;
    }
  }};
`;

const formatBytes = (bytes: number, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

const formatUptime = (seconds: number) => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`;
  }
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  
  return `${minutes}m`;
};

const Monitoring: React.FC = () => {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [containerMetrics, setContainerMetrics] = useState<ContainerMetrics[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'containers' | 'alerts'>('overview');
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d' | '30d'>('24h');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    // Simuliere einen API-Aufruf mit den Dummy-Daten
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        // Simuliere eine Verzögerung
        await new Promise(resolve => setTimeout(resolve, 500));
        setSystemMetrics(dummySystemMetrics);
        setContainerMetrics(dummyContainerMetrics);
        setAlerts(dummyAlerts);
      } catch (err: any) {
        setError('Fehler beim Laden der Monitoring-Daten');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchMetrics();
    
    // Simuliere regelmäßige Aktualisierungen
    const interval = setInterval(() => {
      fetchMetrics();
    }, 30000); // Alle 30 Sekunden aktualisieren
    
    return () => clearInterval(interval);
  }, []);
  
  const handleAcknowledgeAlert = (alertId: string) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Bestätige Alert: ${alertId}`);
    
    // Simuliere das Bestätigen des Alerts
    const updatedAlerts = alerts.map(alert => 
      alert.id === alertId ? { ...alert, acknowledged: true } : alert
    );
    setAlerts(updatedAlerts);
  };
  
  const handleClearAlert = (alertId: string) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Lösche Alert: ${alertId}`);
    
    // Simuliere das Löschen des Alerts
    const updatedAlerts = alerts.filter(alert => alert.id !== alertId);
    setAlerts(updatedAlerts);
  };
  
  const handleRefresh = () => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log('Aktualisiere Monitoring-Daten');
    
    // Simuliere das Aktualisieren der Daten
    setLoading(true);
    setTimeout(() => {
      setSystemMetrics(dummySystemMetrics);
      setContainerMetrics(dummyContainerMetrics);
      setAlerts(dummyAlerts);
      setLoading(false);
    }, 500);
  };
  
  if (loading && !systemMetrics) {
    return <div>Lade Monitoring-Daten...</div>;
  }
  
  if (error) {
    return <div>Fehler: {error}</div>;
  }
  
  if (!systemMetrics) {
    return <div>Keine Monitoring-Daten verfügbar</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>System-Monitoring</Title>
        <div style={{ display: 'flex', gap: '10px' }}>
          <TimeRangeSelector>
            <TimeRangeButton 
              $active={timeRange === '1h'} 
              onClick={() => setTimeRange('1h')}
            >
              1h
            </TimeRangeButton>
            <TimeRangeButton 
              $active={timeRange === '6h'} 
              onClick={() => setTimeRange('6h')}
            >
              6h
            </TimeRangeButton>
            <TimeRangeButton 
              $active={timeRange === '24h'} 
              onClick={() => setTimeRange('24h')}
            >
              24h
            </TimeRangeButton>
            <TimeRangeButton 
              $active={timeRange === '7d'} 
              onClick={() => setTimeRange('7d')}
            >
              7d
            </TimeRangeButton>
            <TimeRangeButton 
              $active={timeRange === '30d'} 
              onClick={() => setTimeRange('30d')}
            >
              30d
            </TimeRangeButton>
          </TimeRangeSelector>
          <Button variant="outlined" onClick={handleRefresh}>Aktualisieren</Button>
        </div>
      </Header>
      
      <TabsContainer>
        <TabList>
          <Tab 
            $active={activeTab === 'overview'} 
            onClick={() => setActiveTab('overview')}
          >
            Übersicht
          </Tab>
          <Tab 
            $active={activeTab === 'containers'} 
            onClick={() => setActiveTab('containers')}
          >
            Container
          </Tab>
          <Tab 
            $active={activeTab === 'alerts'} 
            onClick={() => setActiveTab('alerts')}
          >
            Alerts
            {alerts.filter(alert => !alert.acknowledged).length > 0 && (
              <span style={{ 
                marginLeft: '5px', 
                background: colors.error.main, 
                color: 'white', 
                borderRadius: '50%', 
                padding: '2px 6px', 
                fontSize: '0.75rem' 
              }}>
                {alerts.filter(alert => !alert.acknowledged).length}
              </span>
            )}
          </Tab>
        </TabList>
        
        <TabPanel $active={activeTab === 'overview'}>
          <Grid>
            <MetricCard>
              <MetricTitle>
                <MetricIcon>🔄</MetricIcon>
                CPU-Auslastung
              </MetricTitle>
              <MetricValue>{systemMetrics.cpu.usage}%</MetricValue>
              <ProgressBar>
                <ProgressBarFill $value={systemMetrics.cpu.usage} />
              </ProgressBar>
              <MetricDetails>
                <MetricDetail>
                  <MetricDetailLabel>Kerne</MetricDetailLabel>
                  <MetricDetailValue>{systemMetrics.cpu.cores}</MetricDetailValue>
                </MetricDetail>
                <MetricDetail>
                  <MetricDetailLabel>Temperatur</MetricDetailLabel>
                  <MetricDetailValue>{systemMetrics.cpu.temperature}°C</MetricDetailValue>
                </MetricDetail>
              </MetricDetails>
            </MetricCard>
            
            <MetricCard>
              <MetricTitle>
                <MetricIcon>💾</MetricIcon>
                Speicher-Auslastung
              </MetricTitle>
              <MetricValue>{systemMetrics.memory.usage}%</MetricValue>
              <ProgressBar>
                <ProgressBarFill $value={systemMetrics.memory.usage} />
              </ProgressBar>
              <MetricDetails>
                <MetricDetail>
                  <MetricDetailLabel>Verwendet</MetricDetailLabel>
                  <MetricDetailValue>{formatBytes(systemMetrics.memory.used * 1024 * 1024)}</MetricDetailValue>
                </MetricDetail>
                <MetricDetail>
                  <MetricDetailLabel>Frei</MetricDetailLabel>
                  <MetricDetailValue>{formatBytes(systemMetrics.memory.free * 1024 * 1024)}</MetricDetailValue>
                </MetricDetail>
                <MetricDetail>
                  <MetricDetailLabel>Gesamt</MetricDetailLabel>
                  <MetricDetailValue>{formatBytes(systemMetrics.memory.total * 1024 * 1024)}</MetricDetailValue>
                </MetricDetail>
              </MetricDetails>
            </MetricCard>
            
            <MetricCard>
              <MetricTitle>
                <MetricIcon>💿</MetricIcon>
                Festplatten-Auslastung
              </MetricTitle>
              <MetricValue>{systemMetrics.disk.usage}%</MetricValue>
              <ProgressBar>
                <ProgressBarFill $value={systemMetrics.disk.usage} />
              </ProgressBar>
              <MetricDetails>
                <MetricDetail>
                  <MetricDetailLabel>Verwendet</MetricDetailLabel>
                  <MetricDetailValue>{formatBytes(systemMetrics.disk.used * 1024 * 1024)}</MetricDetailValue>
                </MetricDetail>
                <MetricDetail>
                  <MetricDetailLabel>Frei</MetricDetailLabel>
                  <MetricDetailValue>{formatBytes(systemMetrics.disk.free * 1024 * 1024)}</MetricDetailValue>
                </MetricDetail>
                <MetricDetail>
                  <MetricDetailLabel>Gesamt</MetricDetailLabel>
                  <MetricDetailValue>{formatBytes(systemMetrics.disk.total * 1024 * 1024)}</MetricDetailValue>
                </MetricDetail>
              </MetricDetails>
            </MetricCard>
            
            <MetricCard>
              <MetricTitle>
                <MetricIcon>🌐</MetricIcon>
                Netzwerk
              </MetricTitle>
              <MetricDetails>
                <MetricDetail>
                  <MetricDetailLabel>Empfangen</MetricDetailLabel>
                  <MetricDetailValue>{formatBytes(systemMetrics.network.rx * 1024)}/s</MetricDetailValue>
                </MetricDetail>
                <MetricDetail>
                  <MetricDetailLabel>Gesendet</MetricDetailLabel>
                  <MetricDetailValue>{formatBytes(systemMetrics.network.tx * 1024)}/s</MetricDetailValue>
                </MetricDetail>
                <MetricDetail>
                  <MetricDetailLabel>Verbindungen</MetricDetailLabel>
                  <MetricDetailValue>{systemMetrics.network.connections}</MetricDetailValue>
                </MetricDetail>
              </MetricDetails>
            </MetricCard>
            
            <MetricCard>
              <MetricTitle>
                <MetricIcon>⏱️</MetricIcon>
                Uptime
              </MetricTitle>
              <MetricValue>{formatUptime(systemMetrics.uptime)}</MetricValue>
            </MetricCard>
            
            <MetricCard>
              <MetricTitle>
                <MetricIcon>🐳</MetricIcon>
                Container
              </MetricTitle>
              <MetricDetails>
                <MetricDetail>
                  <MetricDetailLabel>Gesamt</MetricDetailLabel>
                  <MetricDetailValue>{containerMetrics.length}</MetricDetailValue>
                </MetricDetail>
                <MetricDetail>
                  <MetricDetailLabel>Laufend</MetricDetailLabel>
                  <MetricDetailValue>{containerMetrics.filter(c => c.status === 'running').length}</MetricDetailValue>
                </MetricDetail>
                <MetricDetail>
                  <MetricDetailLabel>Gestoppt</MetricDetailLabel>
                  <MetricDetailValue>{containerMetrics.filter(c => c.status === 'stopped').length}</MetricDetailValue>
                </MetricDetail>
                <MetricDetail>
                  <MetricDetailLabel>Fehler</MetricDetailLabel>
                  <MetricDetailValue>{containerMetrics.filter(c => c.status === 'restarting').length}</MetricDetailValue>
                </MetricDetail>
              </MetricDetails>
            </MetricCard>
          </Grid>
        </TabPanel>
        
        <TabPanel $active={activeTab === 'containers'}>
          <Card>
            <div style={{ padding: '0 20px 20px' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableHeaderCell>Name</TableHeaderCell>
                    <TableHeaderCell>Status</TableHeaderCell>
                    <TableHeaderCell>CPU</TableHeaderCell>
                    <TableHeaderCell>Speicher</TableHeaderCell>
                    <TableHeaderCell>Netzwerk (RX/TX)</TableHeaderCell>
                    <TableHeaderCell>Neustarts</TableHeaderCell>
                    <TableHeaderCell>Uptime</TableHeaderCell>
                    <TableHeaderCell>Aktionen</TableHeaderCell>
                  </TableRow>
                </TableHead>
                <tbody>
                  {containerMetrics.map(container => (
                    <TableRow key={container.id}>
                      <TableCell>{container.name}</TableCell>
                      <TableCell>
                        <StatusBadge $status={container.status}>
                          {container.status === 'running' ? 'Läuft' : 
                           container.status === 'stopped' ? 'Gestoppt' : 
                           container.status === 'paused' ? 'Pausiert' : 
                           container.status === 'restarting' ? 'Neustart' : 
                           'Erstellt'}
                        </StatusBadge>
                      </TableCell>
                      <TableCell>{container.cpu}%</TableCell>
                      <TableCell>
                        {formatBytes(container.memory.usage * 1024 * 1024)} / {formatBytes(container.memory.limit * 1024 * 1024)}
                        <ProgressBar>
                          <ProgressBarFill $value={container.memory.percentage} />
                        </ProgressBar>
                      </TableCell>
                      <TableCell>
                        {formatBytes(container.network.rx * 1024)}/s / {formatBytes(container.network.tx * 1024)}/s
                      </TableCell>
                      <TableCell>{container.restarts}</TableCell>
                      <TableCell>{formatUptime(container.uptime)}</TableCell>
                      <TableCell>
                        <div style={{ display: 'flex', gap: '5px' }}>
                          {container.status === 'running' ? (
                            <Button variant="outlined" size="small">Stoppen</Button>
                          ) : (
                            <Button variant="primary" size="small">Starten</Button>
                          )}
                          <Button variant="outlined" size="small">Neustart</Button>
                          <Button variant="outlined" size="small">Logs</Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </tbody>
              </Table>
            </div>
          </Card>
        </TabPanel>
        
        <TabPanel $active={activeTab === 'alerts'}>
          <Card>
            <div style={{ padding: '0 20px 20px' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableHeaderCell>Level</TableHeaderCell>
                    <TableHeaderCell>Nachricht</TableHeaderCell>
                    <TableHeaderCell>Quelle</TableHeaderCell>
                    <TableHeaderCell>Zeitpunkt</TableHeaderCell>
                    <TableHeaderCell>Status</TableHeaderCell>
                    <TableHeaderCell>Aktionen</TableHeaderCell>
                  </TableRow>
                </TableHead>
                <tbody>
                  {alerts.map(alert => (
                    <TableRow key={alert.id}>
                      <TableCell>
                        <AlertBadge $level={alert.level}>
                          {alert.level === 'info' ? 'Info' : 
                           alert.level === 'warning' ? 'Warnung' : 
                           'Kritisch'}
                        </AlertBadge>
                      </TableCell>
                      <TableCell>{alert.message}</TableCell>
                      <TableCell>{alert.source}</TableCell>
                      <TableCell>{new Date(alert.timestamp).toLocaleString()}</TableCell>
                      <TableCell>
                        {alert.acknowledged ? 'Bestätigt' : 'Neu'}
                      </TableCell>
                      <TableCell>
                        <div style={{ display: 'flex', gap: '5px' }}>
                          {!alert.acknowledged && (
                            <Button 
                              variant="outlined" 
                              size="small"
                              onClick={() => handleAcknowledgeAlert(alert.id)}
                            >
                              Bestätigen
                            </Button>
                          )}
                          <Button 
                            variant="outlined" 
                            size="small"
                            onClick={() => handleClearAlert(alert.id)}
                          >
                            Löschen
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </tbody>
              </Table>
            </div>
          </Card>
        </TabPanel>
      </TabsContainer>
    </Container>
  );
};

export default Monitoring;