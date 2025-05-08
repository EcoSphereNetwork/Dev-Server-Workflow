/**
 * Service-Card-Komponente
 * 
 * Eine Karte, die einen Dienst darstellt.
 */

import React from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { Card, Button } from '../../design-system';
import { Service } from '../../types/services';

// Service-Card-Props
export interface ServiceCardProps {
  /** Der Dienst */
  service: Service;
  /** Callback beim Starten des Dienstes */
  onStart?: (id: string) => void;
  /** Callback beim Stoppen des Dienstes */
  onStop?: (id: string) => void;
  /** Callback beim Neustarten des Dienstes */
  onRestart?: (id: string) => void;
  /** Zusätzliche CSS-Klasse */
  className?: string;
}

// Styled-Components für die Service-Card
const ServiceLogo = styled.div<{ $logo?: string }>`
  width: 64px;
  height: 64px;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.background.paper};
  background-image: url(${props => props.$logo || 'https://via.placeholder.com/64'});
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  margin-right: ${props => props.theme.spacing.md};
`;

const ServiceHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ServiceInfo = styled.div`
  flex: 1;
`;

const ServiceName = styled.h3`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
`;

const ServiceType = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
`;

const ServiceStatus = styled.div<{ $status: 'running' | 'stopped' | 'error' }>`
  display: flex;
  align-items: center;
  margin-top: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.typography.fontSize.sm};
  
  &::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: ${props => props.theme.spacing.xs};
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

const ServiceDescription = styled.p`
  margin: ${props => props.theme.spacing.md} 0;
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
`;

const ServiceActions = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
`;

// Service-Card-Komponente
export const ServiceCard: React.FC<ServiceCardProps> = ({
  service,
  onStart,
  onStop,
  onRestart,
  className,
}) => {
  const navigate = useNavigate();
  
  // Status-Text
  const getStatusText = (status: 'running' | 'stopped' | 'error'): string => {
    switch (status) {
      case 'running':
        return 'Läuft';
      case 'stopped':
        return 'Gestoppt';
      case 'error':
        return 'Fehler';
      default:
        return 'Unbekannt';
    }
  };
  
  // Öffne Dienst-Details
  const handleViewDetails = () => {
    navigate(`/services/${service.id}`);
  };
  
  // Öffne Dienst in neuem Tab
  const handleOpenService = () => {
    window.open(service.url, '_blank');
  };
  
  return (
    <Card className={className}>
      <ServiceHeader>
        <ServiceLogo $logo={service.logo} />
        <ServiceInfo>
          <ServiceName>{service.name}</ServiceName>
          <ServiceType>{service.type}</ServiceType>
          <ServiceStatus $status={service.status}>
            {getStatusText(service.status)}
          </ServiceStatus>
        </ServiceInfo>
      </ServiceHeader>
      
      <ServiceDescription>{service.description}</ServiceDescription>
      
      <ServiceActions>
        {service.status === 'stopped' || service.status === 'error' ? (
          <Button
            variant="outlined"
            size="sm"
            onClick={() => onStart?.(service.id)}
            disabled={!onStart}
          >
            Starten
          </Button>
        ) : (
          <Button
            variant="outlined"
            size="sm"
            onClick={() => onStop?.(service.id)}
            disabled={!onStop}
          >
            Stoppen
          </Button>
        )}
        
        <Button
          variant="outlined"
          size="sm"
          onClick={() => onRestart?.(service.id)}
          disabled={!onRestart || service.status === 'stopped'}
        >
          Neustarten
        </Button>
        
        <Button
          variant="outlined"
          size="sm"
          onClick={handleOpenService}
          disabled={service.status !== 'running'}
        >
          Öffnen
        </Button>
        
        <Button
          variant="primary"
          size="sm"
          onClick={handleViewDetails}
        >
          Details
        </Button>
      </ServiceActions>
    </Card>
  );
};

export default ServiceCard;