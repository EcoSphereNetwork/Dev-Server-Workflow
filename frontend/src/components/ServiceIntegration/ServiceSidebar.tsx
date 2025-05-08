/**
 * Service-Sidebar-Komponente
 * 
 * Eine Sidebar für die Integration von Diensten.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../design-system';
import { Service } from '../../types/services';
import { useServices } from '../../context/ServicesContext';
import { useSettings } from '../../context/SettingsContext';

// Service-Sidebar-Props
interface ServiceSidebarProps {
  /** Ob die Sidebar geöffnet ist */
  isOpen: boolean;
  /** Callback beim Schließen der Sidebar */
  onClose: () => void;
}

// Styled-Components für die Service-Sidebar
const SidebarContainer = styled.div<{ $isOpen: boolean }>`
  position: fixed;
  top: 0;
  right: ${props => props.$isOpen ? '0' : '-350px'};
  width: 350px;
  height: 100vh;
  background-color: ${props => props.theme.colors.background.paper};
  box-shadow: ${props => props.theme.shadows.lg};
  z-index: ${props => props.theme.zIndex.drawer};
  transition: right 0.3s ${props => props.theme.transitions.easing.easeInOut};
  display: flex;
  flex-direction: column;
`;

const SidebarHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.md};
  border-bottom: 1px solid ${props => props.theme.colors.divider};
`;

const SidebarTitle = styled.h2`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: ${props => props.theme.typography.fontSize.lg};
  cursor: pointer;
  color: ${props => props.theme.colors.text.secondary};
  
  &:hover {
    color: ${props => props.theme.colors.text.primary};
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const SidebarContent = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: ${props => props.theme.spacing.md};
`;

const SidebarFooter = styled.div`
  padding: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.divider};
  display: flex;
  justify-content: flex-end;
`;

const ServiceList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
`;

const ServiceItem = styled.div<{ $favorite: boolean }>`
  display: flex;
  align-items: center;
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.$favorite ? props.theme.colors.primary + '10' : props.theme.colors.background.default};
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.$favorite ? props.theme.colors.primary + '20' : props.theme.colors.background.paper};
  }
`;

const ServiceIcon = styled.div<{ $logo?: string }>`
  width: 32px;
  height: 32px;
  border-radius: ${props => props.theme.borderRadius.sm};
  background-color: ${props => props.theme.colors.background.paper};
  background-image: url(${props => props.$logo || 'https://via.placeholder.com/32'});
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  margin-right: ${props => props.theme.spacing.sm};
`;

const ServiceInfo = styled.div`
  flex: 1;
`;

const ServiceName = styled.div`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const ServiceStatus = styled.div<{ $status: 'running' | 'stopped' | 'error' }>`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => {
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
`;

const ServiceActions = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
`;

const FavoriteButton = styled.button<{ $favorite: boolean }>`
  background: none;
  border: none;
  cursor: pointer;
  font-size: ${props => props.theme.typography.fontSize.md};
  color: ${props => props.$favorite ? props.theme.colors.warning.main : props.theme.colors.text.secondary};
  
  &:hover {
    color: ${props => props.$favorite ? props.theme.colors.warning.dark : props.theme.colors.text.primary};
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const SearchInput = styled.input`
  width: 100%;
  padding: ${props => props.theme.spacing.sm};
  border: 1px solid ${props => props.theme.colors.divider};
  border-radius: ${props => props.theme.borderRadius.md};
  margin-bottom: ${props => props.theme.spacing.md};
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 2px ${props => props.theme.colors.primary}33;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: ${props => props.theme.colors.text.secondary};
`;

const Overlay = styled.div<{ $isOpen: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: ${props => props.theme.zIndex.drawer - 1};
  opacity: ${props => props.$isOpen ? 1 : 0};
  visibility: ${props => props.$isOpen ? 'visible' : 'hidden'};
  transition: opacity 0.3s ${props => props.theme.transitions.easing.easeInOut},
              visibility 0.3s ${props => props.theme.transitions.easing.easeInOut};
`;

// Service-Sidebar-Komponente
export const ServiceSidebar: React.FC<ServiceSidebarProps> = ({ isOpen, onClose }) => {
  // State für Suche
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();
  
  // Services Context
  const { services, loading, refreshServices } = useServices();
  
  // Settings für Favoriten
  const { settings, toggleFavoriteService } = useSettings();
  
  // Lade Dienste
  useEffect(() => {
    if (isOpen) {
      refreshServices();
    }
  }, [isOpen, refreshServices]);
  
  // Filtere Dienste basierend auf Suche
  const filteredServices = services.filter(service => 
    service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    service.description.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  // Sortiere Dienste: Favoriten zuerst, dann nach Status (laufend zuerst), dann nach Name
  const sortedServices = [...filteredServices].sort((a, b) => {
    // Favoriten zuerst
    const aFavorite = settings.services.favorites.includes(a.id);
    const bFavorite = settings.services.favorites.includes(b.id);
    
    if (aFavorite && !bFavorite) return -1;
    if (!aFavorite && bFavorite) return 1;
    
    // Dann nach Status
    if (a.status === 'running' && b.status !== 'running') return -1;
    if (a.status !== 'running' && b.status === 'running') return 1;
    
    // Dann nach Name
    return a.name.localeCompare(b.name);
  });
  
  // Öffne Dienst
  const handleOpenService = (service: Service) => {
    if (service.status === 'running') {
      window.open(service.url, '_blank');
    } else {
      navigate(`/services/${service.id}`);
    }
    onClose();
  };
  
  // Öffne Dienst-Details
  const handleOpenServiceDetails = (service: Service, event: React.MouseEvent) => {
    event.stopPropagation();
    navigate(`/services/${service.id}`);
    onClose();
  };
  
  // Favorisiere/Entfavorisiere Dienst
  const handleToggleFavorite = (id: string, event: React.MouseEvent) => {
    event.stopPropagation();
    toggleFavoriteService(id);
  };
  
  return (
    <>
      <Overlay $isOpen={isOpen} onClick={onClose} />
      
      <SidebarContainer $isOpen={isOpen}>
        <SidebarHeader>
          <SidebarTitle>Dienste</SidebarTitle>
          <CloseButton onClick={onClose} aria-label="Schließen">
            &times;
          </CloseButton>
        </SidebarHeader>
        
        <SidebarContent>
          <SearchInput
            type="text"
            placeholder="Dienste suchen..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          
          {loading ? (
            <LoadingContainer>
              Lade Dienste...
            </LoadingContainer>
          ) : sortedServices.length === 0 ? (
            <div>Keine Dienste gefunden.</div>
          ) : (
            <ServiceList>
              {sortedServices.map(service => {
                const isFavorite = settings.services.favorites.includes(service.id);
                
                return (
                  <ServiceItem
                    key={service.id}
                    $favorite={isFavorite}
                    onClick={() => handleOpenService(service)}
                  >
                    <ServiceIcon $logo={service.logo} />
                    <ServiceInfo>
                      <ServiceName>{service.name}</ServiceName>
                      <ServiceStatus $status={service.status}>
                        {service.status === 'running' ? 'Läuft' : service.status === 'stopped' ? 'Gestoppt' : 'Fehler'}
                      </ServiceStatus>
                    </ServiceInfo>
                    <ServiceActions>
                      <FavoriteButton
                        $favorite={isFavorite}
                        onClick={(e) => handleToggleFavorite(service.id, e)}
                        aria-label={isFavorite ? 'Von Favoriten entfernen' : 'Zu Favoriten hinzufügen'}
                        title={isFavorite ? 'Von Favoriten entfernen' : 'Zu Favoriten hinzufügen'}
                      >
                        {isFavorite ? '★' : '☆'}
                      </FavoriteButton>
                      <Button
                        variant="text"
                        size="sm"
                        onClick={(e) => handleOpenServiceDetails(service, e)}
                      >
                        Details
                      </Button>
                    </ServiceActions>
                  </ServiceItem>
                );
              })}
            </ServiceList>
          )}
        </SidebarContent>
        
        <SidebarFooter>
          <Button
            variant="outlined"
            onClick={() => {
              navigate('/services');
              onClose();
            }}
          >
            Alle Dienste anzeigen
          </Button>
        </SidebarFooter>
      </SidebarContainer>
    </>
  );
};

export default ServiceSidebar;