/**
 * Dashboard-Komponente
 * 
 * Eine anpassbare Dashboard-Komponente mit Widgets.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Button, GridContainer, GridItem, Modal } from '../../design-system';
import Widget, { WidgetProps, WidgetType, WidgetSize } from './Widget';
import SystemStatusWidget from './widgets/SystemStatusWidget';
import MCPStatusWidget from './widgets/MCPStatusWidget';
import ServiceStatusWidget from './widgets/ServiceStatusWidget';
import RecentActivityWidget from './widgets/RecentActivityWidget';
import QuickActionsWidget from './widgets/QuickActionsWidget';
import MetricsWidget from './widgets/MetricsWidget';
import NotificationsWidget from './widgets/NotificationsWidget';
import WeatherWidget from './widgets/WeatherWidget';
import NewsWidget from './widgets/NewsWidget';
import CustomWidget from './widgets/CustomWidget';

// Dashboard-Props
export interface DashboardProps {
  /** Zusätzliche CSS-Klasse */
  className?: string;
}

// Widget-Konfiguration
export interface WidgetConfig {
  id: string;
  type: WidgetType;
  title: string;
  size: WidgetSize;
  minimized: boolean;
  position: {
    x: number;
    y: number;
  };
}

// Styled-Components für das Dashboard
const DashboardContainer = styled.div`
  padding: ${props => props.theme.spacing.md};
`;

const DashboardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const DashboardTitle = styled.h1`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.xl};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
`;

const DashboardActions = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const WidgetGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.md};
  
  @media (max-width: ${props => props.theme.breakpoints.md}) {
    grid-template-columns: 1fr;
  }
`;

const WidgetTypeButton = styled.button<{ $selected: boolean }>`
  background-color: ${props => props.$selected ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.$selected ? 'white' : props.theme.colors.text.primary};
  border: 1px solid ${props => props.$selected ? props.theme.colors.primary : props.theme.colors.divider};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
  
  &:hover {
    background-color: ${props => props.$selected ? props.theme.colors.primary : 'rgba(0, 0, 0, 0.05)'};
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

// Standard-Widgets
const defaultWidgets: WidgetConfig[] = [
  {
    id: 'system-status',
    type: 'systemStatus',
    title: 'System-Status',
    size: 'medium',
    minimized: false,
    position: { x: 0, y: 0 },
  },
  {
    id: 'mcp-status',
    type: 'mcpStatus',
    title: 'MCP-Server-Status',
    size: 'medium',
    minimized: false,
    position: { x: 1, y: 0 },
  },
  {
    id: 'service-status',
    type: 'serviceStatus',
    title: 'Dienste-Status',
    size: 'medium',
    minimized: false,
    position: { x: 0, y: 1 },
  },
  {
    id: 'recent-activity',
    type: 'recentActivity',
    title: 'Letzte Aktivitäten',
    size: 'medium',
    minimized: false,
    position: { x: 1, y: 1 },
  },
];

// Verfügbare Widget-Typen
const availableWidgetTypes: { type: WidgetType; title: string }[] = [
  { type: 'systemStatus', title: 'System-Status' },
  { type: 'mcpStatus', title: 'MCP-Server-Status' },
  { type: 'serviceStatus', title: 'Dienste-Status' },
  { type: 'recentActivity', title: 'Letzte Aktivitäten' },
  { type: 'quickActions', title: 'Schnellzugriff' },
  { type: 'metrics', title: 'Metriken' },
  { type: 'notifications', title: 'Benachrichtigungen' },
  { type: 'weather', title: 'Wetter' },
  { type: 'news', title: 'Neuigkeiten' },
  { type: 'custom', title: 'Benutzerdefiniert' },
];

// Dashboard-Komponente
export const Dashboard: React.FC<DashboardProps> = ({ className }) => {
  // State für Widgets
  const [widgets, setWidgets] = useState<WidgetConfig[]>([]);
  
  // State für Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedWidgetType, setSelectedWidgetType] = useState<WidgetType | null>(null);
  const [customWidgetTitle, setCustomWidgetTitle] = useState('');
  
  // Lade Widgets aus dem localStorage
  useEffect(() => {
    const savedWidgets = localStorage.getItem('dashboard-widgets');
    if (savedWidgets) {
      try {
        setWidgets(JSON.parse(savedWidgets));
      } catch (error) {
        console.error('Fehler beim Laden der Widgets:', error);
        setWidgets(defaultWidgets);
      }
    } else {
      setWidgets(defaultWidgets);
    }
  }, []);
  
  // Speichere Widgets im localStorage
  useEffect(() => {
    if (widgets.length > 0) {
      localStorage.setItem('dashboard-widgets', JSON.stringify(widgets));
    }
  }, [widgets]);
  
  // Widget hinzufügen
  const handleAddWidget = () => {
    if (!selectedWidgetType) return;
    
    const newWidget: WidgetConfig = {
      id: `${selectedWidgetType}-${Date.now()}`,
      type: selectedWidgetType,
      title: selectedWidgetType === 'custom' ? customWidgetTitle : availableWidgetTypes.find(w => w.type === selectedWidgetType)?.title || 'Widget',
      size: 'medium',
      minimized: false,
      position: { x: 0, y: widgets.length },
    };
    
    setWidgets([...widgets, newWidget]);
    setIsModalOpen(false);
    setSelectedWidgetType(null);
    setCustomWidgetTitle('');
  };
  
  // Widget entfernen
  const handleRemoveWidget = (id: string) => {
    setWidgets(widgets.filter(widget => widget.id !== id));
  };
  
  // Widget minimieren
  const handleMinimizeWidget = (id: string, minimized: boolean) => {
    setWidgets(widgets.map(widget => 
      widget.id === id ? { ...widget, minimized } : widget
    ));
  };
  
  // Widget-Größe ändern
  const handleResizeWidget = (id: string, size: WidgetSize) => {
    setWidgets(widgets.map(widget => 
      widget.id === id ? { ...widget, size } : widget
    ));
  };
  
  // Dashboard zurücksetzen
  const handleResetDashboard = () => {
    setWidgets(defaultWidgets);
  };
  
  // Rendere das entsprechende Widget basierend auf dem Typ
  const renderWidget = (widget: WidgetConfig) => {
    const commonProps = {
      id: widget.id,
      title: widget.title,
      type: widget.type,
      size: widget.size,
      minimized: widget.minimized,
      onRemove: handleRemoveWidget,
      onMinimize: handleMinimizeWidget,
      onResize: handleResizeWidget,
    };
    
    switch (widget.type) {
      case 'systemStatus':
        return <SystemStatusWidget {...commonProps} />;
      case 'mcpStatus':
        return <MCPStatusWidget {...commonProps} />;
      case 'serviceStatus':
        return <ServiceStatusWidget {...commonProps} />;
      case 'recentActivity':
        return <RecentActivityWidget {...commonProps} />;
      case 'quickActions':
        return <QuickActionsWidget {...commonProps} />;
      case 'metrics':
        return <MetricsWidget {...commonProps} />;
      case 'notifications':
        return <NotificationsWidget {...commonProps} />;
      case 'weather':
        return <WeatherWidget {...commonProps} />;
      case 'news':
        return <NewsWidget {...commonProps} />;
      case 'custom':
        return <CustomWidget {...commonProps} />;
      default:
        return null;
    }
  };
  
  return (
    <DashboardContainer className={className}>
      <DashboardHeader>
        <DashboardTitle>Dashboard</DashboardTitle>
        <DashboardActions>
          <Button 
            variant="outlined" 
            onClick={handleResetDashboard}
            aria-label="Dashboard zurücksetzen"
          >
            Zurücksetzen
          </Button>
          <Button 
            variant="primary" 
            onClick={() => setIsModalOpen(true)}
            aria-label="Widget hinzufügen"
          >
            Widget hinzufügen
          </Button>
        </DashboardActions>
      </DashboardHeader>
      
      <WidgetGrid>
        {widgets.map(widget => (
          <div key={widget.id}>
            {renderWidget(widget)}
          </div>
        ))}
      </WidgetGrid>
      
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Widget hinzufügen"
        size="md"
        footer={
          <>
            <Button 
              variant="text" 
              onClick={() => setIsModalOpen(false)}
            >
              Abbrechen
            </Button>
            <Button 
              variant="primary" 
              onClick={handleAddWidget}
              disabled={!selectedWidgetType || (selectedWidgetType === 'custom' && !customWidgetTitle)}
            >
              Hinzufügen
            </Button>
          </>
        }
      >
        <div>
          <h3>Widget-Typ auswählen</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
            {availableWidgetTypes.map(({ type, title }) => (
              <WidgetTypeButton
                key={type}
                $selected={selectedWidgetType === type}
                onClick={() => setSelectedWidgetType(type)}
              >
                {title}
              </WidgetTypeButton>
            ))}
          </div>
          
          {selectedWidgetType === 'custom' && (
            <div>
              <h3>Widget-Titel</h3>
              <input
                type="text"
                value={customWidgetTitle}
                onChange={(e) => setCustomWidgetTitle(e.target.value)}
                placeholder="Titel eingeben"
                style={{ 
                  width: '100%', 
                  padding: '8px', 
                  borderRadius: '4px', 
                  border: '1px solid #ccc',
                  marginBottom: '16px'
                }}
              />
            </div>
          )}
        </div>
      </Modal>
    </DashboardContainer>
  );
};

export default Dashboard;