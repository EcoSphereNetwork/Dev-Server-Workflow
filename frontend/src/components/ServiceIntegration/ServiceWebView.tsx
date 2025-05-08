/**
 * Service-WebView-Komponente
 * 
 * Eine WebView für die Integration von Diensten.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Button } from '../../design-system';
import { Service } from '../../types/services';
import { useServices } from '../../context/ServicesContext';

// Service-WebView-Props
interface ServiceWebViewProps {
  /** Die ID des Dienstes */
  serviceId: string;
  /** Ob die WebView geöffnet ist */
  isOpen: boolean;
  /** Callback beim Schließen der WebView */
  onClose: () => void;
}

// Styled-Components für die Service-WebView
const WebViewContainer = styled.div<{ $isOpen: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: ${props => props.theme.colors.background.paper};
  z-index: ${props => props.theme.zIndex.modal};
  opacity: ${props => props.$isOpen ? 1 : 0};
  visibility: ${props => props.$isOpen ? 'visible' : 'hidden'};
  transition: opacity 0.3s ${props => props.theme.transitions.easing.easeInOut},
              visibility 0.3s ${props => props.theme.transitions.easing.easeInOut};
  display: flex;
  flex-direction: column;
`;

const WebViewHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.md};
  background-color: ${props => props.theme.colors.primary};
  color: white;
`;

const WebViewTitle = styled.h2`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const WebViewActions = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: ${props => props.theme.typography.fontSize.lg};
  cursor: pointer;
  color: white;
  
  &:hover {
    opacity: 0.8;
  }
  
  &:focus-visible {
    outline: 2px solid white;
    outline-offset: 2px;
  }
`;

const WebViewContent = styled.div`
  flex: 1;
  position: relative;
`;

const WebViewIframe = styled.iframe`
  width: 100%;
  height: 100%;
  border: none;
`;

const LoadingContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: ${props => props.theme.colors.background.paper};
  z-index: 1;
`;

const ErrorContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: ${props => props.theme.colors.background.paper};
  z-index: 1;
  padding: ${props => props.theme.spacing.xl};
  text-align: center;
`;

const ErrorTitle = styled.h3`
  margin: 0 0 ${props => props.theme.spacing.md} 0;
  color: ${props => props.theme.colors.error};
`;

const ErrorMessage = styled.p`
  margin: 0 0 ${props => props.theme.spacing.lg} 0;
  color: ${props => props.theme.colors.text.secondary};
`;

// Service-WebView-Komponente
export const ServiceWebView: React.FC<ServiceWebViewProps> = ({ serviceId, isOpen, onClose }) => {
  // State für Dienst
  const [service, setService] = useState<Service | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Services Context
  const { getServiceById } = useServices();
  
  // Lade Dienst
  useEffect(() => {
    const fetchService = async () => {
      if (!isOpen || !serviceId) return;
      
      try {
        setLoading(true);
        setError(null);
        const data = await getServiceById(serviceId);
        setService(data);
      } catch (err) {
        console.error('Fehler beim Laden des Dienstes:', err);
        setError('Der Dienst konnte nicht geladen werden.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchService();
  }, [serviceId, isOpen, getServiceById]);
  
  // Öffne in neuem Tab
  const handleOpenInNewTab = () => {
    if (service) {
      window.open(service.url, '_blank');
    }
  };
  
  return (
    <WebViewContainer $isOpen={isOpen}>
      <WebViewHeader>
        <WebViewTitle>{service?.name || 'Dienst'}</WebViewTitle>
        <WebViewActions>
          <Button
            variant="outlined"
            size="sm"
            onClick={handleOpenInNewTab}
            disabled={!service || service.status !== 'running'}
          >
            In neuem Tab öffnen
          </Button>
          <CloseButton onClick={onClose} aria-label="Schließen">
            &times;
          </CloseButton>
        </WebViewActions>
      </WebViewHeader>
      
      <WebViewContent>
        {loading ? (
          <LoadingContainer>
            Lade Dienst...
          </LoadingContainer>
        ) : error ? (
          <ErrorContainer>
            <ErrorTitle>Fehler</ErrorTitle>
            <ErrorMessage>{error}</ErrorMessage>
            <Button
              variant="primary"
              onClick={onClose}
            >
              Schließen
            </Button>
          </ErrorContainer>
        ) : service?.status !== 'running' ? (
          <ErrorContainer>
            <ErrorTitle>Dienst nicht verfügbar</ErrorTitle>
            <ErrorMessage>
              Der Dienst "{service?.name}" ist derzeit nicht aktiv. 
              Bitte starten Sie den Dienst, um ihn zu verwenden.
            </ErrorMessage>
            <Button
              variant="primary"
              onClick={onClose}
            >
              Schließen
            </Button>
          </ErrorContainer>
        ) : (
          <WebViewIframe
            src={service?.url}
            title={service?.name}
            sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
          />
        )}
      </WebViewContent>
    </WebViewContainer>
  );
};

export default ServiceWebView;