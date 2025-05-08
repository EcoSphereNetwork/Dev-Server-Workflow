// src/config/services.ts

export interface Service {
  id: string;
  name: string;
  url: string;
  description: string;
  icon: string;
  category: 'development' | 'productivity' | 'management' | 'monitoring' | 'infrastructure' | 'other';
}

const services: Service[] = [
  // Entwicklungstools
  {
    id: 'n8n',
    name: 'n8n',
    url: 'https://n8n.ecospherenet.work',
    description: 'Workflow-Automatisierung für Entwickler',
    icon: '🔄',
    category: 'development'
  },
  {
    id: 'gitlab',
    name: 'GitLab',
    url: 'https://gitlab.ecospherenet.work',
    description: 'Git-Repository-Manager',
    icon: '🦊',
    category: 'development'
  },
  {
    id: 'dev-server',
    name: 'Dev-Server',
    url: 'https://dev-server.ecospherenet.work',
    description: 'Entwicklungsserver-Dashboard',
    icon: '🖥️',
    category: 'development'
  },
  
  // Produktivitätstools
  {
    id: 'appflowy',
    name: 'AppFlowy',
    url: 'https://appflowy.ecospherenet.work',
    description: 'Open-Source Alternative zu Notion',
    icon: '📝',
    category: 'productivity'
  },
  {
    id: 'affine',
    name: 'Affine',
    url: 'https://affine.ecospherenet.work',
    description: 'Kollaborative Wissensplattform',
    icon: '✨',
    category: 'productivity'
  },
  
  // Management-Tools
  {
    id: 'openproject',
    name: 'OpenProject',
    url: 'https://openproject.ecospherenet.work',
    description: 'Projektmanagement-Software',
    icon: '📊',
    category: 'management'
  },
  
  // Monitoring-Tools
  {
    id: 'monitoring',
    name: 'Monitoring',
    url: 'https://monitoring.ecospherenet.work',
    description: 'System-Monitoring mit Grafana und Prometheus',
    icon: '📈',
    category: 'monitoring'
  },
  {
    id: 'prometheus',
    name: 'Prometheus',
    url: 'https://monitoring.ecospherenet.work/prometheus/',
    description: 'Metriken-Sammlung und -Speicherung',
    icon: '📊',
    category: 'monitoring'
  },
  {
    id: 'alertmanager',
    name: 'Alertmanager',
    url: 'https://monitoring.ecospherenet.work/alertmanager/',
    description: 'Benachrichtigungen und Alarme',
    icon: '🔔',
    category: 'monitoring'
  },
  
  // Infrastruktur-Tools
  {
    id: 'docker',
    name: 'Docker',
    url: 'https://docker.ecospherenet.work',
    description: 'Docker-Container-Verwaltung mit Portainer',
    icon: '🐳',
    category: 'infrastructure'
  },
  {
    id: 'mcp',
    name: 'MCP-Server',
    url: 'https://mcp.ecospherenet.work',
    description: 'Verwaltung der MCP-Server',
    icon: '🔌',
    category: 'infrastructure'
  },
  
  // Sonstige Tools
  {
    id: 'api',
    name: 'API-Docs',
    url: 'https://api.ecospherenet.work',
    description: 'API-Dokumentation und -Tests',
    icon: '📚',
    category: 'other'
  },
  {
    id: 'auth',
    name: 'Auth',
    url: 'https://auth.ecospherenet.work',
    description: 'Authentifizierung und Autorisierung',
    icon: '🔐',
    category: 'other'
  }
];

export default services;