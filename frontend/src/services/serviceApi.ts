/**
 * Service-API
 * 
 * API-Funktionen für die Verwaltung von Diensten.
 */

import { Service, ServiceLog } from '../types/services';

// Mock-Dienste
const mockServices: Service[] = [
  {
    id: '1',
    name: 'n8n',
    description: 'Workflow-Automatisierung für Entwickler',
    type: 'Workflow-Automation',
    url: 'https://n8n.ecospherenet.work',
    logo: 'https://n8n.io/favicon.ico',
    status: 'running',
    version: '0.214.0',
    resources: {
      cpu: 15,
      memory: 25,
      disk: 10,
    },
    ports: [
      {
        internal: 5678,
        external: 5678,
        protocol: 'tcp',
      },
    ],
    dependencies: ['postgres'],
  },
  {
    id: '2',
    name: 'AppFlowy',
    description: 'Open-Source-Alternative zu Notion',
    type: 'Notizen',
    url: 'https://appflowy.ecospherenet.work',
    logo: 'https://appflowy.io/favicon.ico',
    status: 'running',
    version: '0.1.0',
    resources: {
      cpu: 5,
      memory: 15,
      disk: 5,
    },
  },
  {
    id: '3',
    name: 'OpenProject',
    description: 'Open-Source-Projektmanagement-Software',
    type: 'Projektmanagement',
    url: 'https://openproject.ecospherenet.work',
    logo: 'https://www.openproject.org/favicon.ico',
    status: 'stopped',
    version: '12.2.0',
    resources: {
      cpu: 0,
      memory: 0,
      disk: 20,
    },
    dependencies: ['postgres', 'redis'],
  },
  {
    id: '4',
    name: 'GitLab',
    description: 'Git-Repository-Manager',
    type: 'Git-Repository',
    url: 'https://gitlab.ecospherenet.work',
    logo: 'https://gitlab.com/favicon.ico',
    status: 'running',
    version: '15.4.0',
    resources: {
      cpu: 25,
      memory: 40,
      disk: 35,
    },
    dependencies: ['postgres', 'redis'],
  },
  {
    id: '5',
    name: 'Affine',
    description: 'Kollaboratives Whiteboard und Dokumenteneditor',
    type: 'Whiteboard',
    url: 'https://affine.ecospherenet.work',
    logo: 'https://affine.pro/favicon.ico',
    status: 'error',
    version: '0.5.0',
    resources: {
      cpu: 0,
      memory: 0,
      disk: 8,
    },
  },
];

// Mock-Logs
const generateMockLogs = (serviceId: string): ServiceLog[] => {
  const logs: ServiceLog[] = [];
  const now = new Date();
  
  // Generiere 20 zufällige Logs
  for (let i = 0; i < 20; i++) {
    const timestamp = new Date(now.getTime() - i * 60000); // Jede Minute ein Log
    const level = ['info', 'warning', 'error', 'debug'][Math.floor(Math.random() * 4)] as 'info' | 'warning' | 'error' | 'debug';
    
    let message = '';
    switch (level) {
      case 'info':
        message = 'Dienst läuft normal';
        break;
      case 'warning':
        message = 'Hohe Ressourcennutzung erkannt';
        break;
      case 'error':
        message = 'Fehler beim Verbinden mit der Datenbank';
        break;
      case 'debug':
        message = 'Verarbeite Anfrage: GET /api/v1/users';
        break;
    }
    
    logs.push({
      id: `${serviceId}-log-${i}`,
      message,
      timestamp: timestamp.toISOString(),
      level,
      source: 'system',
    });
  }
  
  return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
};

// API-Funktionen

/**
 * Hole alle Dienste
 */
export const getServices = async (): Promise<Service[]> => {
  // Simuliere API-Aufruf
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(mockServices);
    }, 500);
  });
};

/**
 * Hole einen Dienst anhand seiner ID
 */
export const getService = async (id: string): Promise<Service> => {
  // Simuliere API-Aufruf
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const service = mockServices.find((s) => s.id === id);
      if (service) {
        resolve(service);
      } else {
        reject(new Error('Dienst nicht gefunden'));
      }
    }, 500);
  });
};

/**
 * Starte einen Dienst
 */
export const startService = async (id: string): Promise<Service> => {
  // Simuliere API-Aufruf
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const serviceIndex = mockServices.findIndex((s) => s.id === id);
      if (serviceIndex !== -1) {
        mockServices[serviceIndex] = {
          ...mockServices[serviceIndex],
          status: 'running',
        };
        resolve(mockServices[serviceIndex]);
      } else {
        reject(new Error('Dienst nicht gefunden'));
      }
    }, 1000);
  });
};

/**
 * Stoppe einen Dienst
 */
export const stopService = async (id: string): Promise<Service> => {
  // Simuliere API-Aufruf
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const serviceIndex = mockServices.findIndex((s) => s.id === id);
      if (serviceIndex !== -1) {
        mockServices[serviceIndex] = {
          ...mockServices[serviceIndex],
          status: 'stopped',
        };
        resolve(mockServices[serviceIndex]);
      } else {
        reject(new Error('Dienst nicht gefunden'));
      }
    }, 1000);
  });
};

/**
 * Starte einen Dienst neu
 */
export const restartService = async (id: string): Promise<Service> => {
  // Simuliere API-Aufruf
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const serviceIndex = mockServices.findIndex((s) => s.id === id);
      if (serviceIndex !== -1) {
        // Erst stoppen
        mockServices[serviceIndex] = {
          ...mockServices[serviceIndex],
          status: 'stopped',
        };
        
        // Dann nach einer Verzögerung starten
        setTimeout(() => {
          mockServices[serviceIndex] = {
            ...mockServices[serviceIndex],
            status: 'running',
          };
          resolve(mockServices[serviceIndex]);
        }, 1000);
      } else {
        reject(new Error('Dienst nicht gefunden'));
      }
    }, 500);
  });
};

/**
 * Aktualisiere einen Dienst
 */
export const updateService = async (service: Service): Promise<Service> => {
  // Simuliere API-Aufruf
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const serviceIndex = mockServices.findIndex((s) => s.id === service.id);
      if (serviceIndex !== -1) {
        mockServices[serviceIndex] = {
          ...mockServices[serviceIndex],
          ...service,
        };
        resolve(mockServices[serviceIndex]);
      } else {
        reject(new Error('Dienst nicht gefunden'));
      }
    }, 1000);
  });
};

/**
 * Lösche einen Dienst
 */
export const deleteService = async (id: string): Promise<void> => {
  // Simuliere API-Aufruf
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const serviceIndex = mockServices.findIndex((s) => s.id === id);
      if (serviceIndex !== -1) {
        mockServices.splice(serviceIndex, 1);
        resolve();
      } else {
        reject(new Error('Dienst nicht gefunden'));
      }
    }, 1000);
  });
};

/**
 * Hole die Logs eines Dienstes
 */
export const getServiceLogs = async (id: string): Promise<ServiceLog[]> => {
  // Simuliere API-Aufruf
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const service = mockServices.find((s) => s.id === id);
      if (service) {
        resolve(generateMockLogs(id));
      } else {
        reject(new Error('Dienst nicht gefunden'));
      }
    }, 500);
  });
};