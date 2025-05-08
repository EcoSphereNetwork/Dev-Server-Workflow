/**
 * Notifications-Widget
 * 
 * Zeigt Benachrichtigungen an.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Widget, { WidgetProps } from '../Widget';

// Benachrichtigungs-Typ
interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
  read: boolean;
}

// Styled-Components für das Widget
const NotificationList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
  max-height: 100%;
  overflow-y: auto;
`;

const NotificationItem = styled.div<{ $read: boolean; $type: 'info' | 'warning' | 'error' | 'success' }>`
  display: flex;
  padding: ${props => props.theme.spacing.sm};
  background-color: ${props => props.$read 
    ? props.theme.colors.background.paper 
    : `${props.theme.colors.primary}10`
  };
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
  opacity: ${props => props.$read ? 0.7 : 1};
  transition: background-color 0.2s;
  
  &:hover {
    background-color: ${props => props.$read 
      ? `${props.theme.colors.background.paper}80` 
      : `${props.theme.colors.primary}20`
    };
  }
`;

const NotificationIcon = styled.div<{ $type: 'info' | 'warning' | 'error' | 'success' }>`
  margin-right: ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.typography.fontSize.lg};
`;

const NotificationContent = styled.div`
  flex: 1;
`;

const NotificationTitle = styled.div`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const NotificationMessage = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
  margin-top: ${props => props.theme.spacing.xs};
`;

const NotificationMeta = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.text.secondary};
`;

const NotificationActions = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.xs};
  margin-left: ${props => props.theme.spacing.sm};
`;

const NotificationAction = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  font-size: ${props => props.theme.typography.fontSize.md};
  color: ${props => props.theme.colors.text.secondary};
  padding: ${props => props.theme.spacing.xs};
  border-radius: ${props => props.theme.borderRadius.full};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s, background-color 0.2s;
  
  &:hover {
    color: ${props => props.theme.colors.text.primary};
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const NotificationHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const NotificationCount = styled.div`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
`;

const NotificationFilter = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.xs};
`;

const FilterButton = styled.button<{ $active: boolean }>`
  background-color: ${props => props.$active ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.$active ? 'white' : props.theme.colors.text.primary};
  border: 1px solid ${props => props.$active ? props.theme.colors.primary : props.theme.colors.divider};
  border-radius: ${props => props.theme.borderRadius.sm};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.typography.fontSize.xs};
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

// Notifications-Widget-Props
export interface NotificationsWidgetProps extends Omit<WidgetProps, 'children'> {}

// Notifications-Widget-Komponente
export const NotificationsWidget: React.FC<NotificationsWidgetProps> = (props) => {
  // State für Benachrichtigungen
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  
  // Simuliere Laden von Benachrichtigungen
  useEffect(() => {
    const mockNotifications: Notification[] = [
      {
        id: '1',
        title: 'System-Update verfügbar',
        message: 'Ein neues System-Update ist verfügbar. Klicken Sie hier, um es zu installieren.',
        type: 'info',
        timestamp: new Date(Date.now() - 30 * 60000).toISOString(), // 30 Minuten zuvor
        read: false,
      },
      {
        id: '2',
        title: 'Hohe CPU-Auslastung',
        message: 'Die CPU-Auslastung ist seit 15 Minuten über 80%.',
        type: 'warning',
        timestamp: new Date(Date.now() - 15 * 60000).toISOString(), // 15 Minuten zuvor
        read: true,
      },
      {
        id: '3',
        title: 'Dienst "Affine" ausgefallen',
        message: 'Der Dienst "Affine" ist ausgefallen. Versuchen Sie, ihn neu zu starten.',
        type: 'error',
        timestamp: new Date(Date.now() - 45 * 60000).toISOString(), // 45 Minuten zuvor
        read: false,
      },
      {
        id: '4',
        title: 'Backup erfolgreich',
        message: 'Das tägliche Backup wurde erfolgreich abgeschlossen.',
        type: 'success',
        timestamp: new Date(Date.now() - 120 * 60000).toISOString(), // 2 Stunden zuvor
        read: true,
      },
      {
        id: '5',
        title: 'Neuer Benutzer registriert',
        message: 'Ein neuer Benutzer hat sich registriert und wartet auf Freigabe.',
        type: 'info',
        timestamp: new Date(Date.now() - 180 * 60000).toISOString(), // 3 Stunden zuvor
        read: false,
      },
    ];
    
    // Simuliere Laden
    setTimeout(() => {
      setNotifications(mockNotifications);
      setLoading(false);
    }, 1000);
    
    // Simuliere neue Benachrichtigungen
    const interval = setInterval(() => {
      if (Math.random() > 0.7) {
        const types: Array<'info' | 'warning' | 'error' | 'success'> = ['info', 'warning', 'error', 'success'];
        const type = types[Math.floor(Math.random() * types.length)];
        const titles = [
          'Neue Benachrichtigung',
          'System-Warnung',
          'Dienst-Status geändert',
          'Sicherheits-Update',
          'Neue Anfrage',
        ];
        const title = titles[Math.floor(Math.random() * titles.length)];
        const messages = [
          'Bitte überprüfen Sie das System.',
          'Eine Aktion ist erforderlich.',
          'Ein Dienst benötigt Ihre Aufmerksamkeit.',
          'Neue Daten verfügbar.',
          'Bitte bestätigen Sie die Änderung.',
        ];
        const message = messages[Math.floor(Math.random() * messages.length)];
        
        const newNotification: Notification = {
          id: Date.now().toString(),
          title,
          message,
          type,
          timestamp: new Date().toISOString(),
          read: false,
        };
        
        setNotifications(prevNotifications => [newNotification, ...prevNotifications]);
      }
    }, 60000);
    
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
  
  // Benachrichtigungs-Icon basierend auf Typ
  const getNotificationIcon = (type: 'info' | 'warning' | 'error' | 'success'): string => {
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
  
  // Markiere Benachrichtigung als gelesen
  const handleMarkAsRead = (id: string) => {
    setNotifications(prevNotifications => 
      prevNotifications.map(notification => 
        notification.id === id 
          ? { ...notification, read: true } 
          : notification
      )
    );
  };
  
  // Lösche Benachrichtigung
  const handleDelete = (id: string) => {
    setNotifications(prevNotifications => 
      prevNotifications.filter(notification => notification.id !== id)
    );
  };
  
  // Markiere alle als gelesen
  const handleMarkAllAsRead = () => {
    setNotifications(prevNotifications => 
      prevNotifications.map(notification => ({ ...notification, read: true }))
    );
  };
  
  // Filtere Benachrichtigungen
  const filteredNotifications = filter === 'all' 
    ? notifications 
    : notifications.filter(notification => !notification.read);
  
  // Zähle ungelesene Benachrichtigungen
  const unreadCount = notifications.filter(notification => !notification.read).length;
  
  return (
    <Widget {...props}>
      <NotificationHeader>
        <NotificationCount>
          {unreadCount} ungelesene Benachrichtigung{unreadCount !== 1 ? 'en' : ''}
        </NotificationCount>
        <NotificationFilter>
          <FilterButton
            $active={filter === 'all'}
            onClick={() => setFilter('all')}
            aria-label="Alle Benachrichtigungen anzeigen"
          >
            Alle
          </FilterButton>
          <FilterButton
            $active={filter === 'unread'}
            onClick={() => setFilter('unread')}
            aria-label="Nur ungelesene Benachrichtigungen anzeigen"
          >
            Ungelesen
          </FilterButton>
          <NotificationAction
            onClick={handleMarkAllAsRead}
            aria-label="Alle als gelesen markieren"
            title="Alle als gelesen markieren"
          >
            ✓
          </NotificationAction>
        </NotificationFilter>
      </NotificationHeader>
      
      {loading ? (
        <div>Lade Benachrichtigungen...</div>
      ) : filteredNotifications.length === 0 ? (
        <div>Keine Benachrichtigungen vorhanden.</div>
      ) : (
        <NotificationList>
          {filteredNotifications.map(notification => (
            <NotificationItem 
              key={notification.id} 
              $read={notification.read}
              $type={notification.type}
            >
              <NotificationIcon $type={notification.type}>
                {getNotificationIcon(notification.type)}
              </NotificationIcon>
              <NotificationContent>
                <NotificationTitle>{notification.title}</NotificationTitle>
                <NotificationMessage>{notification.message}</NotificationMessage>
                <NotificationMeta>
                  <span>{formatTimestamp(notification.timestamp)}</span>
                  <NotificationActions>
                    {!notification.read && (
                      <NotificationAction
                        onClick={() => handleMarkAsRead(notification.id)}
                        aria-label="Als gelesen markieren"
                        title="Als gelesen markieren"
                      >
                        ✓
                      </NotificationAction>
                    )}
                    <NotificationAction
                      onClick={() => handleDelete(notification.id)}
                      aria-label="Löschen"
                      title="Löschen"
                    >
                      🗑️
                    </NotificationAction>
                  </NotificationActions>
                </NotificationMeta>
              </NotificationContent>
            </NotificationItem>
          ))}
        </NotificationList>
      )}
    </Widget>
  );
};

export default NotificationsWidget;