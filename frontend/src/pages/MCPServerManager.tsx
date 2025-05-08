// src/pages/MCPServerManager.tsx
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { colors } from '../theme';

// Typen für MCP-Server
interface MCPServer {
  id: string;
  name: string;
  type: 'n8n' | 'docker' | 'prompt' | 'llm' | 'other';
  status: 'running' | 'stopped' | 'error';
  port: number;
  host: string;
  description: string;
  tools: MCPTool[];
  createdAt: string;
  updatedAt: string;
}

interface MCPTool {
  id: string;
  name: string;
  description: string;
  schema: any;
}

// Dummy-Daten für MCP-Server
const dummyServers: MCPServer[] = [
  {
    id: 'mcp-server-1',
    name: 'n8n MCP Server',
    type: 'n8n',
    status: 'running',
    port: 3000,
    host: 'localhost',
    description: 'MCP-Server für n8n-Workflows',
    tools: [
      {
        id: 'tool-1',
        name: 'workflow_github_issue',
        description: 'Erstellt ein GitHub-Issue',
        schema: {}
      },
      {
        id: 'tool-2',
        name: 'workflow_gitlab_issue',
        description: 'Erstellt ein GitLab-Issue',
        schema: {}
      }
    ],
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2023-01-02T00:00:00Z'
  },
  {
    id: 'mcp-server-2',
    name: 'Docker MCP Server',
    type: 'docker',
    status: 'running',
    port: 3001,
    host: 'localhost',
    description: 'MCP-Server für Docker-Container',
    tools: [
      {
        id: 'tool-3',
        name: 'docker_start',
        description: 'Startet einen Docker-Container',
        schema: {}
      },
      {
        id: 'tool-4',
        name: 'docker_stop',
        description: 'Stoppt einen Docker-Container',
        schema: {}
      }
    ],
    createdAt: '2023-01-03T00:00:00Z',
    updatedAt: '2023-01-04T00:00:00Z'
  },
  {
    id: 'mcp-server-3',
    name: 'Prompt MCP Server',
    type: 'prompt',
    status: 'stopped',
    port: 3002,
    host: 'localhost',
    description: 'MCP-Server für Prompt-Engineering',
    tools: [
      {
        id: 'tool-5',
        name: 'prompt_generate',
        description: 'Generiert einen Prompt',
        schema: {}
      }
    ],
    createdAt: '2023-01-05T00:00:00Z',
    updatedAt: '2023-01-06T00:00:00Z'
  },
  {
    id: 'mcp-server-4',
    name: 'LLM MCP Server',
    type: 'llm',
    status: 'error',
    port: 3003,
    host: 'localhost',
    description: 'MCP-Server für LLM-Integration',
    tools: [
      {
        id: 'tool-6',
        name: 'llm_generate',
        description: 'Generiert Text mit einem LLM',
        schema: {}
      }
    ],
    createdAt: '2023-01-07T00:00:00Z',
    updatedAt: '2023-01-08T00:00:00Z'
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

const ServerGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const ServerCard = styled(Card)<{ $status: 'running' | 'stopped' | 'error' }>`
  padding: 20px;
  border-top: 4px solid ${props => {
    switch (props.$status) {
      case 'running': return colors.success.main;
      case 'stopped': return colors.warning.main;
      case 'error': return colors.error.main;
      default: return colors.divider;
    }
  }};
`;

const ServerHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
`;

const ServerName = styled.h2`
  font-size: 1.25rem;
  margin: 0;
`;

const ServerType = styled.span`
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 12px;
  background-color: ${colors.primary.light};
  color: ${colors.primary.main};
`;

const ServerDescription = styled.p`
  color: ${colors.text.secondary};
  margin-bottom: 15px;
`;

const ServerStatus = styled.div<{ $status: 'running' | 'stopped' | 'error' }>`
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  margin-bottom: 15px;
  color: ${props => {
    switch (props.$status) {
      case 'running': return colors.success.main;
      case 'stopped': return colors.warning.main;
      case 'error': return colors.error.main;
      default: return colors.text.secondary;
    }
  }};
`;

const ServerDetails = styled.div`
  margin-bottom: 15px;
  font-size: 0.875rem;
`;

const ServerDetailItem = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  padding-bottom: 5px;
  border-bottom: 1px dashed ${colors.divider};
  
  &:last-child {
    border-bottom: none;
  }
`;

const ServerDetailLabel = styled.span`
  color: ${colors.text.secondary};
`;

const ServerDetailValue = styled.span`
  font-weight: 500;
`;

const ServerActions = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 15px;
`;

const ToolsList = styled.div`
  margin-top: 20px;
`;

const ToolItem = styled.div`
  padding: 10px;
  border: 1px solid ${colors.divider};
  border-radius: 4px;
  margin-bottom: 10px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const ToolHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ToolName = styled.h3`
  font-size: 1rem;
  margin: 0;
`;

const ToolDescription = styled.p`
  font-size: 0.875rem;
  color: ${colors.text.secondary};
  margin: 5px 0 0;
`;

const LogsContainer = styled.div`
  background-color: #1e1e1e;
  color: #f8f8f8;
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  height: 400px;
  overflow-y: auto;
`;

const LogEntry = styled.div`
  margin-bottom: 5px;
  line-height: 1.5;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const LogTimestamp = styled.span`
  color: #6a9955;
  margin-right: 10px;
`;

const LogLevel = styled.span<{ $level: 'info' | 'warning' | 'error' | 'debug' }>`
  color: ${props => {
    switch (props.$level) {
      case 'info': return '#569cd6';
      case 'warning': return '#dcdcaa';
      case 'error': return '#f44747';
      case 'debug': return '#b5cea8';
      default: return '#f8f8f8';
    }
  }};
  margin-right: 10px;
`;

const LogMessage = styled.span``;

const ConfigContainer = styled.div`
  background-color: ${colors.background.default};
  padding: 15px;
  border-radius: 4px;
`;

const ConfigForm = styled.form`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
`;

const Label = styled.label`
  font-size: 0.875rem;
  margin-bottom: 5px;
  color: ${colors.text.secondary};
`;

const Input = styled.input`
  padding: 8px 12px;
  border: 1px solid ${colors.divider};
  border-radius: 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: ${colors.primary.main};
    box-shadow: 0 0 0 2px ${colors.primary.light}40;
  }
`;

const Select = styled.select`
  padding: 8px 12px;
  border: 1px solid ${colors.divider};
  border-radius: 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: ${colors.primary.main};
    box-shadow: 0 0 0 2px ${colors.primary.light}40;
  }
`;

const Textarea = styled.textarea`
  padding: 8px 12px;
  border: 1px solid ${colors.divider};
  border-radius: 4px;
  font-size: 1rem;
  min-height: 100px;
  
  &:focus {
    outline: none;
    border-color: ${colors.primary.main};
    box-shadow: 0 0 0 2px ${colors.primary.light}40;
  }
`;

const FormActions = styled.div`
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 15px;
`;

// Dummy-Logs für die Logs-Ansicht
const dummyLogs = [
  { timestamp: '2023-01-01T12:00:00Z', level: 'info', message: 'Server gestartet auf Port 3000' },
  { timestamp: '2023-01-01T12:01:00Z', level: 'info', message: 'Verbindung zu n8n hergestellt' },
  { timestamp: '2023-01-01T12:02:00Z', level: 'info', message: 'Workflows geladen: 5' },
  { timestamp: '2023-01-01T12:03:00Z', level: 'warning', message: 'Workflow "test" hat keine MCP-Tags' },
  { timestamp: '2023-01-01T12:04:00Z', level: 'error', message: 'Fehler beim Laden des Workflows "broken"' },
  { timestamp: '2023-01-01T12:05:00Z', level: 'debug', message: 'Parameter-Schema für Workflow "github" generiert' },
  { timestamp: '2023-01-01T12:06:00Z', level: 'info', message: 'Anfrage empfangen: mcp.listTools' },
  { timestamp: '2023-01-01T12:07:00Z', level: 'info', message: 'Antwort gesendet: 5 Tools' },
  { timestamp: '2023-01-01T12:08:00Z', level: 'info', message: 'Anfrage empfangen: mcp.callTool' },
  { timestamp: '2023-01-01T12:09:00Z', level: 'info', message: 'Tool aufgerufen: workflow_github_issue' },
  { timestamp: '2023-01-01T12:10:00Z', level: 'info', message: 'Workflow ausgeführt: github_issue' },
  { timestamp: '2023-01-01T12:11:00Z', level: 'info', message: 'Antwort gesendet: Erfolg' }
];

const MCPServerManager: React.FC = () => {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [selectedServer, setSelectedServer] = useState<MCPServer | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'logs' | 'config' | 'tools'>('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    // Simuliere einen API-Aufruf mit den Dummy-Daten
    const fetchServers = async () => {
      try {
        setLoading(true);
        // Simuliere eine Verzögerung
        await new Promise(resolve => setTimeout(resolve, 500));
        setServers(dummyServers);
        setSelectedServer(dummyServers[0]);
      } catch (err: any) {
        setError('Fehler beim Laden der MCP-Server');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchServers();
  }, []);
  
  const handleStartServer = (server: MCPServer) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Starte Server: ${server.name}`);
    
    // Simuliere das Starten des Servers
    const updatedServers = servers.map(s => 
      s.id === server.id ? { ...s, status: 'running' as const } : s
    );
    setServers(updatedServers);
    
    // Aktualisiere den ausgewählten Server, falls er der gestartete Server ist
    if (selectedServer && selectedServer.id === server.id) {
      setSelectedServer({ ...selectedServer, status: 'running' });
    }
  };
  
  const handleStopServer = (server: MCPServer) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Stoppe Server: ${server.name}`);
    
    // Simuliere das Stoppen des Servers
    const updatedServers = servers.map(s => 
      s.id === server.id ? { ...s, status: 'stopped' as const } : s
    );
    setServers(updatedServers);
    
    // Aktualisiere den ausgewählten Server, falls er der gestoppte Server ist
    if (selectedServer && selectedServer.id === server.id) {
      setSelectedServer({ ...selectedServer, status: 'stopped' });
    }
  };
  
  const handleRestartServer = (server: MCPServer) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Starte Server neu: ${server.name}`);
    
    // Simuliere das Neustarten des Servers
    const updatedServers = servers.map(s => 
      s.id === server.id ? { ...s, status: 'running' as const } : s
    );
    setServers(updatedServers);
    
    // Aktualisiere den ausgewählten Server, falls er der neugestartete Server ist
    if (selectedServer && selectedServer.id === server.id) {
      setSelectedServer({ ...selectedServer, status: 'running' });
    }
  };
  
  const handleSelectServer = (server: MCPServer) => {
    setSelectedServer(server);
    setActiveTab('overview');
  };
  
  const handleSaveConfig = (event: React.FormEvent) => {
    event.preventDefault();
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log('Konfiguration gespeichert');
  };
  
  if (loading && servers.length === 0) {
    return <div>Lade MCP-Server...</div>;
  }
  
  if (error) {
    return <div>Fehler: {error}</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>MCP-Server Verwaltung</Title>
        <Button variant="primary">Neuer MCP-Server</Button>
      </Header>
      
      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ width: '300px' }}>
          <ServerGrid style={{ gridTemplateColumns: '1fr' }}>
            {servers.map(server => (
              <ServerCard 
                key={server.id} 
                $status={server.status}
                onClick={() => handleSelectServer(server)}
                style={{ 
                  cursor: 'pointer',
                  border: selectedServer?.id === server.id ? `2px solid ${colors.primary.main}` : undefined
                }}
              >
                <ServerHeader>
                  <ServerName>{server.name}</ServerName>
                  <ServerType>{server.type}</ServerType>
                </ServerHeader>
                <ServerStatus $status={server.status}>
                  {server.status === 'running' ? '● Läuft' : server.status === 'stopped' ? '● Gestoppt' : '● Fehler'}
                </ServerStatus>
                <ServerDescription>{server.description}</ServerDescription>
                <ServerActions>
                  {server.status === 'running' ? (
                    <Button 
                      variant="outlined" 
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleStopServer(server);
                      }}
                    >
                      Stoppen
                    </Button>
                  ) : (
                    <Button 
                      variant="primary" 
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleStartServer(server);
                      }}
                    >
                      Starten
                    </Button>
                  )}
                  <Button 
                    variant="outlined" 
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRestartServer(server);
                    }}
                  >
                    Neustart
                  </Button>
                </ServerActions>
              </ServerCard>
            ))}
          </ServerGrid>
        </div>
        
        <div style={{ flex: 1 }}>
          {selectedServer ? (
            <>
              <TabsContainer>
                <TabList>
                  <Tab 
                    $active={activeTab === 'overview'} 
                    onClick={() => setActiveTab('overview')}
                  >
                    Übersicht
                  </Tab>
                  <Tab 
                    $active={activeTab === 'logs'} 
                    onClick={() => setActiveTab('logs')}
                  >
                    Logs
                  </Tab>
                  <Tab 
                    $active={activeTab === 'config'} 
                    onClick={() => setActiveTab('config')}
                  >
                    Konfiguration
                  </Tab>
                  <Tab 
                    $active={activeTab === 'tools'} 
                    onClick={() => setActiveTab('tools')}
                  >
                    Tools
                  </Tab>
                </TabList>
                
                <TabPanel $active={activeTab === 'overview'}>
                  <Card>
                    <ServerHeader>
                      <div>
                        <ServerName>{selectedServer.name}</ServerName>
                        <ServerDescription>{selectedServer.description}</ServerDescription>
                      </div>
                      <ServerType>{selectedServer.type}</ServerType>
                    </ServerHeader>
                    
                    <ServerStatus $status={selectedServer.status}>
                      {selectedServer.status === 'running' ? '● Läuft' : selectedServer.status === 'stopped' ? '● Gestoppt' : '● Fehler'}
                    </ServerStatus>
                    
                    <ServerDetails>
                      <ServerDetailItem>
                        <ServerDetailLabel>Host:</ServerDetailLabel>
                        <ServerDetailValue>{selectedServer.host}</ServerDetailValue>
                      </ServerDetailItem>
                      <ServerDetailItem>
                        <ServerDetailLabel>Port:</ServerDetailLabel>
                        <ServerDetailValue>{selectedServer.port}</ServerDetailValue>
                      </ServerDetailItem>
                      <ServerDetailItem>
                        <ServerDetailLabel>Tools:</ServerDetailLabel>
                        <ServerDetailValue>{selectedServer.tools.length}</ServerDetailValue>
                      </ServerDetailItem>
                      <ServerDetailItem>
                        <ServerDetailLabel>Erstellt:</ServerDetailLabel>
                        <ServerDetailValue>{new Date(selectedServer.createdAt).toLocaleString()}</ServerDetailValue>
                      </ServerDetailItem>
                      <ServerDetailItem>
                        <ServerDetailLabel>Aktualisiert:</ServerDetailLabel>
                        <ServerDetailValue>{new Date(selectedServer.updatedAt).toLocaleString()}</ServerDetailValue>
                      </ServerDetailItem>
                    </ServerDetails>
                    
                    <ServerActions>
                      {selectedServer.status === 'running' ? (
                        <Button 
                          variant="outlined" 
                          onClick={() => handleStopServer(selectedServer)}
                        >
                          Stoppen
                        </Button>
                      ) : (
                        <Button 
                          variant="primary" 
                          onClick={() => handleStartServer(selectedServer)}
                        >
                          Starten
                        </Button>
                      )}
                      <Button 
                        variant="outlined" 
                        onClick={() => handleRestartServer(selectedServer)}
                      >
                        Neustart
                      </Button>
                      <Button variant="outlined">Bearbeiten</Button>
                      <Button variant="outlined" color="error">Löschen</Button>
                    </ServerActions>
                  </Card>
                </TabPanel>
                
                <TabPanel $active={activeTab === 'logs'}>
                  <Card>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
                      <h2 style={{ margin: 0 }}>Logs</h2>
                      <Button variant="outlined" size="small">Aktualisieren</Button>
                    </div>
                    
                    <LogsContainer>
                      {dummyLogs.map((log, index) => (
                        <LogEntry key={index}>
                          <LogTimestamp>{new Date(log.timestamp).toLocaleString()}</LogTimestamp>
                          <LogLevel $level={log.level as any}>[{log.level.toUpperCase()}]</LogLevel>
                          <LogMessage>{log.message}</LogMessage>
                        </LogEntry>
                      ))}
                    </LogsContainer>
                  </Card>
                </TabPanel>
                
                <TabPanel $active={activeTab === 'config'}>
                  <Card>
                    <h2 style={{ margin: '0 0 15px' }}>Konfiguration</h2>
                    
                    <ConfigContainer>
                      <ConfigForm onSubmit={handleSaveConfig}>
                        <FormGroup>
                          <Label htmlFor="name">Name</Label>
                          <Input 
                            id="name" 
                            type="text" 
                            defaultValue={selectedServer.name} 
                          />
                        </FormGroup>
                        
                        <FormGroup>
                          <Label htmlFor="type">Typ</Label>
                          <Select id="type" defaultValue={selectedServer.type}>
                            <option value="n8n">n8n</option>
                            <option value="docker">Docker</option>
                            <option value="prompt">Prompt</option>
                            <option value="llm">LLM</option>
                            <option value="other">Andere</option>
                          </Select>
                        </FormGroup>
                        
                        <FormGroup>
                          <Label htmlFor="host">Host</Label>
                          <Input 
                            id="host" 
                            type="text" 
                            defaultValue={selectedServer.host} 
                          />
                        </FormGroup>
                        
                        <FormGroup>
                          <Label htmlFor="port">Port</Label>
                          <Input 
                            id="port" 
                            type="number" 
                            defaultValue={selectedServer.port} 
                          />
                        </FormGroup>
                        
                        <FormGroup style={{ gridColumn: '1 / -1' }}>
                          <Label htmlFor="description">Beschreibung</Label>
                          <Textarea 
                            id="description" 
                            defaultValue={selectedServer.description} 
                          />
                        </FormGroup>
                        
                        <FormActions>
                          <Button variant="outlined" type="button">Abbrechen</Button>
                          <Button variant="primary" type="submit">Speichern</Button>
                        </FormActions>
                      </ConfigForm>
                    </ConfigContainer>
                  </Card>
                </TabPanel>
                
                <TabPanel $active={activeTab === 'tools'}>
                  <Card>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
                      <h2 style={{ margin: 0 }}>Tools</h2>
                      <Button variant="outlined" size="small">Aktualisieren</Button>
                    </div>
                    
                    <ToolsList>
                      {selectedServer.tools.map(tool => (
                        <ToolItem key={tool.id}>
                          <ToolHeader>
                            <ToolName>{tool.name}</ToolName>
                            <Button variant="outlined" size="small">Details</Button>
                          </ToolHeader>
                          <ToolDescription>{tool.description}</ToolDescription>
                        </ToolItem>
                      ))}
                    </ToolsList>
                  </Card>
                </TabPanel>
              </TabsContainer>
            </>
          ) : (
            <Card>
              <div style={{ padding: '40px', textAlign: 'center' }}>
                <h2>Kein MCP-Server ausgewählt</h2>
                <p>Bitte wählen Sie einen MCP-Server aus der Liste aus.</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </Container>
  );
};

export default MCPServerManager;