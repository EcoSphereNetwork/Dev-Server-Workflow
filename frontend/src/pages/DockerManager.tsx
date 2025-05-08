// src/pages/DockerManager.tsx
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { colors } from '../theme';

// Typen für Docker-Container
interface DockerContainer {
  id: string;
  name: string;
  image: string;
  status: 'running' | 'stopped' | 'paused' | 'restarting' | 'created';
  ports: string[];
  networks: string[];
  volumes: string[];
  created: string;
  size: number;
  command: string;
}

// Typen für Docker-Images
interface DockerImage {
  id: string;
  repository: string;
  tag: string;
  size: number;
  created: string;
}

// Typen für Docker-Netzwerke
interface DockerNetwork {
  id: string;
  name: string;
  driver: string;
  scope: string;
  containers: string[];
  created: string;
}

// Typen für Docker-Volumes
interface DockerVolume {
  id: string;
  name: string;
  driver: string;
  mountpoint: string;
  created: string;
}

// Dummy-Daten für Docker-Container
const dummyContainers: DockerContainer[] = [
  {
    id: 'container-1',
    name: 'n8n',
    image: 'n8nio/n8n:latest',
    status: 'running',
    ports: ['5678:5678'],
    networks: ['dev-server-network'],
    volumes: ['n8n-data:/home/node/.n8n'],
    created: '2023-01-01T00:00:00Z',
    size: 256 * 1024 * 1024, // 256 MB
    command: 'node /home/node/packages/cli/bin/n8n.js start'
  },
  {
    id: 'container-2',
    name: 'postgres',
    image: 'postgres:13',
    status: 'running',
    ports: ['5432:5432'],
    networks: ['dev-server-network'],
    volumes: ['postgres-data:/var/lib/postgresql/data'],
    created: '2023-01-01T00:00:00Z',
    size: 512 * 1024 * 1024, // 512 MB
    command: 'postgres'
  },
  {
    id: 'container-3',
    name: 'redis',
    image: 'redis:alpine',
    status: 'running',
    ports: ['6379:6379'],
    networks: ['dev-server-network'],
    volumes: ['redis-data:/data'],
    created: '2023-01-01T00:00:00Z',
    size: 64 * 1024 * 1024, // 64 MB
    command: 'redis-server'
  },
  {
    id: 'container-4',
    name: 'nginx',
    image: 'nginx:alpine',
    status: 'running',
    ports: ['80:80', '443:443'],
    networks: ['dev-server-network'],
    volumes: ['nginx-conf:/etc/nginx/conf.d', 'nginx-ssl:/etc/nginx/ssl'],
    created: '2023-01-01T00:00:00Z',
    size: 32 * 1024 * 1024, // 32 MB
    command: 'nginx -g daemon off;'
  },
  {
    id: 'container-5',
    name: 'mcp-server',
    image: 'ecosphere/mcp-server:latest',
    status: 'running',
    ports: ['3000:3000'],
    networks: ['dev-server-network'],
    volumes: ['mcp-data:/app/data'],
    created: '2023-01-01T00:00:00Z',
    size: 128 * 1024 * 1024, // 128 MB
    command: 'node server.js'
  },
  {
    id: 'container-6',
    name: 'broken-service',
    image: 'ecosphere/broken-service:latest',
    status: 'restarting',
    ports: ['3001:3001'],
    networks: ['dev-server-network'],
    volumes: [],
    created: '2023-01-01T00:00:00Z',
    size: 64 * 1024 * 1024, // 64 MB
    command: 'node app.js'
  }
];

// Dummy-Daten für Docker-Images
const dummyImages: DockerImage[] = [
  {
    id: 'image-1',
    repository: 'n8nio/n8n',
    tag: 'latest',
    size: 512 * 1024 * 1024, // 512 MB
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'image-2',
    repository: 'postgres',
    tag: '13',
    size: 256 * 1024 * 1024, // 256 MB
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'image-3',
    repository: 'redis',
    tag: 'alpine',
    size: 32 * 1024 * 1024, // 32 MB
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'image-4',
    repository: 'nginx',
    tag: 'alpine',
    size: 16 * 1024 * 1024, // 16 MB
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'image-5',
    repository: 'ecosphere/mcp-server',
    tag: 'latest',
    size: 256 * 1024 * 1024, // 256 MB
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'image-6',
    repository: 'ecosphere/broken-service',
    tag: 'latest',
    size: 128 * 1024 * 1024, // 128 MB
    created: '2023-01-01T00:00:00Z'
  }
];

// Dummy-Daten für Docker-Netzwerke
const dummyNetworks: DockerNetwork[] = [
  {
    id: 'network-1',
    name: 'dev-server-network',
    driver: 'bridge',
    scope: 'local',
    containers: ['n8n', 'postgres', 'redis', 'nginx', 'mcp-server', 'broken-service'],
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'network-2',
    name: 'bridge',
    driver: 'bridge',
    scope: 'local',
    containers: [],
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'network-3',
    name: 'host',
    driver: 'host',
    scope: 'local',
    containers: [],
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'network-4',
    name: 'none',
    driver: 'null',
    scope: 'local',
    containers: [],
    created: '2023-01-01T00:00:00Z'
  }
];

// Dummy-Daten für Docker-Volumes
const dummyVolumes: DockerVolume[] = [
  {
    id: 'volume-1',
    name: 'n8n-data',
    driver: 'local',
    mountpoint: '/var/lib/docker/volumes/n8n-data/_data',
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'volume-2',
    name: 'postgres-data',
    driver: 'local',
    mountpoint: '/var/lib/docker/volumes/postgres-data/_data',
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'volume-3',
    name: 'redis-data',
    driver: 'local',
    mountpoint: '/var/lib/docker/volumes/redis-data/_data',
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'volume-4',
    name: 'nginx-conf',
    driver: 'local',
    mountpoint: '/var/lib/docker/volumes/nginx-conf/_data',
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'volume-5',
    name: 'nginx-ssl',
    driver: 'local',
    mountpoint: '/var/lib/docker/volumes/nginx-ssl/_data',
    created: '2023-01-01T00:00:00Z'
  },
  {
    id: 'volume-6',
    name: 'mcp-data',
    driver: 'local',
    mountpoint: '/var/lib/docker/volumes/mcp-data/_data',
    created: '2023-01-01T00:00:00Z'
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

const SearchContainer = styled.div`
  margin-bottom: 20px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 10px 15px;
  border: 1px solid ${colors.divider};
  border-radius: 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: ${colors.primary.main};
    box-shadow: 0 0 0 2px ${colors.primary.light}40;
  }
`;

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 600px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid ${colors.divider};
`;

const ModalTitle = styled.h2`
  font-size: 1.25rem;
  margin: 0;
`;

const ModalCloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: ${colors.text.secondary};
  
  &:hover {
    color: ${colors.text.primary};
  }
  
  &:focus {
    outline: none;
  }
`;

const ModalBody = styled.div`
  padding: 20px;
`;

const ModalFooter = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid ${colors.divider};
`;

const FormGroup = styled.div`
  margin-bottom: 15px;
`;

const Label = styled.label`
  display: block;
  font-size: 0.875rem;
  margin-bottom: 5px;
  color: ${colors.text.secondary};
`;

const Input = styled.input`
  width: 100%;
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
  width: 100%;
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
  width: 100%;
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

const formatBytes = (bytes: number, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

// Dummy-Logs für die Logs-Ansicht
const dummyLogs = [
  '2023-01-01T12:00:00.000Z [INFO] Container gestartet',
  '2023-01-01T12:00:01.000Z [INFO] Verbindung zu Datenbank hergestellt',
  '2023-01-01T12:00:02.000Z [INFO] Server läuft auf Port 3000',
  '2023-01-01T12:00:03.000Z [INFO] Anfrage empfangen: GET /api/v1/status',
  '2023-01-01T12:00:04.000Z [INFO] Antwort gesendet: 200 OK',
  '2023-01-01T12:00:05.000Z [WARNING] Hohe CPU-Auslastung: 80%',
  '2023-01-01T12:00:06.000Z [INFO] Anfrage empfangen: POST /api/v1/data',
  '2023-01-01T12:00:07.000Z [ERROR] Fehler beim Verarbeiten der Anfrage: Ungültige Daten',
  '2023-01-01T12:00:08.000Z [INFO] Anfrage empfangen: GET /api/v1/status',
  '2023-01-01T12:00:09.000Z [INFO] Antwort gesendet: 200 OK',
  '2023-01-01T12:00:10.000Z [INFO] Anfrage empfangen: GET /api/v1/data',
  '2023-01-01T12:00:11.000Z [INFO] Antwort gesendet: 200 OK',
  '2023-01-01T12:00:12.000Z [INFO] Anfrage empfangen: GET /api/v1/status',
  '2023-01-01T12:00:13.000Z [INFO] Antwort gesendet: 200 OK',
  '2023-01-01T12:00:14.000Z [WARNING] Speicherauslastung: 75%',
  '2023-01-01T12:00:15.000Z [INFO] Garbage Collection ausgeführt',
  '2023-01-01T12:00:16.000Z [INFO] Speicherauslastung: 50%',
  '2023-01-01T12:00:17.000Z [INFO] Anfrage empfangen: GET /api/v1/status',
  '2023-01-01T12:00:18.000Z [INFO] Antwort gesendet: 200 OK',
  '2023-01-01T12:00:19.000Z [INFO] Anfrage empfangen: GET /api/v1/data',
  '2023-01-01T12:00:20.000Z [INFO] Antwort gesendet: 200 OK'
];

interface ModalProps {
  title: string;
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

const Modal: React.FC<ModalProps> = ({ title, isOpen, onClose, children, footer }) => {
  if (!isOpen) return null;
  
  return (
    <ModalOverlay>
      <ModalContent>
        <ModalHeader>
          <ModalTitle>{title}</ModalTitle>
          <ModalCloseButton onClick={onClose}>&times;</ModalCloseButton>
        </ModalHeader>
        <ModalBody>
          {children}
        </ModalBody>
        {footer && <ModalFooter>{footer}</ModalFooter>}
      </ModalContent>
    </ModalOverlay>
  );
};

const DockerManager: React.FC = () => {
  const [containers, setContainers] = useState<DockerContainer[]>([]);
  const [images, setImages] = useState<DockerImage[]>([]);
  const [networks, setNetworks] = useState<DockerNetwork[]>([]);
  const [volumes, setVolumes] = useState<DockerVolume[]>([]);
  const [activeTab, setActiveTab] = useState<'containers' | 'images' | 'networks' | 'volumes'>('containers');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modals
  const [isNewContainerModalOpen, setIsNewContainerModalOpen] = useState(false);
  const [isLogsModalOpen, setIsLogsModalOpen] = useState(false);
  const [selectedContainer, setSelectedContainer] = useState<DockerContainer | null>(null);
  
  useEffect(() => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    // Simuliere einen API-Aufruf mit den Dummy-Daten
    const fetchDockerData = async () => {
      try {
        setLoading(true);
        // Simuliere eine Verzögerung
        await new Promise(resolve => setTimeout(resolve, 500));
        setContainers(dummyContainers);
        setImages(dummyImages);
        setNetworks(dummyNetworks);
        setVolumes(dummyVolumes);
      } catch (err: any) {
        setError('Fehler beim Laden der Docker-Daten');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDockerData();
  }, []);
  
  const handleStartContainer = (containerId: string) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Starte Container: ${containerId}`);
    
    // Simuliere das Starten des Containers
    const updatedContainers = containers.map(container => 
      container.id === containerId ? { ...container, status: 'running' as const } : container
    );
    setContainers(updatedContainers);
  };
  
  const handleStopContainer = (containerId: string) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Stoppe Container: ${containerId}`);
    
    // Simuliere das Stoppen des Containers
    const updatedContainers = containers.map(container => 
      container.id === containerId ? { ...container, status: 'stopped' as const } : container
    );
    setContainers(updatedContainers);
  };
  
  const handleRestartContainer = (containerId: string) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Starte Container neu: ${containerId}`);
    
    // Simuliere das Neustarten des Containers
    const updatedContainers = containers.map(container => 
      container.id === containerId ? { ...container, status: 'running' as const } : container
    );
    setContainers(updatedContainers);
  };
  
  const handleRemoveContainer = (containerId: string) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Entferne Container: ${containerId}`);
    
    // Simuliere das Entfernen des Containers
    const updatedContainers = containers.filter(container => container.id !== containerId);
    setContainers(updatedContainers);
  };
  
  const handleRemoveImage = (imageId: string) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Entferne Image: ${imageId}`);
    
    // Simuliere das Entfernen des Images
    const updatedImages = images.filter(image => image.id !== imageId);
    setImages(updatedImages);
  };
  
  const handleRemoveNetwork = (networkId: string) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Entferne Netzwerk: ${networkId}`);
    
    // Simuliere das Entfernen des Netzwerks
    const updatedNetworks = networks.filter(network => network.id !== networkId);
    setNetworks(updatedNetworks);
  };
  
  const handleRemoveVolume = (volumeId: string) => {
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log(`Entferne Volume: ${volumeId}`);
    
    // Simuliere das Entfernen des Volumes
    const updatedVolumes = volumes.filter(volume => volume.id !== volumeId);
    setVolumes(updatedVolumes);
  };
  
  const handleShowLogs = (container: DockerContainer) => {
    setSelectedContainer(container);
    setIsLogsModalOpen(true);
  };
  
  const handleCreateContainer = (event: React.FormEvent) => {
    event.preventDefault();
    // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
    console.log('Container erstellen');
    
    // Schließe das Modal
    setIsNewContainerModalOpen(false);
  };
  
  // Filtere die Daten basierend auf dem Suchbegriff
  const filteredContainers = containers.filter(container => 
    container.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    container.image.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  const filteredImages = images.filter(image => 
    image.repository.toLowerCase().includes(searchTerm.toLowerCase()) ||
    image.tag.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  const filteredNetworks = networks.filter(network => 
    network.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    network.driver.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  const filteredVolumes = volumes.filter(volume => 
    volume.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    volume.driver.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  if (loading && containers.length === 0) {
    return <div>Lade Docker-Daten...</div>;
  }
  
  if (error) {
    return <div>Fehler: {error}</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>Docker-Container-Verwaltung</Title>
        <div>
          {activeTab === 'containers' && (
            <Button 
              variant="primary" 
              onClick={() => setIsNewContainerModalOpen(true)}
            >
              Neuer Container
            </Button>
          )}
        </div>
      </Header>
      
      <TabsContainer>
        <TabList>
          <Tab 
            $active={activeTab === 'containers'} 
            onClick={() => setActiveTab('containers')}
          >
            Container
          </Tab>
          <Tab 
            $active={activeTab === 'images'} 
            onClick={() => setActiveTab('images')}
          >
            Images
          </Tab>
          <Tab 
            $active={activeTab === 'networks'} 
            onClick={() => setActiveTab('networks')}
          >
            Netzwerke
          </Tab>
          <Tab 
            $active={activeTab === 'volumes'} 
            onClick={() => setActiveTab('volumes')}
          >
            Volumes
          </Tab>
        </TabList>
        
        <SearchContainer>
          <SearchInput 
            type="text" 
            placeholder={`${activeTab === 'containers' ? 'Container' : activeTab === 'images' ? 'Images' : activeTab === 'networks' ? 'Netzwerke' : 'Volumes'} suchen...`} 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </SearchContainer>
        
        <TabPanel $active={activeTab === 'containers'}>
          <Card>
            <div style={{ padding: '0 20px 20px' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableHeaderCell>Name</TableHeaderCell>
                    <TableHeaderCell>Image</TableHeaderCell>
                    <TableHeaderCell>Status</TableHeaderCell>
                    <TableHeaderCell>Ports</TableHeaderCell>
                    <TableHeaderCell>Größe</TableHeaderCell>
                    <TableHeaderCell>Erstellt</TableHeaderCell>
                    <TableHeaderCell>Aktionen</TableHeaderCell>
                  </TableRow>
                </TableHead>
                <tbody>
                  {filteredContainers.map(container => (
                    <TableRow key={container.id}>
                      <TableCell>{container.name}</TableCell>
                      <TableCell>{container.image}</TableCell>
                      <TableCell>
                        <StatusBadge $status={container.status}>
                          {container.status === 'running' ? 'Läuft' : 
                           container.status === 'stopped' ? 'Gestoppt' : 
                           container.status === 'paused' ? 'Pausiert' : 
                           container.status === 'restarting' ? 'Neustart' : 
                           'Erstellt'}
                        </StatusBadge>
                      </TableCell>
                      <TableCell>{container.ports.join(', ')}</TableCell>
                      <TableCell>{formatBytes(container.size)}</TableCell>
                      <TableCell>{new Date(container.created).toLocaleString()}</TableCell>
                      <TableCell>
                        <div style={{ display: 'flex', gap: '5px' }}>
                          {container.status === 'running' ? (
                            <Button 
                              variant="outlined" 
                              size="small"
                              onClick={() => handleStopContainer(container.id)}
                            >
                              Stoppen
                            </Button>
                          ) : (
                            <Button 
                              variant="primary" 
                              size="small"
                              onClick={() => handleStartContainer(container.id)}
                            >
                              Starten
                            </Button>
                          )}
                          <Button 
                            variant="outlined" 
                            size="small"
                            onClick={() => handleRestartContainer(container.id)}
                          >
                            Neustart
                          </Button>
                          <Button 
                            variant="outlined" 
                            size="small"
                            onClick={() => handleShowLogs(container)}
                          >
                            Logs
                          </Button>
                          <Button 
                            variant="outlined" 
                            size="small"
                            color="error"
                            onClick={() => handleRemoveContainer(container.id)}
                          >
                            Entfernen
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
        
        <TabPanel $active={activeTab === 'images'}>
          <Card>
            <div style={{ padding: '0 20px 20px' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableHeaderCell>Repository</TableHeaderCell>
                    <TableHeaderCell>Tag</TableHeaderCell>
                    <TableHeaderCell>Größe</TableHeaderCell>
                    <TableHeaderCell>Erstellt</TableHeaderCell>
                    <TableHeaderCell>Aktionen</TableHeaderCell>
                  </TableRow>
                </TableHead>
                <tbody>
                  {filteredImages.map(image => (
                    <TableRow key={image.id}>
                      <TableCell>{image.repository}</TableCell>
                      <TableCell>{image.tag}</TableCell>
                      <TableCell>{formatBytes(image.size)}</TableCell>
                      <TableCell>{new Date(image.created).toLocaleString()}</TableCell>
                      <TableCell>
                        <div style={{ display: 'flex', gap: '5px' }}>
                          <Button 
                            variant="primary" 
                            size="small"
                          >
                            Container erstellen
                          </Button>
                          <Button 
                            variant="outlined" 
                            size="small"
                            color="error"
                            onClick={() => handleRemoveImage(image.id)}
                          >
                            Entfernen
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
        
        <TabPanel $active={activeTab === 'networks'}>
          <Card>
            <div style={{ padding: '0 20px 20px' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableHeaderCell>Name</TableHeaderCell>
                    <TableHeaderCell>Driver</TableHeaderCell>
                    <TableHeaderCell>Scope</TableHeaderCell>
                    <TableHeaderCell>Container</TableHeaderCell>
                    <TableHeaderCell>Erstellt</TableHeaderCell>
                    <TableHeaderCell>Aktionen</TableHeaderCell>
                  </TableRow>
                </TableHead>
                <tbody>
                  {filteredNetworks.map(network => (
                    <TableRow key={network.id}>
                      <TableCell>{network.name}</TableCell>
                      <TableCell>{network.driver}</TableCell>
                      <TableCell>{network.scope}</TableCell>
                      <TableCell>{network.containers.join(', ')}</TableCell>
                      <TableCell>{new Date(network.created).toLocaleString()}</TableCell>
                      <TableCell>
                        <div style={{ display: 'flex', gap: '5px' }}>
                          <Button 
                            variant="outlined" 
                            size="small"
                          >
                            Details
                          </Button>
                          <Button 
                            variant="outlined" 
                            size="small"
                            color="error"
                            onClick={() => handleRemoveNetwork(network.id)}
                          >
                            Entfernen
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
        
        <TabPanel $active={activeTab === 'volumes'}>
          <Card>
            <div style={{ padding: '0 20px 20px' }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableHeaderCell>Name</TableHeaderCell>
                    <TableHeaderCell>Driver</TableHeaderCell>
                    <TableHeaderCell>Mountpoint</TableHeaderCell>
                    <TableHeaderCell>Erstellt</TableHeaderCell>
                    <TableHeaderCell>Aktionen</TableHeaderCell>
                  </TableRow>
                </TableHead>
                <tbody>
                  {filteredVolumes.map(volume => (
                    <TableRow key={volume.id}>
                      <TableCell>{volume.name}</TableCell>
                      <TableCell>{volume.driver}</TableCell>
                      <TableCell>{volume.mountpoint}</TableCell>
                      <TableCell>{new Date(volume.created).toLocaleString()}</TableCell>
                      <TableCell>
                        <div style={{ display: 'flex', gap: '5px' }}>
                          <Button 
                            variant="outlined" 
                            size="small"
                          >
                            Details
                          </Button>
                          <Button 
                            variant="outlined" 
                            size="small"
                            color="error"
                            onClick={() => handleRemoveVolume(volume.id)}
                          >
                            Entfernen
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
      
      {/* Modal für Container-Logs */}
      <Modal
        title={`Logs: ${selectedContainer?.name || ''}`}
        isOpen={isLogsModalOpen}
        onClose={() => setIsLogsModalOpen(false)}
        footer={
          <Button variant="primary" onClick={() => setIsLogsModalOpen(false)}>
            Schließen
          </Button>
        }
      >
        <LogsContainer>
          {dummyLogs.map((log, index) => (
            <LogEntry key={index}>
              {log}
            </LogEntry>
          ))}
        </LogsContainer>
      </Modal>
      
      {/* Modal für neuen Container */}
      <Modal
        title="Neuen Container erstellen"
        isOpen={isNewContainerModalOpen}
        onClose={() => setIsNewContainerModalOpen(false)}
        footer={
          <>
            <Button 
              variant="outlined" 
              onClick={() => setIsNewContainerModalOpen(false)}
            >
              Abbrechen
            </Button>
            <Button 
              variant="primary" 
              onClick={handleCreateContainer}
            >
              Erstellen
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateContainer}>
          <FormGroup>
            <Label htmlFor="name">Name</Label>
            <Input 
              id="name" 
              type="text" 
              placeholder="z.B. my-container" 
            />
          </FormGroup>
          
          <FormGroup>
            <Label htmlFor="image">Image</Label>
            <Select id="image">
              <option value="">Bitte wählen...</option>
              {images.map(image => (
                <option key={image.id} value={`${image.repository}:${image.tag}`}>
                  {image.repository}:{image.tag}
                </option>
              ))}
            </Select>
          </FormGroup>
          
          <FormGroup>
            <Label htmlFor="ports">Ports</Label>
            <Input 
              id="ports" 
              type="text" 
              placeholder="z.B. 8080:80, 443:443" 
            />
          </FormGroup>
          
          <FormGroup>
            <Label htmlFor="volumes">Volumes</Label>
            <Input 
              id="volumes" 
              type="text" 
              placeholder="z.B. my-volume:/data" 
            />
          </FormGroup>
          
          <FormGroup>
            <Label htmlFor="networks">Netzwerke</Label>
            <Select id="networks">
              <option value="">Bitte wählen...</option>
              {networks.map(network => (
                <option key={network.id} value={network.name}>
                  {network.name}
                </option>
              ))}
            </Select>
          </FormGroup>
          
          <FormGroup>
            <Label htmlFor="command">Befehl</Label>
            <Input 
              id="command" 
              type="text" 
              placeholder="z.B. nginx -g 'daemon off;'" 
            />
          </FormGroup>
          
          <FormGroup>
            <Label htmlFor="env">Umgebungsvariablen</Label>
            <Textarea 
              id="env" 
              placeholder="z.B. KEY1=VALUE1&#10;KEY2=VALUE2" 
            />
          </FormGroup>
        </form>
      </Modal>
    </Container>
  );
};

export default DockerManager;