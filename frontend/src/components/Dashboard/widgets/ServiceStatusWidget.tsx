/**
 * Service-Status-Widget
 * 
 * Zeigt den Status der Dienste an.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Widget, { WidgetProps } from '../Widget';

// Service-Typ
interface Service {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'error';
  url: string;
  type: string;
}

// Styled-Components für das Widget
const ServiceList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
  max-height: 100%;
  overflow-y: auto;
`;

const ServiceItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.sm};
  background-color: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.sm};
  box-shadow: ${props => props.theme.shadows.sm};
`;

const ServiceInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const ServiceName = styled.span`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const ServiceType = styled.span`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
`;

const ServiceStatus = styled.div<{ $status: 'running' | 'stopped' | 'error' }>`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  
  &::before {
    content: '';
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: ${props => {
      switch (props.$status) {
        case 'running':
          return props.theme.colors.success.main;
        case 'stopped':
          return props.theme.colors.warning.main;
        case 'error':
          return props.theme.colors.error;
        default:
          return props.theme.colors.success.main;
      }
    }};
  }
`;

const ServiceActions = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.xs};
`;

const ServiceButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  font-size: ${props => props.theme.typography.fontSize.md};
  color: ${props => props.theme.colors.text.secondary};
  padding: ${props => props.theme.spacing.xs};
  border-radius: ${props => props.theme.borderRadius.full};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s, background-color 0.2s;
  
  &:hover {
    color: ${props => props.theme.colors.text.primary};
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

// Service-Status-Widget-Props
export interface ServiceStatusWidgetProps extends Omit<WidgetProps, 'children'> {}

// Service-Status-Widget-Komponente
export const ServiceStatusWidget: React.FC<ServiceStatusWidgetProps> = (props) => {
  // State für Dienste
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Simuliere Laden von Diensten
  useEffect(() => {
    const mockServices: Service[] = [
      {
        id: '1',
        name: 'n8n',
        status: 'running',
        url: 'https://n8n.ecospherenet.work',
        type: 'Workflow-Automation',
      },
      {
        id: '2',
        name: 'AppFlowy',
        status: 'running',
        url: 'https://appflowy.ecospherenet.work',
        type: 'Notizen',
      },
      {
        id: '3',
        name: 'OpenProject',
        status: 'stopped',
        url: 'https://openproject.ecospherenet.work',
        type: 'Projektmanagement',
      },
      {
        id: '4',
        name: 'GitLab',
        status: 'running',
        url: 'https://gitlab.ecospherenet.work',
        type: 'Git-Repository',
      },
      {
        id: '5',
        name: 'Affine',
        status: 'error',
        url: 'https://affine.ecospherenet.work',
        type: 'Whiteboard',
      },
    ];
    
    // Simuliere Laden
    setTimeout(() => {
      setServices(mockServices);
      setLoading(false);
    }, 1000);
  }, []);
  
  // Dienst starten
  const handleStartService = (id: string) => {
    setServices(prevServices => 
      prevServices.map(service => 
        service.id === id 
          ? { ...service, status: 'running' } 
          : service
      )
    );
  };
  
  // Dienst stoppen
  const handleStopService = (id: string) => {
    setServices(prevServices => 
      prevServices.map(service => 
        service.id === id 
          ? { ...service, status: 'stopped' } 
          : service
      )
    );
  };
  
  // Dienst neustarten
  const handleRestartService = (id: string) => {
    setServices(prevServices => 
      prevServices.map(service => {
        if (service.id === id) {
          // Simuliere Neustart
          return { ...service, status: 'stopped' };
        }
        return service;
      })
    );
    
    // Nach kurzer Verzögerung auf "running" setzen
    setTimeout(() => {
      setServices(prevServices => 
        prevServices.map(service => 
          service.id === id 
            ? { ...service, status: 'running' } 
            : service
        )
      );
    }, 2000);
  };
  
  // Öffne Dienst in neuem Tab
  const handleOpenService = (url: string) => {
    window.open(url, '_blank');
  };
  
  return (
    <Widget {...props}>
      {loading ? (
        <div>Lade Dienste...</div>
      ) : (
        <ServiceList>
          {services.map(service => (
            <ServiceItem key={service.id}>
              <ServiceInfo>
                <ServiceName>{service.name}</ServiceName>
                <ServiceType>{service.type}</ServiceType>
              </ServiceInfo>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ServiceStatus $status={service.status}>
                  {service.status === 'running' ? 'Läuft' : service.status === 'stopped' ? 'Gestoppt' : 'Fehler'}
                </ServiceStatus>
                <ServiceActions>
                  {service.status === 'stopped' || service.status === 'error' ? (
                    <ServiceButton
                      onClick={() => handleStartService(service.id)}
                      aria-label={`${service.name} starten`}
                      title="Starten"
                    >
                      ▶️
                    </ServiceButton>
                  ) : (
                    <ServiceButton
                      onClick={() => handleStopService(service.id)}
                      aria-label={`${service.name} stoppen`}
                      title="Stoppen"
                    >
                      ⏹️
                    </ServiceButton>
                  )}
                  <ServiceButton
                    onClick={() => handleRestartService(service.id)}
                    aria-label={`${service.name} neustarten`}
                    title="Neustarten"
                  >
                    🔄
                  </ServiceButton>
                  <ServiceButton
                    onClick={() => handleOpenService(service.url)}
                    aria-label={`${service.name} öffnen`}
                    title="Öffnen"
                  >
                    🔗
                  </ServiceButton>
                </ServiceActions>
              </div>
            </ServiceItem>
          ))}
        </ServiceList>
      )}
    </Widget>
  );
};

export default ServiceStatusWidget;