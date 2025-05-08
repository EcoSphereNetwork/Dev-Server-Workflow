# Phase 6: Web-Benutzeroberfläche mit smolitux-ui

Diese Dokumentation enthält eine detaillierte Schritt-für-Schritt-Anleitung für die Implementierung der Web-Benutzeroberfläche mit der smolitux-ui-Bibliothek im Rahmen von Phase 6 des Verbesserungsplans.

## Übersicht

Die Web-Benutzeroberfläche wird mit React und der smolitux-ui-Bibliothek entwickelt. Sie bietet eine intuitive und benutzerfreundliche Schnittstelle für die Verwaltung und Überwachung des Dev-Server-Workflow-Systems.

## Voraussetzungen

- Node.js (Version 16 oder höher)
- npm oder yarn
- Grundkenntnisse in React und TypeScript
- Zugriff auf das GitHub-Repository der smolitux-ui-Bibliothek

## Schritt-für-Schritt-Anleitung

### Woche 1: Grundlegende Infrastruktur

#### Tag 1: Projekt-Setup

1. **Erstellen des React-Projekts**

   ```bash
   # Erstellen eines neuen React-Projekts mit TypeScript
   npx create-react-app frontend --template typescript
   cd frontend
   ```

2. **Installation der smolitux-ui-Bibliothek**

   ```bash
   # Installation der smolitux-ui-Bibliothek
   npm install @ecosphere/smolitux-ui

   # Installation von Peer-Dependencies
   npm install styled-components @types/styled-components
   ```

3. **Konfiguration von ESLint und Prettier**

   ```bash
   # Installation von ESLint und Prettier
   npm install --save-dev eslint prettier eslint-config-prettier eslint-plugin-prettier

   # Erstellen der ESLint-Konfigurationsdatei
   cat > .eslintrc.json << EOF
   {
     "extends": [
       "react-app",
       "react-app/jest",
       "prettier"
     ],
     "plugins": ["prettier"],
     "rules": {
       "prettier/prettier": "error",
       "react/jsx-uses-react": "off",
       "react/react-in-jsx-scope": "off"
     }
   }
   EOF

   # Erstellen der Prettier-Konfigurationsdatei
   cat > .prettierrc << EOF
   {
     "singleQuote": true,
     "trailingComma": "es5",
     "tabWidth": 2,
     "semi": true,
     "printWidth": 100
   }
   EOF
   ```

4. **Aktualisieren der package.json**

   ```json
   {
     "scripts": {
       "start": "react-scripts start",
       "build": "react-scripts build",
       "test": "react-scripts test",
       "eject": "react-scripts eject",
       "lint": "eslint src --ext .ts,.tsx",
       "lint:fix": "eslint src --ext .ts,.tsx --fix",
       "format": "prettier --write \"src/**/*.{ts,tsx}\""
     }
   }
   ```

#### Tag 2: Architektur-Setup

1. **Erstellen der Verzeichnisstruktur**

   ```bash
   # Erstellen der Verzeichnisstruktur
   mkdir -p src/{api,assets,components/{common,dashboard,mcp,workflows,auth},contexts,hooks,layouts,pages,routes,services,store,types,utils}
   ```

2. **Konfiguration des Routing**

   ```bash
   # Installation von React Router
   npm install react-router-dom @types/react-router-dom
   ```

   ```tsx
   // src/routes/index.tsx
   import { BrowserRouter, Routes, Route } from 'react-router-dom';
   import { MainLayout } from '../layouts';
   import { Dashboard, MCPServers, Workflows, Settings, Login } from '../pages';

   export function AppRoutes() {
     return (
       <BrowserRouter>
         <Routes>
           <Route path="/login" element={<Login />} />
           <Route path="/" element={<MainLayout />}>
             <Route index element={<Dashboard />} />
             <Route path="mcp-servers" element={<MCPServers />} />
             <Route path="workflows" element={<MCPServers />} />
             <Route path="settings" element={<Settings />} />
           </Route>
         </Routes>
       </BrowserRouter>
     );
   }
   ```

3. **Einrichten der Zustandsverwaltung**

   ```bash
   # Installation von Zustand
   npm install zustand
   ```

   ```tsx
   // src/store/auth.ts
   import create from 'zustand';

   interface AuthState {
     token: string | null;
     user: any | null;
     isAuthenticated: boolean;
     login: (token: string, user: any) => void;
     logout: () => void;
   }

   export const useAuthStore = create<AuthState>((set) => ({
     token: localStorage.getItem('token'),
     user: JSON.parse(localStorage.getItem('user') || 'null'),
     isAuthenticated: !!localStorage.getItem('token'),
     login: (token, user) => {
       localStorage.setItem('token', token);
       localStorage.setItem('user', JSON.stringify(user));
       set({ token, user, isAuthenticated: true });
     },
     logout: () => {
       localStorage.removeItem('token');
       localStorage.removeItem('user');
       set({ token: null, user: null, isAuthenticated: false });
     },
   }));
   ```

4. **Einrichten der API-Clients**

   ```bash
   # Installation von Axios
   npm install axios
   ```

   ```tsx
   // src/api/client.ts
   import axios from 'axios';

   const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

   export const apiClient = axios.create({
     baseURL: API_URL,
     headers: {
       'Content-Type': 'application/json',
     },
   });

   // Interceptor für das Hinzufügen des Auth-Tokens
   apiClient.interceptors.request.use(
     (config) => {
       const token = localStorage.getItem('token');
       if (token) {
         config.headers.Authorization = `Bearer ${token}`;
       }
       return config;
     },
     (error) => Promise.reject(error)
   );
   ```

#### Tag 3: Theme und Styling

1. **Konfiguration des smolitux-ui Themes**

   ```tsx
   // src/theme.ts
   import { createTheme } from '@ecosphere/smolitux-ui';

   export const theme = createTheme({
     colors: {
       primary: {
         main: '#3f51b5',
         light: '#757de8',
         dark: '#002984',
         contrastText: '#ffffff'
       },
       secondary: {
         main: '#f50057',
         light: '#ff5983',
         dark: '#bb002f',
         contrastText: '#ffffff'
       },
       // Weitere Farben...
     },
     typography: {
       fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
       // Weitere Typografie-Optionen...
     },
     // Weitere Theme-Optionen...
   });
   ```

2. **Einrichten des ThemeProvider**

   ```tsx
   // src/App.tsx
   import { ThemeProvider } from '@ecosphere/smolitux-ui';
   import { theme } from './theme';
   import { AppRoutes } from './routes';

   function App() {
     return (
       <ThemeProvider theme={theme}>
         <AppRoutes />
       </ThemeProvider>
     );
   }

   export default App;
   ```

3. **Erstellen von globalen Styles**

   ```tsx
   // src/globalStyles.ts
   import { createGlobalStyle } from 'styled-components';

   export const GlobalStyles = createGlobalStyle`
     body {
       margin: 0;
       padding: 0;
       font-family: 'Roboto', sans-serif;
       background-color: #f5f5f5;
     }

     * {
       box-sizing: border-box;
     }
   `;
   ```

   ```tsx
   // src/index.tsx
   import React from 'react';
   import ReactDOM from 'react-dom';
   import App from './App';
   import { GlobalStyles } from './globalStyles';

   ReactDOM.render(
     <React.StrictMode>
       <GlobalStyles />
       <App />
     </React.StrictMode>,
     document.getElementById('root')
   );
   ```

#### Tag 4-5: Authentifizierung und Layouts

1. **Implementierung der Anmeldung**

   ```tsx
   // src/pages/Login.tsx
   import { useState } from 'react';
   import { useNavigate } from 'react-router-dom';
   import { Card, Box, Typography, Input, Button, Alert } from '@ecosphere/smolitux-ui';
   import { useAuthStore } from '../store/auth';
   import { apiClient } from '../api/client';

   export function Login() {
     const [username, setUsername] = useState('');
     const [password, setPassword] = useState('');
     const [error, setError] = useState('');
     const [loading, setLoading] = useState(false);
     const navigate = useNavigate();
     const login = useAuthStore((state) => state.login);

     const handleLogin = async (e: React.FormEvent) => {
       e.preventDefault();
       setError('');
       setLoading(true);

       try {
         const response = await apiClient.post('/auth/login', { username, password });
         login(response.data.token, response.data.user);
         navigate('/');
       } catch (err: any) {
         setError(err.response?.data?.message || 'Anmeldung fehlgeschlagen');
       } finally {
         setLoading(false);
       }
     };

     return (
       <Box
         display="flex"
         justifyContent="center"
         alignItems="center"
         minHeight="100vh"
         bg="background.default"
       >
         <Card width="400px" p={4}>
           <Typography variant="h4" mb={3} textAlign="center">
             Anmelden
           </Typography>

           {error && (
             <Alert variant="error" mb={3}>
               {error}
             </Alert>
           )}

           <form onSubmit={handleLogin}>
             <Box mb={3}>
               <Input
                 label="Benutzername"
                 value={username}
                 onChange={(e) => setUsername(e.target.value)}
                 fullWidth
                 required
               />
             </Box>

             <Box mb={4}>
               <Input
                 label="Passwort"
                 type="password"
                 value={password}
                 onChange={(e) => setPassword(e.target.value)}
                 fullWidth
                 required
               />
             </Box>

             <Button
               variant="primary"
               type="submit"
               fullWidth
               disabled={loading}
             >
               {loading ? 'Wird angemeldet...' : 'Anmelden'}
             </Button>
           </form>
         </Card>
       </Box>
     );
   }
   ```

2. **Implementierung des Hauptlayouts**

   ```tsx
   // src/layouts/MainLayout.tsx
   import { useState } from 'react';
   import { Outlet, useNavigate } from 'react-router-dom';
   import {
     Box,
     Navbar,
     Sidebar,
     SidebarItem,
     Icon,
     Avatar,
     Dropdown,
     DropdownItem,
   } from '@ecosphere/smolitux-ui';
   import { useAuthStore } from '../store/auth';

   export function MainLayout() {
     const [sidebarOpen, setSidebarOpen] = useState(true);
     const navigate = useNavigate();
     const { user, logout } = useAuthStore();

     const handleLogout = () => {
       logout();
       navigate('/login');
     };

     return (
       <Box display="flex" height="100vh">
         <Sidebar open={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)}>
           <SidebarItem
             icon={<Icon name="dashboard" />}
             label="Dashboard"
             onClick={() => navigate('/')}
           />
           <SidebarItem
             icon={<Icon name="server" />}
             label="MCP-Server"
             onClick={() => navigate('/mcp-servers')}
           />
           <SidebarItem
             icon={<Icon name="workflow" />}
             label="Workflows"
             onClick={() => navigate('/workflows')}
           />
           <SidebarItem
             icon={<Icon name="settings" />}
             label="Einstellungen"
             onClick={() => navigate('/settings')}
           />
         </Sidebar>

         <Box display="flex" flexDirection="column" flex={1} overflow="hidden">
           <Navbar>
             <Box ml="auto">
               <Dropdown
                 trigger={
                   <Avatar
                     name={user?.name || 'Benutzer'}
                     src={user?.avatar}
                     size="sm"
                   />
                 }
               >
                 <DropdownItem onClick={() => navigate('/profile')}>
                   Profil
                 </DropdownItem>
                 <DropdownItem onClick={handleLogout}>
                   Abmelden
                 </DropdownItem>
               </Dropdown>
             </Box>
           </Navbar>

           <Box flex={1} p={3} overflow="auto">
             <Outlet />
           </Box>
         </Box>
       </Box>
     );
   }
   ```

3. **Implementierung der Berechtigungsprüfung**

   ```tsx
   // src/components/auth/ProtectedRoute.tsx
   import { Navigate, useLocation } from 'react-router-dom';
   import { useAuthStore } from '../../store/auth';

   interface ProtectedRouteProps {
     children: React.ReactNode;
     requiredPermission?: string;
   }

   export function ProtectedRoute({ children, requiredPermission }: ProtectedRouteProps) {
     const { isAuthenticated, user } = useAuthStore();
     const location = useLocation();

     if (!isAuthenticated) {
       return <Navigate to="/login" state={{ from: location }} replace />;
     }

     if (requiredPermission && !user?.permissions?.includes(requiredPermission)) {
       return <Navigate to="/unauthorized" replace />;
     }

     return <>{children}</>;
   }
   ```

### Woche 2: Hauptkomponenten

#### Tag 1-2: Dashboard

1. **Implementierung des Dashboard-Layouts**

   ```tsx
   // src/pages/Dashboard.tsx
   import { useEffect, useState } from 'react';
   import {
     Box,
     Grid,
     Card,
     Typography,
     Chart,
     Badge,
   } from '@ecosphere/smolitux-ui';
   import { apiClient } from '../api/client';

   export function Dashboard() {
     const [stats, setStats] = useState({
       mcpServers: { total: 0, online: 0, offline: 0 },
       workflows: { total: 0, active: 0, inactive: 0 },
       users: { total: 0, active: 0 },
       cpuUsage: 0,
     });

     const [loading, setLoading] = useState(true);

     useEffect(() => {
       const fetchStats = async () => {
         try {
           const response = await apiClient.get('/dashboard/stats');
           setStats(response.data);
         } catch (error) {
           console.error('Fehler beim Laden der Statistiken:', error);
         } finally {
           setLoading(false);
         }
       };

       fetchStats();
     }, []);

     if (loading) {
       return <Box p={3}>Laden...</Box>;
     }

     return (
       <Box>
         <Typography variant="h4" mb={3}>Dashboard</Typography>
         
         <Grid container spacing={3}>
           <Grid item xs={12} md={6} lg={3}>
             <Card title="MCP-Server">
               <Typography variant="h2">{stats.mcpServers.total}</Typography>
               <Box mt={2} display="flex" gap={2}>
                 <Badge variant="success">{stats.mcpServers.online} Online</Badge>
                 <Badge variant="error">{stats.mcpServers.offline} Offline</Badge>
               </Box>
             </Card>
           </Grid>
           
           <Grid item xs={12} md={6} lg={3}>
             <Card title="Workflows">
               <Typography variant="h2">{stats.workflows.total}</Typography>
               <Box mt={2} display="flex" gap={2}>
                 <Badge variant="success">{stats.workflows.active} Aktiv</Badge>
                 <Badge variant="warning">{stats.workflows.inactive} Inaktiv</Badge>
               </Box>
             </Card>
           </Grid>
           
           <Grid item xs={12} md={6} lg={3}>
             <Card title="Benutzer">
               <Typography variant="h2">{stats.users.total}</Typography>
               <Box mt={2}>
                 <Badge variant="info">{stats.users.active} Aktiv</Badge>
               </Box>
             </Card>
           </Grid>
           
           <Grid item xs={12} md={6} lg={3}>
             <Card title="CPU-Auslastung">
               <Typography variant="h2">{stats.cpuUsage}%</Typography>
               <Box mt={2}>
                 <Badge 
                   variant={
                     stats.cpuUsage < 50 ? 'success' : 
                     stats.cpuUsage < 80 ? 'warning' : 'error'
                   }
                 >
                   {
                     stats.cpuUsage < 50 ? 'Normal' : 
                     stats.cpuUsage < 80 ? 'Mittel' : 'Hoch'
                   }
                 </Badge>
               </Box>
             </Card>
           </Grid>
           
           {/* Weitere Dashboard-Komponenten... */}
         </Grid>
       </Box>
     );
   }
   ```

2. **Implementierung der Systemstatus-Anzeige**

   ```tsx
   // src/components/dashboard/SystemStatus.tsx
   import { useEffect, useState } from 'react';
   import { Card, Table, Badge, Box, Typography } from '@ecosphere/smolitux-ui';
   import { apiClient } from '../../api/client';

   export function SystemStatus() {
     const [servers, setServers] = useState([]);
     const [loading, setLoading] = useState(true);

     useEffect(() => {
       const fetchServers = async () => {
         try {
           const response = await apiClient.get('/mcp-servers/status');
           setServers(response.data);
         } catch (error) {
           console.error('Fehler beim Laden der Server-Status:', error);
         } finally {
           setLoading(false);
         }
       };

       fetchServers();
       const interval = setInterval(fetchServers, 30000); // Alle 30 Sekunden aktualisieren

       return () => clearInterval(interval);
     }, []);

     if (loading) {
       return <Box p={3}>Laden...</Box>;
     }

     return (
       <Card title="System-Status">
         <Table>
           <Table.Header>
             <Table.Row>
               <Table.HeaderCell>Server</Table.HeaderCell>
               <Table.HeaderCell>Status</Table.HeaderCell>
               <Table.HeaderCell>Letzte Aktualisierung</Table.HeaderCell>
             </Table.Row>
           </Table.Header>
           <Table.Body>
             {servers.map((server) => (
               <Table.Row key={server.id}>
                 <Table.Cell>{server.name}</Table.Cell>
                 <Table.Cell>
                   <Badge 
                     variant={server.status === 'online' ? 'success' : 'error'}
                   >
                     {server.status === 'online' ? 'Online' : 'Offline'}
                   </Badge>
                 </Table.Cell>
                 <Table.Cell>{new Date(server.lastUpdated).toLocaleString()}</Table.Cell>
               </Table.Row>
             ))}
           </Table.Body>
         </Table>
       </Card>
     );
   }
   ```

#### Tag 3-4: MCP-Server-Verwaltung

1. **Implementierung der Server-Liste**

   ```tsx
   // src/pages/MCPServers.tsx
   import { useState, useEffect } from 'react';
   import {
     Box,
     Typography,
     DataGrid,
     Button,
     Badge,
     Modal,
     Input,
     Select,
   } from '@ecosphere/smolitux-ui';
   import { apiClient } from '../api/client';

   export function MCPServers() {
     const [servers, setServers] = useState([]);
     const [loading, setLoading] = useState(true);
     const [modalOpen, setModalOpen] = useState(false);
     const [selectedServer, setSelectedServer] = useState(null);
     const [formData, setFormData] = useState({
       name: '',
       url: '',
       description: '',
       type: 'standard',
     });

     useEffect(() => {
       fetchServers();
     }, []);

     const fetchServers = async () => {
       try {
         setLoading(true);
         const response = await apiClient.get('/mcp-servers');
         setServers(response.data);
       } catch (error) {
         console.error('Fehler beim Laden der Server:', error);
       } finally {
         setLoading(false);
       }
     };

     const handleStartServer = async (id) => {
       try {
         await apiClient.post(`/mcp-servers/${id}/start`);
         fetchServers();
       } catch (error) {
         console.error('Fehler beim Starten des Servers:', error);
       }
     };

     const handleStopServer = async (id) => {
       try {
         await apiClient.post(`/mcp-servers/${id}/stop`);
         fetchServers();
       } catch (error) {
         console.error('Fehler beim Stoppen des Servers:', error);
       }
     };

     const handleAddServer = () => {
       setSelectedServer(null);
       setFormData({
         name: '',
         url: '',
         description: '',
         type: 'standard',
       });
       setModalOpen(true);
     };

     const handleEditServer = (server) => {
       setSelectedServer(server);
       setFormData({
         name: server.name,
         url: server.url,
         description: server.description || '',
         type: server.type || 'standard',
       });
       setModalOpen(true);
     };

     const handleSaveServer = async () => {
       try {
         if (selectedServer) {
           await apiClient.put(`/mcp-servers/${selectedServer.id}`, formData);
         } else {
           await apiClient.post('/mcp-servers', formData);
         }
         setModalOpen(false);
         fetchServers();
       } catch (error) {
         console.error('Fehler beim Speichern des Servers:', error);
       }
     };

     const columns = [
       { field: 'name', headerName: 'Name', width: 200 },
       { 
         field: 'status', 
         headerName: 'Status', 
         width: 150,
         renderCell: (params) => (
           <Badge 
             variant={params.value === 'online' ? 'success' : 'error'}
           >
             {params.value === 'online' ? 'Online' : 'Offline'}
           </Badge>
         )
       },
       { field: 'url', headerName: 'URL', width: 250 },
       { field: 'type', headerName: 'Typ', width: 150 },
       {
         field: 'actions',
         headerName: 'Aktionen',
         width: 250,
         renderCell: (params) => (
           <Box display="flex" gap={1}>
             <Button 
               variant="primary" 
               size="small"
               disabled={params.row.status === 'online'}
               onClick={() => handleStartServer(params.row.id)}
             >
               Starten
             </Button>
             <Button 
               variant="secondary" 
               size="small"
               disabled={params.row.status === 'offline'}
               onClick={() => handleStopServer(params.row.id)}
             >
               Stoppen
             </Button>
             <Button 
               variant="info" 
               size="small"
               onClick={() => handleEditServer(params.row)}
             >
               Bearbeiten
             </Button>
           </Box>
         )
       }
     ];

     return (
       <Box>
         <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
           <Typography variant="h4">MCP-Server</Typography>
           <Button variant="primary" onClick={handleAddServer}>
             Server hinzufügen
           </Button>
         </Box>
         
         <DataGrid
           rows={servers}
           columns={columns}
           loading={loading}
           pageSize={10}
         />

         <Modal
           open={modalOpen}
           onClose={() => setModalOpen(false)}
           title={selectedServer ? 'Server bearbeiten' : 'Server hinzufügen'}
         >
           <Box p={3}>
             <Box mb={3}>
               <Input
                 label="Name"
                 value={formData.name}
                 onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                 fullWidth
                 required
               />
             </Box>

             <Box mb={3}>
               <Input
                 label="URL"
                 value={formData.url}
                 onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                 fullWidth
                 required
               />
             </Box>

             <Box mb={3}>
               <Input
                 label="Beschreibung"
                 value={formData.description}
                 onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                 fullWidth
               />
             </Box>

             <Box mb={4}>
               <Select
                 label="Typ"
                 value={formData.type}
                 onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                 fullWidth
                 required
               >
                 <option value="standard">Standard</option>
                 <option value="aws">AWS</option>
                 <option value="firebase">Firebase</option>
                 <option value="salesforce">Salesforce</option>
               </Select>
             </Box>

             <Box display="flex" justifyContent="flex-end" gap={2}>
               <Button variant="secondary" onClick={() => setModalOpen(false)}>
                 Abbrechen
               </Button>
               <Button variant="primary" onClick={handleSaveServer}>
                 Speichern
               </Button>
             </Box>
           </Box>
         </Modal>
       </Box>
     );
   }
   ```

2. **Implementierung der Server-Details**

   ```tsx
   // src/pages/MCPServerDetails.tsx
   import { useState, useEffect } from 'react';
   import { useParams } from 'react-router-dom';
   import {
     Box,
     Typography,
     Card,
     Tabs,
     Tab,
     Table,
     Badge,
     Button,
   } from '@ecosphere/smolitux-ui';
   import { apiClient } from '../api/client';

   export function MCPServerDetails() {
     const { id } = useParams();
     const [server, setServer] = useState(null);
     const [loading, setLoading] = useState(true);
     const [activeTab, setActiveTab] = useState('info');
     const [functions, setFunctions] = useState([]);
     const [logs, setLogs] = useState([]);

     useEffect(() => {
       fetchServer();
     }, [id]);

     const fetchServer = async () => {
       try {
         setLoading(true);
         const response = await apiClient.get(`/mcp-servers/${id}`);
         setServer(response.data);

         if (activeTab === 'functions') {
           fetchFunctions();
         } else if (activeTab === 'logs') {
           fetchLogs();
         }
       } catch (error) {
         console.error('Fehler beim Laden des Servers:', error);
       } finally {
         setLoading(false);
       }
     };

     const fetchFunctions = async () => {
       try {
         const response = await apiClient.get(`/mcp-servers/${id}/functions`);
         setFunctions(response.data);
       } catch (error) {
         console.error('Fehler beim Laden der Funktionen:', error);
       }
     };

     const fetchLogs = async () => {
       try {
         const response = await apiClient.get(`/mcp-servers/${id}/logs`);
         setLogs(response.data);
       } catch (error) {
         console.error('Fehler beim Laden der Logs:', error);
       }
     };

     const handleTabChange = (tab) => {
       setActiveTab(tab);
       if (tab === 'functions') {
         fetchFunctions();
       } else if (tab === 'logs') {
         fetchLogs();
       }
     };

     if (loading || !server) {
       return <Box p={3}>Laden...</Box>;
     }

     return (
       <Box>
         <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
           <Typography variant="h4">{server.name}</Typography>
           <Badge 
             variant={server.status === 'online' ? 'success' : 'error'}
             size="lg"
           >
             {server.status === 'online' ? 'Online' : 'Offline'}
           </Badge>
         </Box>

         <Card mb={4}>
           <Box p={3}>
             <Typography variant="h6" mb={2}>Server-Informationen</Typography>
             <Box display="grid" gridTemplateColumns="1fr 1fr" gap={3}>
               <Box>
                 <Typography variant="caption">URL</Typography>
                 <Typography variant="body1">{server.url}</Typography>
               </Box>
               <Box>
                 <Typography variant="caption">Typ</Typography>
                 <Typography variant="body1">{server.type}</Typography>
               </Box>
               <Box>
                 <Typography variant="caption">Beschreibung</Typography>
                 <Typography variant="body1">{server.description || '-'}</Typography>
               </Box>
               <Box>
                 <Typography variant="caption">Letzte Aktualisierung</Typography>
                 <Typography variant="body1">
                   {new Date(server.lastUpdated).toLocaleString()}
                 </Typography>
               </Box>
             </Box>
           </Box>
         </Card>

         <Tabs value={activeTab} onChange={handleTabChange}>
           <Tab value="info" label="Informationen" />
           <Tab value="functions" label="Funktionen" />
           <Tab value="logs" label="Logs" />
         </Tabs>

         <Box mt={3}>
           {activeTab === 'info' && (
             <Card>
               <Box p={3}>
                 <Typography variant="h6" mb={2}>Aktionen</Typography>
                 <Box display="flex" gap={2}>
                   <Button 
                     variant="primary"
                     disabled={server.status === 'online'}
                     onClick={() => {/* Starte Server */}}
                   >
                     Server starten
                   </Button>
                   <Button 
                     variant="secondary"
                     disabled={server.status === 'offline'}
                     onClick={() => {/* Stoppe Server */}}
                   >
                     Server stoppen
                   </Button>
                   <Button 
                     variant="info"
                     onClick={() => {/* Teste Verbindung */}}
                   >
                     Verbindung testen
                   </Button>
                 </Box>
               </Box>
             </Card>
           )}

           {activeTab === 'functions' && (
             <Card>
               <Table>
                 <Table.Header>
                   <Table.Row>
                     <Table.HeaderCell>Name</Table.HeaderCell>
                     <Table.HeaderCell>Beschreibung</Table.HeaderCell>
                     <Table.HeaderCell>Parameter</Table.HeaderCell>
                   </Table.Row>
                 </Table.Header>
                 <Table.Body>
                   {functions.map((func) => (
                     <Table.Row key={func.name}>
                       <Table.Cell>{func.name}</Table.Cell>
                       <Table.Cell>{func.description}</Table.Cell>
                       <Table.Cell>
                         {func.parameters.map((param) => param.name).join(', ')}
                       </Table.Cell>
                     </Table.Row>
                   ))}
                 </Table.Body>
               </Table>
             </Card>
           )}

           {activeTab === 'logs' && (
             <Card>
               <Table>
                 <Table.Header>
                   <Table.Row>
                     <Table.HeaderCell>Zeitstempel</Table.HeaderCell>
                     <Table.HeaderCell>Level</Table.HeaderCell>
                     <Table.HeaderCell>Nachricht</Table.HeaderCell>
                   </Table.Row>
                 </Table.Header>
                 <Table.Body>
                   {logs.map((log, index) => (
                     <Table.Row key={index}>
                       <Table.Cell>{new Date(log.timestamp).toLocaleString()}</Table.Cell>
                       <Table.Cell>
                         <Badge 
                           variant={
                             log.level === 'error' ? 'error' :
                             log.level === 'warning' ? 'warning' :
                             log.level === 'info' ? 'info' : 'default'
                           }
                         >
                           {log.level}
                         </Badge>
                       </Table.Cell>
                       <Table.Cell>{log.message}</Table.Cell>
                     </Table.Row>
                   ))}
                 </Table.Body>
               </Table>
             </Card>
           )}
         </Box>
       </Box>
     );
   }
   ```

#### Tag 5-7: Workflow-Verwaltung und Benutzer-Verwaltung

1. **Implementierung der Workflow-Liste**

   ```tsx
   // src/pages/Workflows.tsx
   import { useState, useEffect } from 'react';
   import {
     Box,
     Typography,
     DataGrid,
     Button,
     Badge,
     Modal,
     Input,
     Select,
   } from '@ecosphere/smolitux-ui';
   import { apiClient } from '../api/client';

   export function Workflows() {
     const [workflows, setWorkflows] = useState([]);
     const [loading, setLoading] = useState(true);
     const [modalOpen, setModalOpen] = useState(false);
     const [selectedWorkflow, setSelectedWorkflow] = useState(null);
     const [formData, setFormData] = useState({
       name: '',
       description: '',
       active: true,
     });

     useEffect(() => {
       fetchWorkflows();
     }, []);

     const fetchWorkflows = async () => {
       try {
         setLoading(true);
         const response = await apiClient.get('/workflows');
         setWorkflows(response.data);
       } catch (error) {
         console.error('Fehler beim Laden der Workflows:', error);
       } finally {
         setLoading(false);
       }
     };

     const handleRunWorkflow = async (id) => {
       try {
         await apiClient.post(`/workflows/${id}/run`);
         fetchWorkflows();
       } catch (error) {
         console.error('Fehler beim Ausführen des Workflows:', error);
       }
     };

     const handleAddWorkflow = () => {
       setSelectedWorkflow(null);
       setFormData({
         name: '',
         description: '',
         active: true,
       });
       setModalOpen(true);
     };

     const handleEditWorkflow = (workflow) => {
       setSelectedWorkflow(workflow);
       setFormData({
         name: workflow.name,
         description: workflow.description || '',
         active: workflow.active,
       });
       setModalOpen(true);
     };

     const handleSaveWorkflow = async () => {
       try {
         if (selectedWorkflow) {
           await apiClient.put(`/workflows/${selectedWorkflow.id}`, formData);
         } else {
           await apiClient.post('/workflows', formData);
         }
         setModalOpen(false);
         fetchWorkflows();
       } catch (error) {
         console.error('Fehler beim Speichern des Workflows:', error);
       }
     };

     const columns = [
       { field: 'name', headerName: 'Name', width: 200 },
       { 
         field: 'active', 
         headerName: 'Status', 
         width: 150,
         renderCell: (params) => (
           <Badge 
             variant={params.value ? 'success' : 'warning'}
           >
             {params.value ? 'Aktiv' : 'Inaktiv'}
           </Badge>
         )
       },
       { field: 'description', headerName: 'Beschreibung', width: 300 },
       { field: 'lastRun', headerName: 'Letzte Ausführung', width: 200 },
       {
         field: 'actions',
         headerName: 'Aktionen',
         width: 250,
         renderCell: (params) => (
           <Box display="flex" gap={1}>
             <Button 
               variant="primary" 
               size="small"
               onClick={() => handleRunWorkflow(params.row.id)}
             >
               Ausführen
             </Button>
             <Button 
               variant="info" 
               size="small"
               onClick={() => handleEditWorkflow(params.row)}
             >
               Bearbeiten
             </Button>
           </Box>
         )
       }
     ];

     return (
       <Box>
         <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
           <Typography variant="h4">Workflows</Typography>
           <Button variant="primary" onClick={handleAddWorkflow}>
             Workflow hinzufügen
           </Button>
         </Box>
         
         <DataGrid
           rows={workflows}
           columns={columns}
           loading={loading}
           pageSize={10}
         />

         <Modal
           open={modalOpen}
           onClose={() => setModalOpen(false)}
           title={selectedWorkflow ? 'Workflow bearbeiten' : 'Workflow hinzufügen'}
         >
           <Box p={3}>
             <Box mb={3}>
               <Input
                 label="Name"
                 value={formData.name}
                 onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                 fullWidth
                 required
               />
             </Box>

             <Box mb={3}>
               <Input
                 label="Beschreibung"
                 value={formData.description}
                 onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                 fullWidth
               />
             </Box>

             <Box mb={4}>
               <Select
                 label="Status"
                 value={formData.active ? 'active' : 'inactive'}
                 onChange={(e) => setFormData({ ...formData, active: e.target.value === 'active' })}
                 fullWidth
                 required
               >
                 <option value="active">Aktiv</option>
                 <option value="inactive">Inaktiv</option>
               </Select>
             </Box>

             <Box display="flex" justifyContent="flex-end" gap={2}>
               <Button variant="secondary" onClick={() => setModalOpen(false)}>
                 Abbrechen
               </Button>
               <Button variant="primary" onClick={handleSaveWorkflow}>
                 Speichern
               </Button>
             </Box>
           </Box>
         </Modal>
       </Box>
     );
   }
   ```

2. **Implementierung der Benutzer-Verwaltung**

   ```tsx
   // src/pages/Users.tsx
   import { useState, useEffect } from 'react';
   import {
     Box,
     Typography,
     DataGrid,
     Button,
     Badge,
     Modal,
     Input,
     Select,
   } from '@ecosphere/smolitux-ui';
   import { apiClient } from '../api/client';

   export function Users() {
     const [users, setUsers] = useState([]);
     const [roles, setRoles] = useState([]);
     const [loading, setLoading] = useState(true);
     const [modalOpen, setModalOpen] = useState(false);
     const [selectedUser, setSelectedUser] = useState(null);
     const [formData, setFormData] = useState({
       username: '',
       email: '',
       fullName: '',
       roles: [],
       password: '',
     });

     useEffect(() => {
       fetchUsers();
       fetchRoles();
     }, []);

     const fetchUsers = async () => {
       try {
         setLoading(true);
         const response = await apiClient.get('/users');
         setUsers(response.data);
       } catch (error) {
         console.error('Fehler beim Laden der Benutzer:', error);
       } finally {
         setLoading(false);
       }
     };

     const fetchRoles = async () => {
       try {
         const response = await apiClient.get('/roles');
         setRoles(response.data);
       } catch (error) {
         console.error('Fehler beim Laden der Rollen:', error);
       }
     };

     const handleAddUser = () => {
       setSelectedUser(null);
       setFormData({
         username: '',
         email: '',
         fullName: '',
         roles: [],
         password: '',
       });
       setModalOpen(true);
     };

     const handleEditUser = (user) => {
       setSelectedUser(user);
       setFormData({
         username: user.username,
         email: user.email || '',
         fullName: user.fullName || '',
         roles: user.roles || [],
         password: '',
       });
       setModalOpen(true);
     };

     const handleSaveUser = async () => {
       try {
         if (selectedUser) {
           await apiClient.put(`/users/${selectedUser.id}`, formData);
         } else {
           await apiClient.post('/users', formData);
         }
         setModalOpen(false);
         fetchUsers();
       } catch (error) {
         console.error('Fehler beim Speichern des Benutzers:', error);
       }
     };

     const columns = [
       { field: 'username', headerName: 'Benutzername', width: 200 },
       { field: 'email', headerName: 'E-Mail', width: 250 },
       { field: 'fullName', headerName: 'Name', width: 200 },
       { 
         field: 'roles', 
         headerName: 'Rollen', 
         width: 250,
         renderCell: (params) => (
           <Box display="flex" gap={1}>
             {params.value.map((role) => (
               <Badge key={role} variant="info">{role}</Badge>
             ))}
           </Box>
         )
       },
       {
         field: 'actions',
         headerName: 'Aktionen',
         width: 150,
         renderCell: (params) => (
           <Box display="flex" gap={1}>
             <Button 
               variant="info" 
               size="small"
               onClick={() => handleEditUser(params.row)}
             >
               Bearbeiten
             </Button>
           </Box>
         )
       }
     ];

     return (
       <Box>
         <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
           <Typography variant="h4">Benutzer</Typography>
           <Button variant="primary" onClick={handleAddUser}>
             Benutzer hinzufügen
           </Button>
         </Box>
         
         <DataGrid
           rows={users}
           columns={columns}
           loading={loading}
           pageSize={10}
         />

         <Modal
           open={modalOpen}
           onClose={() => setModalOpen(false)}
           title={selectedUser ? 'Benutzer bearbeiten' : 'Benutzer hinzufügen'}
         >
           <Box p={3}>
             <Box mb={3}>
               <Input
                 label="Benutzername"
                 value={formData.username}
                 onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                 fullWidth
                 required
                 disabled={!!selectedUser}
               />
             </Box>

             <Box mb={3}>
               <Input
                 label="E-Mail"
                 type="email"
                 value={formData.email}
                 onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                 fullWidth
                 required
               />
             </Box>

             <Box mb={3}>
               <Input
                 label="Name"
                 value={formData.fullName}
                 onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                 fullWidth
               />
             </Box>

             <Box mb={3}>
               <Select
                 label="Rollen"
                 value={formData.roles}
                 onChange={(e) => {
                   const options = e.target.options;
                   const selectedRoles = [];
                   for (let i = 0; i < options.length; i++) {
                     if (options[i].selected) {
                       selectedRoles.push(options[i].value);
                     }
                   }
                   setFormData({ ...formData, roles: selectedRoles });
                 }}
                 fullWidth
                 multiple
                 required
               >
                 {roles.map((role) => (
                   <option key={role.name} value={role.name}>{role.name}</option>
                 ))}
               </Select>
             </Box>

             {!selectedUser && (
               <Box mb={4}>
                 <Input
                   label="Passwort"
                   type="password"
                   value={formData.password}
                   onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                   fullWidth
                   required
                 />
               </Box>
             )}

             <Box display="flex" justifyContent="flex-end" gap={2}>
               <Button variant="secondary" onClick={() => setModalOpen(false)}>
                 Abbrechen
               </Button>
               <Button variant="primary" onClick={handleSaveUser}>
                 Speichern
               </Button>
             </Box>
           </Box>
         </Modal>
       </Box>
     );
   }
   ```

### Woche 3: Integration und Tests

#### Tag 1-2: Integration mit Backend

1. **Implementierung der API-Hooks**

   ```tsx
   // src/hooks/useApi.ts
   import { useState, useEffect } from 'react';
   import { apiClient } from '../api/client';

   export function useApi<T>(url: string, options: any = {}) {
     const [data, setData] = useState<T | null>(null);
     const [loading, setLoading] = useState(true);
     const [error, setError] = useState<Error | null>(null);
     const [refetchIndex, setRefetchIndex] = useState(0);

     const refetch = () => setRefetchIndex((prev) => prev + 1);

     useEffect(() => {
       const fetchData = async () => {
         try {
           setLoading(true);
           setError(null);
           const response = await apiClient.get(url, options);
           setData(response.data);
         } catch (err) {
           setError(err as Error);
         } finally {
           setLoading(false);
         }
       };

       fetchData();
     }, [url, refetchIndex]);

     return { data, loading, error, refetch };
   }

   export function useApiMutation<T, R>(
     url: string,
     method: 'post' | 'put' | 'delete' = 'post',
     options: any = {}
   ) {
     const [data, setData] = useState<R | null>(null);
     const [loading, setLoading] = useState(false);
     const [error, setError] = useState<Error | null>(null);

     const mutate = async (payload: T) => {
       try {
         setLoading(true);
         setError(null);
         const response = await apiClient[method](url, payload, options);
         setData(response.data);
         return response.data;
       } catch (err) {
         setError(err as Error);
         throw err;
       } finally {
         setLoading(false);
       }
     };

     return { mutate, data, loading, error };
   }
   ```

2. **Implementierung der WebSocket-Integration**

   ```tsx
   // src/api/websocket.ts
   import { useEffect, useState, useRef } from 'react';

   export function useWebSocket<T>(url: string) {
     const [data, setData] = useState<T | null>(null);
     const [isConnected, setIsConnected] = useState(false);
     const [error, setError] = useState<Error | null>(null);
     const wsRef = useRef<WebSocket | null>(null);

     useEffect(() => {
       const token = localStorage.getItem('token');
       const wsUrl = `${url}${token ? `?token=${token}` : ''}`;
       const ws = new WebSocket(wsUrl);

       ws.onopen = () => {
         setIsConnected(true);
         setError(null);
       };

       ws.onmessage = (event) => {
         try {
           const parsedData = JSON.parse(event.data);
           setData(parsedData);
         } catch (err) {
           setError(new Error('Failed to parse WebSocket message'));
         }
       };

       ws.onerror = (event) => {
         setError(new Error('WebSocket error'));
         setIsConnected(false);
       };

       ws.onclose = () => {
         setIsConnected(false);
       };

       wsRef.current = ws;

       return () => {
         ws.close();
       };
     }, [url]);

     const send = (data: any) => {
       if (wsRef.current && isConnected) {
         wsRef.current.send(JSON.stringify(data));
       }
     };

     return { data, isConnected, error, send };
   }
   ```

3. **Implementierung der Authentifizierung und Autorisierung**

   ```tsx
   // src/contexts/AuthContext.tsx
   import { createContext, useContext, useEffect, useState } from 'react';
   import { useNavigate } from 'react-router-dom';
   import { apiClient } from '../api/client';

   interface AuthContextType {
     user: any | null;
     isAuthenticated: boolean;
     login: (username: string, password: string) => Promise<void>;
     logout: () => void;
     hasPermission: (permission: string) => boolean;
   }

   const AuthContext = createContext<AuthContextType | null>(null);

   export function AuthProvider({ children }: { children: React.ReactNode }) {
     const [user, setUser] = useState<any | null>(null);
     const [isAuthenticated, setIsAuthenticated] = useState(false);
     const [loading, setLoading] = useState(true);
     const navigate = useNavigate();

     useEffect(() => {
       const token = localStorage.getItem('token');
       if (token) {
         validateToken(token);
       } else {
         setLoading(false);
       }
     }, []);

     const validateToken = async (token: string) => {
       try {
         const response = await apiClient.get('/auth/validate', {
           headers: { Authorization: `Bearer ${token}` }
         });
         setUser(response.data.user);
         setIsAuthenticated(true);
       } catch (error) {
         localStorage.removeItem('token');
       } finally {
         setLoading(false);
       }
     };

     const login = async (username: string, password: string) => {
       const response = await apiClient.post('/auth/login', { username, password });
       const { token, user } = response.data;
       localStorage.setItem('token', token);
       setUser(user);
       setIsAuthenticated(true);
     };

     const logout = () => {
       localStorage.removeItem('token');
       setUser(null);
       setIsAuthenticated(false);
       navigate('/login');
     };

     const hasPermission = (permission: string) => {
       if (!user || !user.permissions) return false;
       return user.permissions.includes(permission);
     };

     if (loading) {
       return <div>Loading...</div>;
     }

     return (
       <AuthContext.Provider value={{ user, isAuthenticated, login, logout, hasPermission }}>
         {children}
       </AuthContext.Provider>
     );
   }

   export function useAuth() {
     const context = useContext(AuthContext);
     if (!context) {
       throw new Error('useAuth must be used within an AuthProvider');
     }
     return context;
   }
   ```

#### Tag 3-5: Tests und Optimierung

1. **Implementierung von Unit-Tests**

   ```tsx
   // src/components/common/Button.test.tsx
   import { render, screen, fireEvent } from '@testing-library/react';
   import { Button } from '@ecosphere/smolitux-ui';
   import { ThemeProvider } from '@ecosphere/smolitux-ui';
   import { theme } from '../../theme';

   describe('Button Component', () => {
     it('renders correctly', () => {
       render(
         <ThemeProvider theme={theme}>
           <Button variant="primary">Test Button</Button>
         </ThemeProvider>
       );
       
       expect(screen.getByText('Test Button')).toBeInTheDocument();
     });

     it('handles click events', () => {
       const handleClick = jest.fn();
       
       render(
         <ThemeProvider theme={theme}>
           <Button variant="primary" onClick={handleClick}>Click Me</Button>
         </ThemeProvider>
       );
       
       fireEvent.click(screen.getByText('Click Me'));
       expect(handleClick).toHaveBeenCalledTimes(1);
     });

     it('is disabled when disabled prop is true', () => {
       render(
         <ThemeProvider theme={theme}>
           <Button variant="primary" disabled>Disabled Button</Button>
         </ThemeProvider>
       );
       
       expect(screen.getByText('Disabled Button')).toBeDisabled();
     });
   });
   ```

2. **Implementierung von Integrationstests**

   ```tsx
   // src/pages/Login.test.tsx
   import { render, screen, fireEvent, waitFor } from '@testing-library/react';
   import { MemoryRouter } from 'react-router-dom';
   import { ThemeProvider } from '@ecosphere/smolitux-ui';
   import { theme } from '../theme';
   import { Login } from './Login';
   import { apiClient } from '../api/client';

   // Mock the API client
   jest.mock('../api/client', () => ({
     apiClient: {
       post: jest.fn(),
     },
   }));

   // Mock the auth store
   jest.mock('../store/auth', () => ({
     useAuthStore: () => ({
       login: jest.fn(),
     }),
   }));

   describe('Login Page', () => {
     beforeEach(() => {
       jest.clearAllMocks();
     });

     it('renders login form correctly', () => {
       render(
         <MemoryRouter>
           <ThemeProvider theme={theme}>
             <Login />
           </ThemeProvider>
         </MemoryRouter>
       );
       
       expect(screen.getByText('Anmelden')).toBeInTheDocument();
       expect(screen.getByLabelText('Benutzername')).toBeInTheDocument();
       expect(screen.getByLabelText('Passwort')).toBeInTheDocument();
       expect(screen.getByRole('button', { name: 'Anmelden' })).toBeInTheDocument();
     });

     it('submits the form with correct data', async () => {
       (apiClient.post as jest.Mock).mockResolvedValueOnce({
         data: { token: 'test-token', user: { username: 'testuser' } },
       });

       render(
         <MemoryRouter>
           <ThemeProvider theme={theme}>
             <Login />
           </ThemeProvider>
         </MemoryRouter>
       );
       
       fireEvent.change(screen.getByLabelText('Benutzername'), {
         target: { value: 'testuser' },
       });
       
       fireEvent.change(screen.getByLabelText('Passwort'), {
         target: { value: 'password123' },
       });
       
       fireEvent.click(screen.getByRole('button', { name: 'Anmelden' }));
       
       await waitFor(() => {
         expect(apiClient.post).toHaveBeenCalledWith('/auth/login', {
           username: 'testuser',
           password: 'password123',
         });
       });
     });

     it('shows error message on login failure', async () => {
       (apiClient.post as jest.Mock).mockRejectedValueOnce({
         response: { data: { message: 'Ungültige Anmeldedaten' } },
       });

       render(
         <MemoryRouter>
           <ThemeProvider theme={theme}>
             <Login />
           </ThemeProvider>
         </MemoryRouter>
       );
       
       fireEvent.change(screen.getByLabelText('Benutzername'), {
         target: { value: 'testuser' },
       });
       
       fireEvent.change(screen.getByLabelText('Passwort'), {
         target: { value: 'wrongpassword' },
       });
       
       fireEvent.click(screen.getByRole('button', { name: 'Anmelden' }));
       
       await waitFor(() => {
         expect(screen.getByText('Ungültige Anmeldedaten')).toBeInTheDocument();
       });
     });
   });
   ```

3. **Leistungsoptimierung**

   ```tsx
   // src/components/dashboard/ServerStatus.tsx
   import { memo } from 'react';
   import { Badge } from '@ecosphere/smolitux-ui';

   interface ServerStatusProps {
     status: 'online' | 'offline';
   }

   // Memoize the component to prevent unnecessary re-renders
   export const ServerStatus = memo(({ status }: ServerStatusProps) => {
     return (
       <Badge 
         variant={status === 'online' ? 'success' : 'error'}
       >
         {status === 'online' ? 'Online' : 'Offline'}
       </Badge>
     );
   });
   ```

   ```tsx
   // src/hooks/useDebouncedValue.ts
   import { useState, useEffect } from 'react';

   export function useDebouncedValue<T>(value: T, delay: number): T {
     const [debouncedValue, setDebouncedValue] = useState(value);

     useEffect(() => {
       const handler = setTimeout(() => {
         setDebouncedValue(value);
       }, delay);

       return () => {
         clearTimeout(handler);
       };
     }, [value, delay]);

     return debouncedValue;
   }
   ```

#### Tag 6-7: Internationalisierung und Barrierefreiheit

1. **Implementierung der Internationalisierung**

   ```bash
   # Installation von i18next
   npm install i18next react-i18next i18next-browser-languagedetector
   ```

   ```tsx
   // src/i18n/index.ts
   import i18n from 'i18next';
   import { initReactI18next } from 'react-i18next';
   import LanguageDetector from 'i18next-browser-languagedetector';

   import translationDE from './locales/de/translation.json';
   import translationEN from './locales/en/translation.json';

   const resources = {
     de: {
       translation: translationDE,
     },
     en: {
       translation: translationEN,
     },
   };

   i18n
     .use(LanguageDetector)
     .use(initReactI18next)
     .init({
       resources,
       fallbackLng: 'de',
       interpolation: {
         escapeValue: false,
       },
     });

   export default i18n;
   ```

   ```json
   // src/i18n/locales/de/translation.json
   {
     "common": {
       "save": "Speichern",
       "cancel": "Abbrechen",
       "edit": "Bearbeiten",
       "delete": "Löschen",
       "add": "Hinzufügen",
       "search": "Suchen",
       "loading": "Laden..."
     },
     "auth": {
       "login": "Anmelden",
       "logout": "Abmelden",
       "username": "Benutzername",
       "password": "Passwort",
       "loginFailed": "Anmeldung fehlgeschlagen"
     },
     "dashboard": {
       "title": "Dashboard",
       "mcpServers": "MCP-Server",
       "workflows": "Workflows",
       "users": "Benutzer",
       "cpuUsage": "CPU-Auslastung"
     },
     "mcpServers": {
       "title": "MCP-Server",
       "addServer": "Server hinzufügen",
       "editServer": "Server bearbeiten",
       "name": "Name",
       "url": "URL",
       "status": "Status",
       "type": "Typ",
       "description": "Beschreibung",
       "actions": "Aktionen",
       "start": "Starten",
       "stop": "Stoppen",
       "online": "Online",
       "offline": "Offline"
     }
   }
   ```

   ```tsx
   // src/pages/Login.tsx (mit i18n)
   import { useState } from 'react';
   import { useNavigate } from 'react-router-dom';
   import { useTranslation } from 'react-i18next';
   import { Card, Box, Typography, Input, Button, Alert } from '@ecosphere/smolitux-ui';
   import { useAuthStore } from '../store/auth';
   import { apiClient } from '../api/client';

   export function Login() {
     const { t } = useTranslation();
     const [username, setUsername] = useState('');
     const [password, setPassword] = useState('');
     const [error, setError] = useState('');
     const [loading, setLoading] = useState(false);
     const navigate = useNavigate();
     const login = useAuthStore((state) => state.login);

     const handleLogin = async (e: React.FormEvent) => {
       e.preventDefault();
       setError('');
       setLoading(true);

       try {
         const response = await apiClient.post('/auth/login', { username, password });
         login(response.data.token, response.data.user);
         navigate('/');
       } catch (err: any) {
         setError(err.response?.data?.message || t('auth.loginFailed'));
       } finally {
         setLoading(false);
       }
     };

     return (
       <Box
         display="flex"
         justifyContent="center"
         alignItems="center"
         minHeight="100vh"
         bg="background.default"
       >
         <Card width="400px" p={4}>
           <Typography variant="h4" mb={3} textAlign="center">
             {t('auth.login')}
           </Typography>

           {error && (
             <Alert variant="error" mb={3}>
               {error}
             </Alert>
           )}

           <form onSubmit={handleLogin}>
             <Box mb={3}>
               <Input
                 label={t('auth.username')}
                 value={username}
                 onChange={(e) => setUsername(e.target.value)}
                 fullWidth
                 required
               />
             </Box>

             <Box mb={4}>
               <Input
                 label={t('auth.password')}
                 type="password"
                 value={password}
                 onChange={(e) => setPassword(e.target.value)}
                 fullWidth
                 required
               />
             </Box>

             <Button
               variant="primary"
               type="submit"
               fullWidth
               disabled={loading}
             >
               {loading ? t('common.loading') : t('auth.login')}
             </Button>
           </form>
         </Card>
       </Box>
     );
   }
   ```

2. **Implementierung der Barrierefreiheit**

   ```tsx
   // src/components/common/SkipLink.tsx
   import styled from 'styled-components';

   const StyledSkipLink = styled.a`
     position: absolute;
     top: -40px;
     left: 0;
     background: ${({ theme }) => theme.colors.primary.main};
     color: ${({ theme }) => theme.colors.primary.contrastText};
     padding: 8px;
     z-index: 100;
     transition: top 0.3s;

     &:focus {
       top: 0;
     }
   `;

   export function SkipLink() {
     return (
       <StyledSkipLink href="#main-content">
         Skip to main content
       </StyledSkipLink>
     );
   }
   ```

   ```tsx
   // src/layouts/MainLayout.tsx (mit Barrierefreiheit)
   import { useState } from 'react';
   import { Outlet, useNavigate } from 'react-router-dom';
   import { useTranslation } from 'react-i18next';
   import {
     Box,
     Navbar,
     Sidebar,
     SidebarItem,
     Icon,
     Avatar,
     Dropdown,
     DropdownItem,
   } from '@ecosphere/smolitux-ui';
   import { useAuthStore } from '../store/auth';
   import { SkipLink } from '../components/common/SkipLink';

   export function MainLayout() {
     const { t } = useTranslation();
     const [sidebarOpen, setSidebarOpen] = useState(true);
     const navigate = useNavigate();
     const { user, logout } = useAuthStore();

     const handleLogout = () => {
       logout();
       navigate('/login');
     };

     return (
       <>
         <SkipLink />
         <Box display="flex" height="100vh">
           <Sidebar 
             open={sidebarOpen} 
             onToggle={() => setSidebarOpen(!sidebarOpen)}
             aria-label={t('common.navigation')}
           >
             <SidebarItem
               icon={<Icon name="dashboard" />}
               label={t('dashboard.title')}
               onClick={() => navigate('/')}
               aria-current={location.pathname === '/' ? 'page' : undefined}
             />
             <SidebarItem
               icon={<Icon name="server" />}
               label={t('mcpServers.title')}
               onClick={() => navigate('/mcp-servers')}
               aria-current={location.pathname === '/mcp-servers' ? 'page' : undefined}
             />
             {/* Weitere Menüpunkte... */}
           </Sidebar>

           <Box display="flex" flexDirection="column" flex={1} overflow="hidden">
             <Navbar>
               <Box ml="auto">
                 <Dropdown
                   trigger={
                     <Avatar
                       name={user?.name || t('common.user')}
                       src={user?.avatar}
                       size="sm"
                       aria-label={t('common.userMenu')}
                     />
                   }
                 >
                   <DropdownItem onClick={() => navigate('/profile')}>
                     {t('common.profile')}
                   </DropdownItem>
                   <DropdownItem onClick={handleLogout}>
                     {t('auth.logout')}
                   </DropdownItem>
                 </Dropdown>
               </Box>
             </Navbar>

             <Box 
               flex={1} 
               p={3} 
               overflow="auto"
               id="main-content"
               role="main"
               tabIndex={-1}
             >
               <Outlet />
             </Box>
           </Box>
         </Box>
       </>
     );
   }
   ```

## Zusammenfassung

Diese detaillierte Schritt-für-Schritt-Anleitung beschreibt die Implementierung der Web-Benutzeroberfläche mit der smolitux-ui-Bibliothek im Rahmen von Phase 6 des Verbesserungsplans. Die Anleitung umfasst alle Aspekte der Entwicklung, von der Einrichtung des Projekts über die Implementierung der Hauptkomponenten bis hin zur Integration mit dem Backend und der Optimierung der Anwendung.

Die Web-Benutzeroberfläche bietet eine intuitive und benutzerfreundliche Schnittstelle für die Verwaltung und Überwachung des Dev-Server-Workflow-Systems und nutzt dabei die Vorteile der smolitux-ui-Bibliothek für ein konsistentes Design und eine verbesserte Benutzererfahrung.