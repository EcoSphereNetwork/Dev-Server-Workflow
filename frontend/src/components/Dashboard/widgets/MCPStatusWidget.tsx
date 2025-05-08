/**
 * MCP-Status-Widget
 * 
 * Zeigt den Status der MCP-Server an.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Widget, { WidgetProps } from '../Widget';

// MCP-Server-Typ
interface MCPServer {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'warning';
  lastSeen: string;
  type: string;
}

// Styled-Components für das Widget
const ServerList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
  max-height: 100%;
  overflow-y: auto;
`;

const ServerItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.sm};
  background-color: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.sm};
  box-shadow: ${props => props.theme.shadows.sm};
`;

const ServerInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const ServerName = styled.span`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const ServerType = styled.span`
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
`;

const ServerStatus = styled.div<{ $status: 'online' | 'offline' | 'warning' }>`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  
  &::before {
    content: '';
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: ${props => {
      switch (props.$status) {
        case 'online':
          return props.theme.colors.success.main;
        case 'warning':
          return props.theme.colors.warning.main;
        case 'offline':
          return props.theme.colors.error;
        default:
          return props.theme.colors.success.main;
      }
    }};
  }
`;

const LastSeen = styled.span`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.text.secondary};
`;

// MCP-Status-Widget-Props
export interface MCPStatusWidgetProps extends Omit<WidgetProps, 'children'> {}

// MCP-Status-Widget-Komponente
export const MCPStatusWidget: React.FC<MCPStatusWidgetProps> = (props) => {
  // State für MCP-Server
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Simuliere Laden von MCP-Servern
  useEffect(() => {
    const mockServers: MCPServer[] = [
      {
        id: '1',
        name: 'MCP-Server 1',
        status: 'online',
        lastSeen: new Date().toISOString(),
        type: 'Docker',
      },
      {
        id: '2',
        name: 'MCP-Server 2',
        status: 'warning',
        lastSeen: new Date().toISOString(),
        type: 'n8n',
      },
      {
        id: '3',
        name: 'MCP-Server 3',
        status: 'offline',
        lastSeen: new Date(Date.now() - 3600000).toISOString(), // 1 Stunde zuvor
        type: 'LLM',
      },
      {
        id: '4',
        name: 'MCP-Server 4',
        status: 'online',
        lastSeen: new Date().toISOString(),
        type: 'Prompt',
      },
    ];
    
    // Simuliere Laden
    setTimeout(() => {
      setServers(mockServers);
      setLoading(false);
    }, 1000);
    
    // Simuliere Status-Updates
    const interval = setInterval(() => {
      setServers(prevServers => 
        prevServers.map(server => ({
          ...server,
          status: Math.random() > 0.8 
            ? (Math.random() > 0.5 ? 'warning' : 'offline') 
            : 'online',
          lastSeen: server.status !== 'offline' 
            ? new Date().toISOString() 
            : server.lastSeen,
        }))
      );
    }, 10000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Formatiere Zeitstempel
  const formatLastSeen = (timestamp: string): string => {
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
  
  return (
    <Widget {...props}>
      {loading ? (
        <div>Lade MCP-Server...</div>
      ) : (
        <ServerList>
          {servers.map(server => (
            <ServerItem key={server.id}>
              <ServerInfo>
                <ServerName>{server.name}</ServerName>
                <ServerType>{server.type}</ServerType>
              </ServerInfo>
              <div>
                <ServerStatus $status={server.status}>
                  {server.status === 'online' ? 'Online' : server.status === 'warning' ? 'Warnung' : 'Offline'}
                </ServerStatus>
                <LastSeen>{formatLastSeen(server.lastSeen)}</LastSeen>
              </div>
            </ServerItem>
          ))}
        </ServerList>
      )}
    </Widget>
  );
};

export default MCPStatusWidget;