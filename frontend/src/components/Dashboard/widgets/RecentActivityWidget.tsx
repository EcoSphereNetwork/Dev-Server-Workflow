/**
 * Recent-Activity-Widget
 * 
 * Zeigt die letzten Aktivitäten an.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Widget, { WidgetProps } from '../Widget';

// Aktivitäts-Typ
interface Activity {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: string;
  user?: string;
  service?: string;
}

// Styled-Components für das Widget
const ActivityList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
  max-height: 100%;
  overflow-y: auto;
`;

const ActivityItem = styled.div<{ $type: 'info' | 'warning' | 'error' | 'success' }>`
  display: flex;
  padding: ${props => props.theme.spacing.sm};
  background-color: ${props => {
    switch (props.$type) {
      case 'info':
        return `${props.theme.colors.info.light}20`;
      case 'warning':
        return `${props.theme.colors.warning.light}20`;
      case 'error':
        return `${props.theme.colors.error}20`;
      case 'success':
        return `${props.theme.colors.success.light}20`;
      default:
        return props.theme.colors.background.paper;
    }
  }};
  border-left: 4px solid ${props => {
    switch (props.$type) {
      case 'info':
        return props.theme.colors.info.main;
      case 'warning':
        return props.theme.colors.warning.main;
      case 'error':
        return props.theme.colors.error;
      case 'success':
        return props.theme.colors.success.main;
      default:
        return props.theme.colors.primary;
    }
  }};
  border-radius: ${props => props.theme.borderRadius.sm};
`;

const ActivityIcon = styled.div<{ $type: 'info' | 'warning' | 'error' | 'success' }>`
  margin-right: ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.typography.fontSize.lg};
`;

const ActivityContent = styled.div`
  flex: 1;
`;

const ActivityMessage = styled.div`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const ActivityMeta = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.text.secondary};
`;

// Recent-Activity-Widget-Props
export interface RecentActivityWidgetProps extends Omit<WidgetProps, 'children'> {}

// Recent-Activity-Widget-Komponente
export const RecentActivityWidget: React.FC<RecentActivityWidgetProps> = (props) => {
  // State für Aktivitäten
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Simuliere Laden von Aktivitäten
  useEffect(() => {
    const mockActivities: Activity[] = [
      {
        id: '1',
        type: 'success',
        message: 'Dienst "n8n" erfolgreich gestartet',
        timestamp: new Date(Date.now() - 5 * 60000).toISOString(), // 5 Minuten zuvor
        user: 'admin',
        service: 'n8n',
      },
      {
        id: '2',
        type: 'error',
        message: 'Fehler beim Starten von "Affine"',
        timestamp: new Date(Date.now() - 15 * 60000).toISOString(), // 15 Minuten zuvor
        user: 'system',
        service: 'Affine',
      },
      {
        id: '3',
        type: 'warning',
        message: 'Hohe CPU-Auslastung erkannt',
        timestamp: new Date(Date.now() - 30 * 60000).toISOString(), // 30 Minuten zuvor
        user: 'system',
      },
      {
        id: '4',
        type: 'info',
        message: 'Backup erfolgreich abgeschlossen',
        timestamp: new Date(Date.now() - 60 * 60000).toISOString(), // 1 Stunde zuvor
        user: 'system',
      },
      {
        id: '5',
        type: 'success',
        message: 'Workflow "Daten-Import" erfolgreich ausgeführt',
        timestamp: new Date(Date.now() - 90 * 60000).toISOString(), // 1,5 Stunden zuvor
        user: 'admin',
        service: 'n8n',
      },
    ];
    
    // Simuliere Laden
    setTimeout(() => {
      setActivities(mockActivities);
      setLoading(false);
    }, 1000);
    
    // Simuliere neue Aktivitäten
    const interval = setInterval(() => {
      const types: Array<'info' | 'warning' | 'error' | 'success'> = ['info', 'warning', 'error', 'success'];
      const type = types[Math.floor(Math.random() * types.length)];
      const services = ['n8n', 'AppFlowy', 'OpenProject', 'GitLab', 'Affine'];
      const service = services[Math.floor(Math.random() * services.length)];
      const messages = [
        `Dienst "${service}" gestartet`,
        `Dienst "${service}" gestoppt`,
        `Workflow in "${service}" ausgeführt`,
        `Neue Daten in "${service}" importiert`,
        `Konfiguration von "${service}" geändert`,
      ];
      const message = messages[Math.floor(Math.random() * messages.length)];
      
      const newActivity: Activity = {
        id: Date.now().toString(),
        type,
        message,
        timestamp: new Date().toISOString(),
        user: Math.random() > 0.5 ? 'admin' : 'system',
        service,
      };
      
      setActivities(prevActivities => [newActivity, ...prevActivities].slice(0, 10));
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Formatiere Zeitstempel
  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Gerade eben';
    if (diffMins < 60) return `Vor ${diffMins} Minuten`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `Vor ${diffHours} Stunden`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `Vor ${diffDays} Tagen`;
  };
  
  // Aktivitäts-Icon basierend auf Typ
  const getActivityIcon = (type: 'info' | 'warning' | 'error' | 'success'): string => {
    switch (type) {
      case 'info':
        return 'ℹ️';
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      case 'success':
        return '✅';
      default:
        return 'ℹ️';
    }
  };
  
  return (
    <Widget {...props}>
      {loading ? (
        <div>Lade Aktivitäten...</div>
      ) : (
        <ActivityList>
          {activities.map(activity => (
            <ActivityItem key={activity.id} $type={activity.type}>
              <ActivityIcon $type={activity.type}>
                {getActivityIcon(activity.type)}
              </ActivityIcon>
              <ActivityContent>
                <ActivityMessage>{activity.message}</ActivityMessage>
                <ActivityMeta>
                  <span>{formatTimestamp(activity.timestamp)}</span>
                  <span>{activity.user}</span>
                </ActivityMeta>
              </ActivityContent>
            </ActivityItem>
          ))}
        </ActivityList>
      )}
    </Widget>
  );
};

export default RecentActivityWidget;