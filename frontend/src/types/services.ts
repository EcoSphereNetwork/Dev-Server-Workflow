/**
 * Service-Typen
 */

// Service-Typ
export interface Service {
  /** Die ID des Dienstes */
  id: string;
  /** Der Name des Dienstes */
  name: string;
  /** Die Beschreibung des Dienstes */
  description: string;
  /** Der Typ des Dienstes */
  type: string;
  /** Die URL des Dienstes */
  url: string;
  /** Das Logo des Dienstes */
  logo?: string;
  /** Der Status des Dienstes */
  status: 'running' | 'stopped' | 'error';
  /** Die Version des Dienstes */
  version?: string;
  /** Die Konfiguration des Dienstes */
  config?: Record<string, any>;
  /** Die Ressourcen des Dienstes */
  resources?: {
    cpu?: number;
    memory?: number;
    disk?: number;
  };
  /** Die Abhängigkeiten des Dienstes */
  dependencies?: string[];
  /** Die Ports des Dienstes */
  ports?: Array<{
    internal: number;
    external: number;
    protocol: 'tcp' | 'udp';
  }>;
  /** Die Umgebungsvariablen des Dienstes */
  environment?: Record<string, string>;
  /** Die Volumes des Dienstes */
  volumes?: Array<{
    source: string;
    target: string;
  }>;
  /** Die Netzwerke des Dienstes */
  networks?: string[];
  /** Die Labels des Dienstes */
  labels?: Record<string, string>;
  /** Die Metadaten des Dienstes */
  metadata?: Record<string, any>;
}

// Service-Kategorie
export interface ServiceCategory {
  /** Die ID der Kategorie */
  id: string;
  /** Der Name der Kategorie */
  name: string;
  /** Die Beschreibung der Kategorie */
  description?: string;
  /** Die Dienste in der Kategorie */
  services: Service[];
}

// Service-Aktion
export interface ServiceAction {
  /** Die ID der Aktion */
  id: string;
  /** Der Name der Aktion */
  name: string;
  /** Die Beschreibung der Aktion */
  description?: string;
  /** Der Typ der Aktion */
  type: 'start' | 'stop' | 'restart' | 'update' | 'backup' | 'restore' | 'custom';
  /** Die Parameter der Aktion */
  parameters?: Record<string, any>;
  /** Die Funktion der Aktion */
  execute: (serviceId: string, parameters?: Record<string, any>) => Promise<void>;
}

// Service-Log
export interface ServiceLog {
  /** Die ID des Logs */
  id: string;
  /** Die Nachricht des Logs */
  message: string;
  /** Der Zeitstempel des Logs */
  timestamp: string;
  /** Der Level des Logs */
  level: 'info' | 'warning' | 'error' | 'debug';
  /** Die Quelle des Logs */
  source?: string;
  /** Die Metadaten des Logs */
  metadata?: Record<string, any>;
}

// Service-Statistik
export interface ServiceStats {
  /** Die ID des Dienstes */
  serviceId: string;
  /** Der Zeitstempel der Statistik */
  timestamp: string;
  /** Die CPU-Auslastung */
  cpu: number;
  /** Die Speicher-Auslastung */
  memory: number;
  /** Die Festplatten-Auslastung */
  disk: number;
  /** Die Netzwerk-Auslastung */
  network: {
    rx: number;
    tx: number;
  };
  /** Die Anzahl der Anfragen */
  requests?: number;
  /** Die Antwortzeit */
  responseTime?: number;
  /** Die Fehlerrate */
  errorRate?: number;
  /** Die Metadaten der Statistik */
  metadata?: Record<string, any>;
}