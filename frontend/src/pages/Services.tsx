// src/pages/Services.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Container, Card, Button } from '../design-system';
import { ServiceList } from '../components/Services';
import { Service, ServiceCategory } from '../types/services';
import { useServices } from '../context/ServicesContext';

// Styled-Components für die Services-Seite
const PageContainer = styled.div`
  padding: ${props => props.theme.spacing.md};
`;

const PageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const PageTitle = styled.h1`
  font-size: ${props => props.theme.typography.fontSize.xl};
  margin: 0;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: ${props => props.theme.typography.fontSize.lg};
  color: ${props => props.theme.colors.text.secondary};
`;

const ErrorContainer = styled.div`
  padding: ${props => props.theme.spacing.lg};
  background-color: ${props => props.theme.colors.error}20;
  border-radius: ${props => props.theme.borderRadius.md};
  color: ${props => props.theme.colors.error};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

// Services-Komponente
const Services: React.FC = () => {
  const navigate = useNavigate();
  
  // Services Context
  const { 
    services, 
    loading, 
    error, 
    startService, 
    stopService, 
    restartService 
  } = useServices();
  
  // Kategorien für die Dienste
  const categories: ServiceCategory[] = [
    {
      id: 'productivity',
      name: 'Produktivität',
      description: 'Tools für die Zusammenarbeit und Dokumentation',
      services: services.filter(service => 
        service.type === 'Notizen' || 
        service.type === 'Whiteboard'
      ),
    },
    {
      id: 'development',
      name: 'Entwicklung',
      description: 'Tools für die Softwareentwicklung',
      services: services.filter(service => 
        service.type === 'Git-Repository' || 
        service.type === 'Workflow-Automation'
      ),
    },
    {
      id: 'management',
      name: 'Management',
      description: 'Tools für das Projekt- und Ressourcenmanagement',
      services: services.filter(service => 
        service.type === 'Projektmanagement'
      ),
    },
  ];
  
  // Starte einen Dienst
  const handleStartService = async (id: string) => {
    try {
      await startService(id);
    } catch (err) {
      console.error('Fehler beim Starten des Dienstes:', err);
    }
  };
  
  // Stoppe einen Dienst
  const handleStopService = async (id: string) => {
    try {
      await stopService(id);
    } catch (err) {
      console.error('Fehler beim Stoppen des Dienstes:', err);
    }
  };
  
  // Starte einen Dienst neu
  const handleRestartService = async (id: string) => {
    try {
      await restartService(id);
    } catch (err) {
      console.error('Fehler beim Neustarten des Dienstes:', err);
    }
  };
  
  // Navigiere zur Dienst-Detail-Seite
  const handleViewServiceDetails = (id: string) => {
    navigate(`/services/${id}`);
  };
  
  return (
    <Container size="xl">
      <PageContainer>
        <PageHeader>
          <PageTitle>Dienste</PageTitle>
          <Button 
            variant="primary"
            onClick={() => navigate('/services/new')}
          >
            Neuen Dienst hinzufügen
          </Button>
        </PageHeader>
        
        {error && (
          <ErrorContainer>
            <strong>Fehler:</strong> {error}
          </ErrorContainer>
        )}
        
        {loading ? (
          <Card>
            <LoadingContainer>
              Lade Dienste...
            </LoadingContainer>
          </Card>
        ) : (
          <ServiceList
            services={services}
            categories={categories}
            onStart={handleStartService}
            onStop={handleStopService}
            onRestart={handleRestartService}
          />
        )}
      </PageContainer>
    </Container>
  );
};

export default Services;