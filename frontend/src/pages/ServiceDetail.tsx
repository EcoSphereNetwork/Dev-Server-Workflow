// src/pages/ServiceDetail.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Container, Button } from '../design-system';
import { ServiceDetail as ServiceDetailComponent } from '../components/Services';
import { getService, getServiceLogs, startService, stopService, restartService, updateService, deleteService } from '../services/serviceApi';
import { Service, ServiceLog } from '../types/services';

// Styled-Components für die ServiceDetail-Seite
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

// ServiceDetail-Komponente
const ServiceDetailPage: React.FC = () => {
  // State für Dienst und Logs
  const [service, setService] = useState<Service | null>(null);
  const [logs, setLogs] = useState<ServiceLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  // Lade Dienst und Logs
  useEffect(() => {
    const fetchServiceAndLogs = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const [serviceData, logsData] = await Promise.all([
          getService(id),
          getServiceLogs(id),
        ]);
        
        setService(serviceData);
        setLogs(logsData);
        setError(null);
      } catch (err) {
        console.error('Fehler beim Laden des Dienstes:', err);
        setError('Der Dienst konnte nicht geladen werden. Bitte versuchen Sie es später erneut.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchServiceAndLogs();
  }, [id]);
  
  // Starte den Dienst
  const handleStartService = async () => {
    if (!id) return;
    
    try {
      const updatedService = await startService(id);
      setService(updatedService);
    } catch (err) {
      console.error('Fehler beim Starten des Dienstes:', err);
      setError('Der Dienst konnte nicht gestartet werden. Bitte versuchen Sie es später erneut.');
    }
  };
  
  // Stoppe den Dienst
  const handleStopService = async () => {
    if (!id) return;
    
    try {
      const updatedService = await stopService(id);
      setService(updatedService);
    } catch (err) {
      console.error('Fehler beim Stoppen des Dienstes:', err);
      setError('Der Dienst konnte nicht gestoppt werden. Bitte versuchen Sie es später erneut.');
    }
  };
  
  // Starte den Dienst neu
  const handleRestartService = async () => {
    if (!id) return;
    
    try {
      const updatedService = await restartService(id);
      setService(updatedService);
    } catch (err) {
      console.error('Fehler beim Neustarten des Dienstes:', err);
      setError('Der Dienst konnte nicht neu gestartet werden. Bitte versuchen Sie es später erneut.');
    }
  };
  
  // Aktualisiere den Dienst
  const handleUpdateService = async (updatedService: Service) => {
    try {
      const result = await updateService(updatedService);
      setService(result);
    } catch (err) {
      console.error('Fehler beim Aktualisieren des Dienstes:', err);
      setError('Der Dienst konnte nicht aktualisiert werden. Bitte versuchen Sie es später erneut.');
    }
  };
  
  // Lösche den Dienst
  const handleDeleteService = async () => {
    if (!id) return;
    
    try {
      await deleteService(id);
      navigate('/services');
    } catch (err) {
      console.error('Fehler beim Löschen des Dienstes:', err);
      setError('Der Dienst konnte nicht gelöscht werden. Bitte versuchen Sie es später erneut.');
    }
  };
  
  return (
    <Container size="xl">
      <PageContainer>
        <PageHeader>
          <PageTitle>Dienst-Details</PageTitle>
          <Button 
            variant="outlined" 
            onClick={() => navigate('/services')}
          >
            Zurück zur Übersicht
          </Button>
        </PageHeader>
        
        {error && (
          <ErrorContainer>
            <strong>Fehler:</strong> {error}
          </ErrorContainer>
        )}
        
        {loading ? (
          <LoadingContainer>
            Lade Dienst-Details...
          </LoadingContainer>
        ) : service ? (
          <ServiceDetailComponent
            service={service}
            logs={logs}
            onStart={handleStartService}
            onStop={handleStopService}
            onRestart={handleRestartService}
            onUpdate={handleUpdateService}
            onDelete={handleDeleteService}
          />
        ) : (
          <ErrorContainer>
            Dienst nicht gefunden.
          </ErrorContainer>
        )}
      </PageContainer>
    </Container>
  );
};

export default ServiceDetailPage;