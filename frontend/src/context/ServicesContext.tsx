/**
 * Services Context
 * 
 * Kontext für die Verwaltung von Diensten, der in der gesamten Anwendung verfügbar ist.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Service, ServiceLog } from '../types/services';
import { 
  getServices, 
  getService, 
  startService, 
  stopService, 
  restartService, 
  updateService, 
  deleteService, 
  getServiceLogs 
} from '../services/serviceApi';

// Services Context Typ
interface ServicesContextType {
  services: Service[];
  loading: boolean;
  error: string | null;
  refreshServices: () => Promise<void>;
  getServiceById: (id: string) => Promise<Service>;
  getServiceLogs: (id: string) => Promise<ServiceLog[]>;
  startService: (id: string) => Promise<Service>;
  stopService: (id: string) => Promise<Service>;
  restartService: (id: string) => Promise<Service>;
  updateService: (service: Service) => Promise<Service>;
  deleteService: (id: string) => Promise<void>;
}

// Services Context
const ServicesContext = createContext<ServicesContextType | undefined>(undefined);

// Services Provider Props
interface ServicesProviderProps {
  children: ReactNode;
}

// Services Provider
export const ServicesProvider: React.FC<ServicesProviderProps> = ({ children }) => {
  // State für Dienste
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Lade Dienste beim ersten Rendern
  useEffect(() => {
    refreshServices();
  }, []);
  
  // Aktualisiere Dienste
  const refreshServices = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getServices();
      setServices(data);
    } catch (err) {
      console.error('Fehler beim Laden der Dienste:', err);
      setError('Die Dienste konnten nicht geladen werden. Bitte versuchen Sie es später erneut.');
    } finally {
      setLoading(false);
    }
  };
  
  // Hole Dienst anhand der ID
  const getServiceById = async (id: string): Promise<Service> => {
    try {
      return await getService(id);
    } catch (err) {
      console.error('Fehler beim Laden des Dienstes:', err);
      throw new Error('Der Dienst konnte nicht geladen werden.');
    }
  };
  
  // Hole Logs eines Dienstes
  const getServiceLogsById = async (id: string): Promise<ServiceLog[]> => {
    try {
      return await getServiceLogs(id);
    } catch (err) {
      console.error('Fehler beim Laden der Logs:', err);
      throw new Error('Die Logs konnten nicht geladen werden.');
    }
  };
  
  // Starte einen Dienst
  const startServiceById = async (id: string): Promise<Service> => {
    try {
      const updatedService = await startService(id);
      setServices(prevServices => 
        prevServices.map(service => 
          service.id === id ? updatedService : service
        )
      );
      return updatedService;
    } catch (err) {
      console.error('Fehler beim Starten des Dienstes:', err);
      throw new Error('Der Dienst konnte nicht gestartet werden.');
    }
  };
  
  // Stoppe einen Dienst
  const stopServiceById = async (id: string): Promise<Service> => {
    try {
      const updatedService = await stopService(id);
      setServices(prevServices => 
        prevServices.map(service => 
          service.id === id ? updatedService : service
        )
      );
      return updatedService;
    } catch (err) {
      console.error('Fehler beim Stoppen des Dienstes:', err);
      throw new Error('Der Dienst konnte nicht gestoppt werden.');
    }
  };
  
  // Starte einen Dienst neu
  const restartServiceById = async (id: string): Promise<Service> => {
    try {
      const updatedService = await restartService(id);
      setServices(prevServices => 
        prevServices.map(service => 
          service.id === id ? updatedService : service
        )
      );
      return updatedService;
    } catch (err) {
      console.error('Fehler beim Neustarten des Dienstes:', err);
      throw new Error('Der Dienst konnte nicht neu gestartet werden.');
    }
  };
  
  // Aktualisiere einen Dienst
  const updateServiceById = async (service: Service): Promise<Service> => {
    try {
      const updatedService = await updateService(service);
      setServices(prevServices => 
        prevServices.map(s => 
          s.id === service.id ? updatedService : s
        )
      );
      return updatedService;
    } catch (err) {
      console.error('Fehler beim Aktualisieren des Dienstes:', err);
      throw new Error('Der Dienst konnte nicht aktualisiert werden.');
    }
  };
  
  // Lösche einen Dienst
  const deleteServiceById = async (id: string): Promise<void> => {
    try {
      await deleteService(id);
      setServices(prevServices => 
        prevServices.filter(service => service.id !== id)
      );
    } catch (err) {
      console.error('Fehler beim Löschen des Dienstes:', err);
      throw new Error('Der Dienst konnte nicht gelöscht werden.');
    }
  };
  
  // Kontext-Wert
  const contextValue: ServicesContextType = {
    services,
    loading,
    error,
    refreshServices,
    getServiceById,
    getServiceLogs: getServiceLogsById,
    startService: startServiceById,
    stopService: stopServiceById,
    restartService: restartServiceById,
    updateService: updateServiceById,
    deleteService: deleteServiceById,
  };
  
  return (
    <ServicesContext.Provider value={contextValue}>
      {children}
    </ServicesContext.Provider>
  );
};

// Hook für den Zugriff auf den Services Context
export const useServices = (): ServicesContextType => {
  const context = useContext(ServicesContext);
  if (!context) {
    throw new Error('useServices must be used within a ServicesProvider');
  }
  return context;
};

export default ServicesContext;