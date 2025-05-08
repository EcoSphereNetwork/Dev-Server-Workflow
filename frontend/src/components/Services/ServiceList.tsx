/**
 * Service-List-Komponente
 * 
 * Eine Liste von Diensten.
 */

import React, { useState } from 'react';
import styled from 'styled-components';
import { Input, Button } from '../../design-system';
import ServiceCard from './ServiceCard';
import { Service, ServiceCategory } from '../../types/services';

// Service-List-Props
export interface ServiceListProps {
  /** Die Dienste */
  services: Service[];
  /** Die Kategorien */
  categories?: ServiceCategory[];
  /** Callback beim Starten eines Dienstes */
  onStart?: (id: string) => void;
  /** Callback beim Stoppen eines Dienstes */
  onStop?: (id: string) => void;
  /** Callback beim Neustarten eines Dienstes */
  onRestart?: (id: string) => void;
  /** Zusätzliche CSS-Klasse */
  className?: string;
}

// Styled-Components für die Service-List
const ListContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
`;

const ListHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.md};
`;

const SearchContainer = styled.div`
  flex: 1;
  min-width: 250px;
`;

const FilterContainer = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  flex-wrap: wrap;
`;

const FilterButton = styled.button<{ $active: boolean }>`
  background-color: ${props => props.$active ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.$active ? 'white' : props.theme.colors.text.primary};
  border: 1px solid ${props => props.$active ? props.theme.colors.primary : props.theme.colors.divider};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.$active ? props.theme.colors.primary : 'rgba(0, 0, 0, 0.05)'};
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const ServicesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: ${props => props.theme.spacing.md};
`;

const CategorySection = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const CategoryTitle = styled.h2`
  font-size: ${props => props.theme.typography.fontSize.lg};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.text.secondary};
`;

// Service-List-Komponente
export const ServiceList: React.FC<ServiceListProps> = ({
  services,
  categories,
  onStart,
  onStop,
  onRestart,
  className,
}) => {
  // State für Suche und Filter
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'running' | 'stopped' | 'error'>('all');
  
  // Filtere Dienste basierend auf Suche und Filter
  const filteredServices = services.filter(service => {
    // Suche
    const matchesSearch = 
      service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      service.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      service.type.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Status-Filter
    const matchesStatus = statusFilter === 'all' || service.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });
  
  // Gruppiere Dienste nach Kategorien, wenn Kategorien vorhanden sind
  const renderServices = () => {
    if (filteredServices.length === 0) {
      return (
        <EmptyState>
          <h3>Keine Dienste gefunden</h3>
          <p>Versuchen Sie, Ihre Suche oder Filter anzupassen.</p>
        </EmptyState>
      );
    }
    
    if (!categories || categories.length === 0) {
      return (
        <ServicesGrid>
          {filteredServices.map(service => (
            <ServiceCard
              key={service.id}
              service={service}
              onStart={onStart}
              onStop={onStop}
              onRestart={onRestart}
            />
          ))}
        </ServicesGrid>
      );
    }
    
    return categories.map(category => {
      const categoryServices = filteredServices.filter(service => 
        category.services.some(s => s.id === service.id)
      );
      
      if (categoryServices.length === 0) return null;
      
      return (
        <CategorySection key={category.id}>
          <CategoryTitle>{category.name}</CategoryTitle>
          <ServicesGrid>
            {categoryServices.map(service => (
              <ServiceCard
                key={service.id}
                service={service}
                onStart={onStart}
                onStop={onStop}
                onRestart={onRestart}
              />
            ))}
          </ServicesGrid>
        </CategorySection>
      );
    });
  };
  
  return (
    <ListContainer className={className}>
      <ListHeader>
        <SearchContainer>
          <Input
            placeholder="Dienste suchen..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            startIcon="🔍"
          />
        </SearchContainer>
        
        <FilterContainer>
          <FilterButton
            $active={statusFilter === 'all'}
            onClick={() => setStatusFilter('all')}
          >
            Alle
          </FilterButton>
          <FilterButton
            $active={statusFilter === 'running'}
            onClick={() => setStatusFilter('running')}
          >
            Laufend
          </FilterButton>
          <FilterButton
            $active={statusFilter === 'stopped'}
            onClick={() => setStatusFilter('stopped')}
          >
            Gestoppt
          </FilterButton>
          <FilterButton
            $active={statusFilter === 'error'}
            onClick={() => setStatusFilter('error')}
          >
            Fehler
          </FilterButton>
        </FilterContainer>
      </ListHeader>
      
      {renderServices()}
    </ListContainer>
  );
};

export default ServiceList;