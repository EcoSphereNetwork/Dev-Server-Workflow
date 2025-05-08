/**
 * Service-Menu-Komponente
 * 
 * Eine Menü-Komponente für die Integration von Diensten in der Sidebar.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useSettings } from '../../context/SettingsContext';
import { useServices } from '../../context/ServicesContext';

// Service-Menu-Props
interface ServiceMenuProps {
  /** Callback beim Auswählen eines Dienstes */
  onSelectService: (serviceId: string) => void;
}

// Styled-Components für das Service-Menu
const MenuContainer = styled.div`
  margin-top: ${props => props.theme.spacing.md};
  padding-top: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.divider};
`;

const MenuTitle = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  color: ${props => props.theme.colors.text.secondary};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const MenuList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xs};
`;

const MenuItem = styled.button<{ $active: boolean }>`
  display: flex;
  align-items: center;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background-color: ${props => props.$active ? props.theme.colors.primary + '20' : 'transparent'};
  color: ${props => props.$active ? props.theme.colors.primary : props.theme.colors.text.primary};
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  cursor: pointer;
  text-align: left;
  font-weight: ${props => props.$active ? props.theme.typography.fontWeight.medium : props.theme.typography.fontWeight.regular};
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.$active ? props.theme.colors.primary + '30' : props.theme.colors.background.paper};
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const MenuItemIcon = styled.div<{ $logo?: string; $status: 'running' | 'stopped' | 'error' }>`
  width: 24px;
  height: 24px;
  border-radius: ${props => props.theme.borderRadius.sm};
  background-color: ${props => props.theme.colors.background.paper};
  background-image: url(${props => props.$logo || 'https://via.placeholder.com/24'});
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  margin-right: ${props => props.theme.spacing.sm};
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -2px;
    right: -2px;
    width: 8px;
    height: 8px;
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
    border: 1px solid ${props => props.theme.colors.background.paper};
  }
`;

const MenuItemLabel = styled.span`
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const LoadingContainer = styled.div`
  padding: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.text.secondary};
  font-size: ${props => props.theme.typography.fontSize.sm};
  text-align: center;
`;

// Service-Menu-Komponente
export const ServiceMenu: React.FC<ServiceMenuProps> = ({ onSelectService }) => {
  // State für aktiven Dienst
  const [activeServiceId, setActiveServiceId] = useState<string | null>(null);
  
  // Services Context
  const { services, loading } = useServices();
  
  // Settings für Favoriten
  const { settings } = useSettings();
  
  // Filtere Favoriten
  const favoriteServices = services.filter(service => 
    settings.services.favorites.includes(service.id)
  );
  
  // Sortiere Favoriten nach Status (laufend zuerst), dann nach Name
  const sortedFavorites = [...favoriteServices].sort((a, b) => {
    // Nach Status
    if (a.status === 'running' && b.status !== 'running') return -1;
    if (a.status !== 'running' && b.status === 'running') return 1;
    
    // Nach Name
    return a.name.localeCompare(b.name);
  });
  
  // Wähle einen Dienst aus
  const handleSelectService = (serviceId: string) => {
    setActiveServiceId(serviceId);
    onSelectService(serviceId);
  };
  
  // Wenn keine Favoriten vorhanden sind, zeige nichts an
  if (!loading && favoriteServices.length === 0) {
    return null;
  }
  
  return (
    <MenuContainer>
      <MenuTitle>Favorisierte Dienste</MenuTitle>
      
      {loading ? (
        <LoadingContainer>
          Lade Dienste...
        </LoadingContainer>
      ) : (
        <MenuList>
          {sortedFavorites.map(service => (
            <MenuItem
              key={service.id}
              $active={activeServiceId === service.id}
              onClick={() => handleSelectService(service.id)}
            >
              <MenuItemIcon 
                $logo={service.logo} 
                $status={service.status} 
              />
              <MenuItemLabel>{service.name}</MenuItemLabel>
            </MenuItem>
          ))}
        </MenuList>
      )}
    </MenuContainer>
  );
};

export default ServiceMenu;