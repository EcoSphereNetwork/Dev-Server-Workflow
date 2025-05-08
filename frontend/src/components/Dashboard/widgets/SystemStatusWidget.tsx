/**
 * System-Status-Widget
 * 
 * Zeigt den Status des Systems an.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Widget, { WidgetProps } from '../Widget';

// Styled-Components für das Widget
const StatusContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.sm};
  background-color: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.sm};
  box-shadow: ${props => props.theme.shadows.sm};
`;

const StatusLabel = styled.span`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const StatusValue = styled.span<{ $status: 'good' | 'warning' | 'error' }>`
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
        case 'good':
          return props.theme.colors.success.main;
        case 'warning':
          return props.theme.colors.warning.main;
        case 'error':
          return props.theme.colors.error;
        default:
          return props.theme.colors.success.main;
      }
    }};
  }
`;

// System-Status-Widget-Props
export interface SystemStatusWidgetProps extends Omit<WidgetProps, 'children'> {}

// System-Status-Widget-Komponente
export const SystemStatusWidget: React.FC<SystemStatusWidgetProps> = (props) => {
  // State für System-Status
  const [cpuUsage, setCpuUsage] = useState(0);
  const [memoryUsage, setMemoryUsage] = useState(0);
  const [diskUsage, setDiskUsage] = useState(0);
  const [networkStatus, setNetworkStatus] = useState<'good' | 'warning' | 'error'>('good');
  
  // Simuliere System-Status-Updates
  useEffect(() => {
    const interval = setInterval(() => {
      setCpuUsage(Math.floor(Math.random() * 100));
      setMemoryUsage(Math.floor(Math.random() * 100));
      setDiskUsage(Math.floor(Math.random() * 100));
      setNetworkStatus(Math.random() > 0.8 ? 'warning' : 'good');
    }, 5000);
    
    // Initiale Werte
    setCpuUsage(Math.floor(Math.random() * 100));
    setMemoryUsage(Math.floor(Math.random() * 100));
    setDiskUsage(Math.floor(Math.random() * 100));
    setNetworkStatus('good');
    
    return () => clearInterval(interval);
  }, []);
  
  // Bestimme Status basierend auf Nutzung
  const getCpuStatus = (): 'good' | 'warning' | 'error' => {
    if (cpuUsage < 50) return 'good';
    if (cpuUsage < 80) return 'warning';
    return 'error';
  };
  
  const getMemoryStatus = (): 'good' | 'warning' | 'error' => {
    if (memoryUsage < 50) return 'good';
    if (memoryUsage < 80) return 'warning';
    return 'error';
  };
  
  const getDiskStatus = (): 'good' | 'warning' | 'error' => {
    if (diskUsage < 70) return 'good';
    if (diskUsage < 90) return 'warning';
    return 'error';
  };
  
  return (
    <Widget {...props}>
      <StatusContainer>
        <StatusItem>
          <StatusLabel>CPU-Auslastung</StatusLabel>
          <StatusValue $status={getCpuStatus()}>
            {cpuUsage}%
          </StatusValue>
        </StatusItem>
        
        <StatusItem>
          <StatusLabel>Speicher-Auslastung</StatusLabel>
          <StatusValue $status={getMemoryStatus()}>
            {memoryUsage}%
          </StatusValue>
        </StatusItem>
        
        <StatusItem>
          <StatusLabel>Festplatten-Auslastung</StatusLabel>
          <StatusValue $status={getDiskStatus()}>
            {diskUsage}%
          </StatusValue>
        </StatusItem>
        
        <StatusItem>
          <StatusLabel>Netzwerk-Status</StatusLabel>
          <StatusValue $status={networkStatus}>
            {networkStatus === 'good' ? 'Gut' : networkStatus === 'warning' ? 'Eingeschränkt' : 'Fehler'}
          </StatusValue>
        </StatusItem>
      </StatusContainer>
    </Widget>
  );
};

export default SystemStatusWidget;