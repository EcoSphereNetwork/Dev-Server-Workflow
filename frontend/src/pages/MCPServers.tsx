// src/pages/MCPServers.tsx
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { 
  Button, 
  Card, 
  Table, 
  Modal, 
  Input, 
  Select, 
  Spinner, 
  Alert,
  Tabs,
  TabView,
  Badge
} from '../components/SmolituxComponents';
import apiClient from '../api/client';
import { colors } from '../theme';

// Typen für die MCP-Server-Daten
interface MCPServer {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'offline' | 'error';
  url: string;
  version: string;
  lastSeen: string;
  tools: number;
}

const MCPServersContainer = styled.div`
  padding: 20px;
`;

const MCPServersHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const MCPServersTitle = styled.h1`
  font-size: 1.5rem;
  margin: 0;
`;

const MCPServersActions = styled.div`
  display: flex;
  gap: 10px;
`;

const StatusBadge = styled(Badge)<{ $status: 'online' | 'offline' | 'error' }>`
  background-color: ${props => {
    switch (props.$status) {
      case 'online':
        return colors.success.main;
      case 'offline':
        return colors.error.main;
      case 'error':
        return colors.warning.main;
      default:
        return colors.info.main;
    }
  }};
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
`;

const MCPServers: React.FC = () => {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newServer, setNewServer] = useState({
    name: '',
    type: 'docker',
    url: '',
  });

  useEffect(() => {
    const fetchServers = async () => {
      try {
        setLoading(true);
        // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
        // const response = await apiClient.get('/mcp-servers');
        // setServers(response.data);
        
        // Simulierte Daten für die Entwicklung
        setServers([
          {
            id: '1',
            name: 'Docker MCP',
            type: 'docker',
            status: 'online',
            url: 'http://localhost:3334',
            version: '1.0.0',
            lastSeen: '2025-05-08T14:30:00Z',
            tools: 12
          },
          {
            id: '2',
            name: 'n8n MCP',
            type: 'n8n',
            status: 'online',
            url: 'http://localhost:3335',
            version: '0.9.0',
            lastSeen: '2025-05-08T14:25:00Z',
            tools: 8
          },
          {
            id: '3',
            name: 'AWS MCP',
            type: 'aws',
            status: 'offline',
            url: 'http://localhost:3336',
            version: '0.8.5',
            lastSeen: '2025-05-07T18:45:00Z',
            tools: 15
          },
          {
            id: '4',
            name: 'Firebase MCP',
            type: 'firebase',
            status: 'error',
            url: 'http://localhost:3337',
            version: '0.7.2',
            lastSeen: '2025-05-08T10:15:00Z',
            tools: 6
          }
        ]);
      } catch (err: any) {
        setError('Fehler beim Laden der MCP-Server');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchServers();
  }, []);

  const handleAddServer = async () => {
    try {
      // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
      // const response = await apiClient.post('/mcp-servers', newServer);
      // setServers([...servers, response.data]);
      
      // Simulierte Daten für die Entwicklung
      const newId = (servers.length + 1).toString();
      setServers([...servers, {
        id: newId,
        name: newServer.name,
        type: newServer.type,
        status: 'offline',
        url: newServer.url,
        version: '0.0.0',
        lastSeen: new Date().toISOString(),
        tools: 0
      }]);
      
      setShowAddModal(false);
      setNewServer({
        name: '',
        type: 'docker',
        url: '',
      });
    } catch (err: any) {
      setError('Fehler beim Hinzufügen des MCP-Servers');
      console.error(err);
    }
  };

  const handleDeleteServer = async (id: string) => {
    try {
      // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
      // await apiClient.delete(`/mcp-servers/${id}`);
      
      // Simulierte Daten für die Entwicklung
      setServers(servers.filter(server => server.id !== id));
    } catch (err: any) {
      setError('Fehler beim Löschen des MCP-Servers');
      console.error(err);
    }
  };

  const handleStartServer = async (id: string) => {
    try {
      // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
      // await apiClient.post(`/mcp-servers/${id}/start`);
      
      // Simulierte Daten für die Entwicklung
      setServers(servers.map(server => 
        server.id === id ? { ...server, status: 'online' } : server
      ));
    } catch (err: any) {
      setError('Fehler beim Starten des MCP-Servers');
      console.error(err);
    }
  };

  const handleStopServer = async (id: string) => {
    try {
      // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
      // await apiClient.post(`/mcp-servers/${id}/stop`);
      
      // Simulierte Daten für die Entwicklung
      setServers(servers.map(server => 
        server.id === id ? { ...server, status: 'offline' } : server
      ));
    } catch (err: any) {
      setError('Fehler beim Stoppen des MCP-Servers');
      console.error(err);
    }
  };

  if (loading && !servers.length) {
    return (
      <MCPServersContainer>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>
          <Spinner />
        </div>
      </MCPServersContainer>
    );
  }

  return (
    <MCPServersContainer>
      <MCPServersHeader>
        <MCPServersTitle>MCP-Server</MCPServersTitle>
        <MCPServersActions>
          <Button variant="primary" onClick={() => setShowAddModal(true)}>
            Neuer MCP-Server
          </Button>
        </MCPServersActions>
      </MCPServersHeader>

      {error && (
        <Alert variant="error" style={{ marginBottom: '20px' }}>
          {error}
        </Alert>
      )}

      <Card>
        <Table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Typ</th>
              <th>Status</th>
              <th>URL</th>
              <th>Version</th>
              <th>Zuletzt gesehen</th>
              <th>Tools</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {servers.map((server) => (
              <tr key={server.id}>
                <td>{server.name}</td>
                <td>{server.type}</td>
                <td>
                  <StatusBadge $status={server.status}>
                    {server.status === 'online' ? 'Online' : 
                     server.status === 'offline' ? 'Offline' : 'Fehler'}
                  </StatusBadge>
                </td>
                <td>{server.url}</td>
                <td>{server.version}</td>
                <td>{new Date(server.lastSeen).toLocaleString()}</td>
                <td>{server.tools}</td>
                <td>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    {server.status === 'offline' && (
                      <Button 
                        variant="success" 
                        onClick={() => handleStartServer(server.id)}
                        style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                      >
                        Start
                      </Button>
                    )}
                    {server.status === 'online' && (
                      <Button 
                        variant="warning" 
                        onClick={() => handleStopServer(server.id)}
                        style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                      >
                        Stop
                      </Button>
                    )}
                    <Button 
                      variant="error" 
                      onClick={() => handleDeleteServer(server.id)}
                      style={{ padding: '4px 8px', fontSize: '0.8rem' }}
                    >
                      Löschen
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Card>

      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Neuen MCP-Server hinzufügen"
      >
        <div style={{ padding: '20px' }}>
          <Input
            label="Name"
            value={newServer.name}
            onChange={(e) => setNewServer({ ...newServer, name: e.target.value })}
            fullWidth
            style={{ marginBottom: '15px' }}
          />
          
          <Select
            label="Typ"
            value={newServer.type}
            onChange={(e) => setNewServer({ ...newServer, type: e.target.value })}
            fullWidth
            style={{ marginBottom: '15px' }}
          >
            <option value="docker">Docker</option>
            <option value="n8n">n8n</option>
            <option value="aws">AWS</option>
            <option value="firebase">Firebase</option>
            <option value="salesforce">Salesforce</option>
          </Select>
          
          <Input
            label="URL"
            value={newServer.url}
            onChange={(e) => setNewServer({ ...newServer, url: e.target.value })}
            fullWidth
            style={{ marginBottom: '20px' }}
          />
          
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <Button variant="secondary" onClick={() => setShowAddModal(false)}>
              Abbrechen
            </Button>
            <Button 
              variant="primary" 
              onClick={handleAddServer}
              disabled={!newServer.name || !newServer.url}
            >
              Hinzufügen
            </Button>
          </div>
        </div>
      </Modal>
    </MCPServersContainer>
  );
};

export default MCPServers;