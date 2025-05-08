// src/pages/ServiceView.tsx
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Button from '../components/common/Button';
import { colors } from '../theme';
import services from '../config/services';

const ServiceViewContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
`;

const ServiceHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background-color: ${colors.primary.main};
  color: white;
`;

const ServiceTitle = styled.h2`
  margin: 0;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  
  .icon {
    margin-right: 10px;
    font-size: 1.5rem;
  }
`;

const ServiceActions = styled.div`
  display: flex;
  gap: 10px;
`;

// Verwende ein div als Container für iframe oder webview
const ServiceFrameContainer = styled.div`
  flex: 1;
  width: 100%;
  height: 100%;
`;

// Styles für iframe
const ServiceFrame = styled.iframe`
  flex: 1;
  border: none;
  width: 100%;
  height: 100%;
`;

// Styles für webview (wird in Electron verwendet)
const ServiceWebView = styled.webview`
  flex: 1;
  border: none;
  width: 100%;
  height: 100%;
`;

const BackButton = styled(Button)`
  background-color: transparent;
  border: 1px solid white;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
`;

const ServiceView: React.FC = () => {
  const { serviceId } = useParams<{ serviceId: string }>();
  const [service, setService] = useState(services.find(s => s.id === serviceId));
  const navigate = useNavigate();
  
  useEffect(() => {
    if (!serviceId || !service) {
      navigate('/services');
    }
  }, [serviceId, service, navigate]);
  
  if (!service) {
    return <div>Dienst nicht gefunden</div>;
  }
  
  return (
    <ServiceViewContainer>
      <ServiceHeader>
        <ServiceTitle>
          <span className="icon">{service.icon}</span>
          {service.name}
        </ServiceTitle>
        <ServiceActions>
          <BackButton onClick={() => navigate('/services')}>
            Zurück
          </BackButton>
          <Button 
            variant="outlined" 
            onClick={() => window.open(service.url, '_blank')}
          >
            In neuem Tab öffnen
          </Button>
        </ServiceActions>
      </ServiceHeader>
      <ServiceFrameContainer>
        {window.electron ? (
          // In Electron verwenden wir das webview-Tag
          <ServiceWebView 
            src={service.url}
            allowpopups="true"
            webpreferences="allowRunningInsecureContent=no, javascript=yes"
          />
        ) : (
          // Im Browser verwenden wir ein iframe
          <ServiceFrame 
            src={service.url} 
            title={service.name}
            sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
          />
        )}
      </ServiceFrameContainer>
    </ServiceViewContainer>
  );
};

export default ServiceView;