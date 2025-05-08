// src/pages/Services.tsx
import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { colors } from '../theme';
import configuredServices, { Service as ConfiguredService } from '../config/services';

// Typen für die Dienste
interface Service extends ConfiguredService {
  status: 'online' | 'offline' | 'unknown';
}

// Typen für die Kategorien
type CategoryType = 'development' | 'productivity' | 'management' | 'monitoring' | 'infrastructure' | 'other';

interface Category {
  id: CategoryType;
  name: string;
  icon: string;
  description: string;
}

const categories: Category[] = [
  {
    id: 'development',
    name: 'Entwicklung',
    icon: '💻',
    description: 'Tools für die Softwareentwicklung'
  },
  {
    id: 'productivity',
    name: 'Produktivität',
    icon: '📝',
    description: 'Tools für die Zusammenarbeit und Dokumentation'
  },
  {
    id: 'management',
    name: 'Management',
    icon: '📊',
    description: 'Tools für das Projekt- und Ressourcenmanagement'
  },
  {
    id: 'monitoring',
    name: 'Monitoring',
    icon: '📈',
    description: 'Tools für die Überwachung und Analyse'
  },
  {
    id: 'infrastructure',
    name: 'Infrastruktur',
    icon: '🔧',
    description: 'Tools für die Verwaltung der Infrastruktur'
  },
  {
    id: 'other',
    name: 'Sonstiges',
    icon: '🔍',
    description: 'Weitere Tools und Dienste'
  }
];

const ServicesContainer = styled.div`
  padding: 20px;
`;

const ServicesTitle = styled.h1`
  font-size: 1.5rem;
  margin-bottom: 20px;
`;

const CategorySection = styled.div`
  margin-bottom: 40px;
`;

const CategoryHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid ${colors.divider};
  padding-bottom: 10px;
`;

const CategoryIcon = styled.div`
  font-size: 1.5rem;
  margin-right: 10px;
`;

const CategoryTitle = styled.h2`
  font-size: 1.25rem;
  margin: 0;
  color: ${colors.primary.main};
`;

const CategoryDescription = styled.p`
  color: ${colors.text.secondary};
  margin: 0 0 0 10px;
  font-size: 0.875rem;
`;

const ServicesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
`;

const ServiceCard = styled(Card)`
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  }
`;

const ServiceHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 15px;
`;

const ServiceIcon = styled.div`
  font-size: 1.5rem;
  margin-right: 10px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: ${colors.primary.light};
  color: ${colors.primary.main};
  border-radius: 8px;
`;

const ServiceName = styled.h2`
  font-size: 1.25rem;
  margin: 0;
`;

const ServiceDescription = styled.p`
  color: ${colors.text.secondary};
  margin-bottom: 15px;
  flex-grow: 1;
`;

const ServiceStatus = styled.div<{ $status: 'online' | 'offline' | 'unknown' }>`
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  margin-bottom: 15px;
  color: ${props => {
    switch (props.$status) {
      case 'online': return colors.success.main;
      case 'offline': return colors.error.main;
      default: return colors.warning.main;
    }
  }};
`;

const ServiceActions = styled.div`
  display: flex;
  gap: 10px;
  margin-top: auto;
`;

const SearchContainer = styled.div`
  margin-bottom: 20px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 10px 15px;
  border: 1px solid ${colors.divider};
  border-radius: 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: ${colors.primary.main};
    box-shadow: 0 0 0 2px ${colors.primary.light}40;
  }
`;

const FilterContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
`;

const FilterButton = styled.button<{ $active: boolean }>`
  padding: 8px 16px;
  border: 1px solid ${props => props.$active ? colors.primary.main : colors.divider};
  border-radius: 20px;
  background-color: ${props => props.$active ? colors.primary.main : 'transparent'};
  color: ${props => props.$active ? 'white' : colors.text.primary};
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease-in-out;
  
  &:hover {
    background-color: ${props => props.$active ? colors.primary.dark : colors.background.default};
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px ${colors.primary.light}40;
  }
`;

const NoResults = styled.div`
  text-align: center;
  padding: 40px;
  color: ${colors.text.secondary};
  font-size: 1.1rem;
`;

const IframeContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const IframeWrapper = styled.div`
  position: relative;
  width: 90%;
  height: 90%;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
`;

const IframeHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background-color: ${colors.primary.main};
  color: white;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  
  &:hover {
    opacity: 0.8;
  }
`;

const StyledIframe = styled.iframe`
  width: 100%;
  height: calc(100% - 50px);
  border: none;
`;

const Services: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategories, setActiveCategories] = useState<CategoryType[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchServices = async () => {
      try {
        setLoading(true);
        // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
        // const response = await apiClient.get('/services');
        // setServices(response.data);
        
        // Verwende die konfigurierten Dienste und füge den Status hinzu
        const servicesWithStatus = configuredServices.map(service => ({
          ...service,
          status: 'online' as const // Alle Dienste sind standardmäßig online
        }));
        
        setServices(servicesWithStatus);
      } catch (err: any) {
        setError('Fehler beim Laden der Dienste');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchServices();
  }, []);

  const handleOpenService = (service: Service) => {
    // Für die Web-UI: Öffne den Dienst in einem Modal
    if (window.electron) {
      // In der Electron-App: Navigiere zur ServiceView-Komponente
      navigate(`/services/${service.id}`);
    } else {
      // Im Browser: Öffne den Dienst in einem Modal
      setSelectedService(service);
    }
  };

  const handleCloseService = () => {
    setSelectedService(null);
  };

  const handleOpenInNewTab = (url: string) => {
    window.open(url, '_blank');
  };

  const handleCategoryFilter = (categoryId: CategoryType) => {
    if (activeCategories.includes(categoryId)) {
      setActiveCategories(activeCategories.filter(id => id !== categoryId));
    } else {
      setActiveCategories([...activeCategories, categoryId]);
    }
  };

  const filteredServices = useMemo(() => {
    return services.filter(service => {
      // Suche
      const matchesSearch = searchTerm === '' || 
        service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        service.description.toLowerCase().includes(searchTerm.toLowerCase());
      
      // Kategorie-Filter
      const matchesCategory = activeCategories.length === 0 || 
        activeCategories.includes(service.category);
      
      return matchesSearch && matchesCategory;
    });
  }, [services, searchTerm, activeCategories]);

  // Gruppiere Dienste nach Kategorie
  const servicesByCategory = useMemo(() => {
    const grouped: Record<CategoryType, Service[]> = {
      development: [],
      productivity: [],
      management: [],
      monitoring: [],
      infrastructure: [],
      other: []
    };
    
    filteredServices.forEach(service => {
      grouped[service.category].push(service);
    });
    
    return grouped;
  }, [filteredServices]);

  if (loading && services.length === 0) {
    return <div>Lade Dienste...</div>;
  }

  if (error) {
    return <div>Fehler: {error}</div>;
  }

  return (
    <ServicesContainer>
      <ServicesTitle>Integrierte Dienste</ServicesTitle>
      
      <SearchContainer>
        <SearchInput 
          type="text" 
          placeholder="Dienste suchen..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </SearchContainer>
      
      <FilterContainer>
        <FilterButton 
          $active={activeCategories.length === 0}
          onClick={() => setActiveCategories([])}
        >
          Alle
        </FilterButton>
        {categories.map(category => (
          <FilterButton 
            key={category.id}
            $active={activeCategories.includes(category.id)}
            onClick={() => handleCategoryFilter(category.id)}
          >
            {category.icon} {category.name}
          </FilterButton>
        ))}
      </FilterContainer>
      
      {filteredServices.length === 0 ? (
        <NoResults>
          Keine Dienste gefunden. Bitte passen Sie Ihre Suchkriterien an.
        </NoResults>
      ) : (
        categories.map(category => {
          const categoryServices = servicesByCategory[category.id];
          
          if (categoryServices.length === 0) {
            return null;
          }
          
          return (
            <CategorySection key={category.id}>
              <CategoryHeader>
                <CategoryIcon>{category.icon}</CategoryIcon>
                <CategoryTitle>{category.name}</CategoryTitle>
                <CategoryDescription>{category.description}</CategoryDescription>
              </CategoryHeader>
              
              <ServicesGrid>
                {categoryServices.map(service => (
                  <ServiceCard key={service.id}>
                    <ServiceHeader>
                      <ServiceIcon>{service.icon}</ServiceIcon>
                      <ServiceName>{service.name}</ServiceName>
                    </ServiceHeader>
                    <ServiceDescription>{service.description}</ServiceDescription>
                    <ServiceStatus $status={service.status}>
                      {service.status === 'online' ? '● Online' : service.status === 'offline' ? '● Offline' : '● Status unbekannt'}
                    </ServiceStatus>
                    <ServiceActions>
                      <Button 
                        variant="primary" 
                        onClick={() => handleOpenService(service)}
                        fullWidth
                      >
                        Öffnen
                      </Button>
                      <Button 
                        variant="outlined" 
                        onClick={() => handleOpenInNewTab(service.url)}
                      >
                        Neuer Tab
                      </Button>
                    </ServiceActions>
                  </ServiceCard>
                ))}
              </ServicesGrid>
            </CategorySection>
          );
        })
      )}

      {selectedService && (
        <IframeContainer>
          <IframeWrapper>
            <IframeHeader>
              <h3>{selectedService.name}</h3>
              <CloseButton onClick={handleCloseService}>&times;</CloseButton>
            </IframeHeader>
            <StyledIframe 
              src={selectedService.url} 
              title={selectedService.name}
              sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
            />
          </IframeWrapper>
        </IframeContainer>
      )}
    </ServicesContainer>
  );
};

export default Services;