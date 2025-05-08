/**
 * Service-Detail-Komponente
 * 
 * Zeigt detaillierte Informationen zu einem Dienst an.
 */

import React, { useState } from 'react';
import styled from 'styled-components';
import { Card, Button, Input, Modal, GridContainer, GridItem } from '../../design-system';
import { Service, ServiceLog } from '../../types/services';

// Service-Detail-Props
export interface ServiceDetailProps {
  /** Der Dienst */
  service: Service;
  /** Die Logs des Dienstes */
  logs?: ServiceLog[];
  /** Callback beim Starten des Dienstes */
  onStart?: () => void;
  /** Callback beim Stoppen des Dienstes */
  onStop?: () => void;
  /** Callback beim Neustarten des Dienstes */
  onRestart?: () => void;
  /** Callback beim Aktualisieren des Dienstes */
  onUpdate?: (service: Service) => void;
  /** Callback beim Löschen des Dienstes */
  onDelete?: () => void;
  /** Zusätzliche CSS-Klasse */
  className?: string;
}

// Styled-Components für die Service-Detail
const DetailContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
`;

const ServiceHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ServiceLogo = styled.div<{ $logo?: string }>`
  width: 80px;
  height: 80px;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.background.paper};
  background-image: url(${props => props.$logo || 'https://via.placeholder.com/80'});
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  margin-right: ${props => props.theme.spacing.md};
`;

const ServiceInfo = styled.div`
  flex: 1;
`;

const ServiceName = styled.h2`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.xl};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
`;

const ServiceType = styled.div`
  font-size: ${props => props.theme.typography.fontSize.md};
  color: ${props => props.theme.colors.text.secondary};
`;

const ServiceStatus = styled.div<{ $status: 'running' | 'stopped' | 'error' }>`
  display: flex;
  align-items: center;
  margin-top: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.typography.fontSize.md};
  
  &::before {
    content: '';
    display: inline-block;
    width: 10px;
    height: 10px;
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

const ServiceActions = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
`;

const ServiceDescription = styled.p`
  margin: ${props => props.theme.spacing.md} 0;
  font-size: ${props => props.theme.typography.fontSize.md};
  color: ${props => props.theme.colors.text.secondary};
`;

const SectionTitle = styled.h3`
  margin: ${props => props.theme.spacing.md} 0 ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const InfoItem = styled.div`
  margin-bottom: ${props => props.theme.spacing.md};
`;

const InfoLabel = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const InfoValue = styled.div`
  font-size: ${props => props.theme.typography.fontSize.md};
`;

const LogsContainer = styled.div`
  max-height: 300px;
  overflow-y: auto;
  background-color: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.md};
  border: 1px solid ${props => props.theme.colors.divider};
  padding: ${props => props.theme.spacing.sm};
  font-family: ${props => props.theme.typography.fontFamily.code};
  font-size: ${props => props.theme.typography.fontSize.sm};
`;

const LogEntry = styled.div<{ $level: 'info' | 'warning' | 'error' | 'debug' }>`
  padding: ${props => props.theme.spacing.xs};
  border-bottom: 1px solid ${props => props.theme.colors.divider};
  color: ${props => {
    switch (props.$level) {
      case 'info':
        return props.theme.colors.text.primary;
      case 'warning':
        return props.theme.colors.warning.main;
      case 'error':
        return props.theme.colors.error;
      case 'debug':
        return props.theme.colors.text.secondary;
      default:
        return props.theme.colors.text.primary;
    }
  }};
  
  &:last-child {
    border-bottom: none;
  }
`;

const LogTimestamp = styled.span`
  color: ${props => props.theme.colors.text.secondary};
  margin-right: ${props => props.theme.spacing.sm};
`;

const TabContainer = styled.div`
  display: flex;
  flex-direction: column;
`;

const TabHeader = styled.div`
  display: flex;
  border-bottom: 1px solid ${props => props.theme.colors.divider};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const TabButton = styled.button<{ $active: boolean }>`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background-color: ${props => props.$active ? props.theme.colors.background.paper : 'transparent'};
  border: none;
  border-bottom: 2px solid ${props => props.$active ? props.theme.colors.primary : 'transparent'};
  cursor: pointer;
  font-weight: ${props => props.$active ? props.theme.typography.fontWeight.medium : props.theme.typography.fontWeight.regular};
  color: ${props => props.$active ? props.theme.colors.primary : props.theme.colors.text.primary};
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.theme.colors.background.paper};
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const TabContent = styled.div`
  padding: ${props => props.theme.spacing.md} 0;
`;

const ConfigForm = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

// Service-Detail-Komponente
export const ServiceDetail: React.FC<ServiceDetailProps> = ({
  service,
  logs = [],
  onStart,
  onStop,
  onRestart,
  onUpdate,
  onDelete,
  className,
}) => {
  // State für Tabs und Modals
  const [activeTab, setActiveTab] = useState<'overview' | 'config' | 'logs' | 'stats'>('overview');
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [editedService, setEditedService] = useState<Service>(service);
  
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
  
  // Formatiere Zeitstempel
  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };
  
  // Öffne Dienst in neuem Tab
  const handleOpenService = () => {
    window.open(service.url, '_blank');
  };
  
  // Aktualisiere Dienst
  const handleUpdate = () => {
    if (onUpdate) {
      onUpdate(editedService);
    }
  };
  
  // Rendere Tab-Inhalt
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <GridContainer spacing={{ xs: 2 }}>
            <GridItem xs={12} md={6}>
              <InfoItem>
                <InfoLabel>URL</InfoLabel>
                <InfoValue>
                  <a href={service.url} target="_blank" rel="noopener noreferrer">
                    {service.url}
                  </a>
                </InfoValue>
              </InfoItem>
            </GridItem>
            
            <GridItem xs={12} md={6}>
              <InfoItem>
                <InfoLabel>Version</InfoLabel>
                <InfoValue>{service.version || 'Nicht verfügbar'}</InfoValue>
              </InfoItem>
            </GridItem>
            
            {service.resources && (
              <>
                <GridItem xs={12} md={4}>
                  <InfoItem>
                    <InfoLabel>CPU-Auslastung</InfoLabel>
                    <InfoValue>{service.resources.cpu || 0}%</InfoValue>
                  </InfoItem>
                </GridItem>
                
                <GridItem xs={12} md={4}>
                  <InfoItem>
                    <InfoLabel>Speicher-Auslastung</InfoLabel>
                    <InfoValue>{service.resources.memory || 0}%</InfoValue>
                  </InfoItem>
                </GridItem>
                
                <GridItem xs={12} md={4}>
                  <InfoItem>
                    <InfoLabel>Festplatten-Auslastung</InfoLabel>
                    <InfoValue>{service.resources.disk || 0}%</InfoValue>
                  </InfoItem>
                </GridItem>
              </>
            )}
            
            {service.ports && service.ports.length > 0 && (
              <GridItem xs={12}>
                <InfoItem>
                  <InfoLabel>Ports</InfoLabel>
                  <InfoValue>
                    {service.ports.map((port, index) => (
                      <div key={index}>
                        {port.internal}:{port.external} ({port.protocol})
                      </div>
                    ))}
                  </InfoValue>
                </InfoItem>
              </GridItem>
            )}
            
            {service.dependencies && service.dependencies.length > 0 && (
              <GridItem xs={12}>
                <InfoItem>
                  <InfoLabel>Abhängigkeiten</InfoLabel>
                  <InfoValue>
                    {service.dependencies.join(', ')}
                  </InfoValue>
                </InfoItem>
              </GridItem>
            )}
          </GridContainer>
        );
      
      case 'config':
        return (
          <ConfigForm>
            <Input
              label="Name"
              value={editedService.name}
              onChange={(e) => setEditedService({ ...editedService, name: e.target.value })}
            />
            
            <Input
              label="Beschreibung"
              value={editedService.description}
              onChange={(e) => setEditedService({ ...editedService, description: e.target.value })}
            />
            
            <Input
              label="URL"
              value={editedService.url}
              onChange={(e) => setEditedService({ ...editedService, url: e.target.value })}
            />
            
            <Input
              label="Version"
              value={editedService.version || ''}
              onChange={(e) => setEditedService({ ...editedService, version: e.target.value })}
            />
            
            <Button variant="primary" onClick={handleUpdate}>
              Speichern
            </Button>
          </ConfigForm>
        );
      
      case 'logs':
        return (
          <>
            <LogsContainer>
              {logs.length === 0 ? (
                <div>Keine Logs verfügbar.</div>
              ) : (
                logs.map((log, index) => (
                  <LogEntry key={index} $level={log.level}>
                    <LogTimestamp>{formatTimestamp(log.timestamp)}</LogTimestamp>
                    {log.message}
                  </LogEntry>
                ))
              )}
            </LogsContainer>
            
            <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
              <Button variant="outlined" size="sm">
                Logs herunterladen
              </Button>
            </div>
          </>
        );
      
      case 'stats':
        return (
          <div>
            <p>Statistiken werden geladen...</p>
          </div>
        );
      
      default:
        return null;
    }
  };
  
  return (
    <DetailContainer className={className}>
      <Card>
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
              onClick={onStart}
              disabled={!onStart}
            >
              Starten
            </Button>
          ) : (
            <Button
              variant="outlined"
              onClick={onStop}
              disabled={!onStop}
            >
              Stoppen
            </Button>
          )}
          
          <Button
            variant="outlined"
            onClick={onRestart}
            disabled={!onRestart || service.status === 'stopped'}
          >
            Neustarten
          </Button>
          
          <Button
            variant="outlined"
            onClick={handleOpenService}
            disabled={service.status !== 'running'}
          >
            Öffnen
          </Button>
          
          <Button
            variant="error"
            onClick={() => setIsDeleteModalOpen(true)}
          >
            Löschen
          </Button>
        </ServiceActions>
      </Card>
      
      <Card>
        <TabContainer>
          <TabHeader>
            <TabButton
              $active={activeTab === 'overview'}
              onClick={() => setActiveTab('overview')}
            >
              Übersicht
            </TabButton>
            <TabButton
              $active={activeTab === 'config'}
              onClick={() => setActiveTab('config')}
            >
              Konfiguration
            </TabButton>
            <TabButton
              $active={activeTab === 'logs'}
              onClick={() => setActiveTab('logs')}
            >
              Logs
            </TabButton>
            <TabButton
              $active={activeTab === 'stats'}
              onClick={() => setActiveTab('stats')}
            >
              Statistiken
            </TabButton>
          </TabHeader>
          
          <TabContent>
            {renderTabContent()}
          </TabContent>
        </TabContainer>
      </Card>
      
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Dienst löschen"
        size="sm"
        footer={
          <>
            <Button
              variant="text"
              onClick={() => setIsDeleteModalOpen(false)}
            >
              Abbrechen
            </Button>
            <Button
              variant="error"
              onClick={() => {
                if (onDelete) {
                  onDelete();
                }
                setIsDeleteModalOpen(false);
              }}
            >
              Löschen
            </Button>
          </>
        }
      >
        <p>Sind Sie sicher, dass Sie den Dienst "{service.name}" löschen möchten?</p>
        <p>Diese Aktion kann nicht rückgängig gemacht werden.</p>
      </Modal>
    </DetailContainer>
  );
};

export default ServiceDetail;