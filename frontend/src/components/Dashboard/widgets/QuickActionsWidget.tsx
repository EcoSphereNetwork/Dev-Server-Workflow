/**
 * Quick-Actions-Widget
 * 
 * Zeigt Schnellzugriff-Aktionen an.
 */

import React from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import Widget, { WidgetProps } from '../Widget';

// Aktion-Typ
interface Action {
  id: string;
  name: string;
  icon: string;
  description: string;
  onClick: () => void;
}

// Styled-Components für das Widget
const ActionsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: ${props => props.theme.spacing.md};
`;

const ActionItem = styled.button`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.md};
  background-color: ${props => props.theme.colors.background.paper};
  border: 1px solid ${props => props.theme.colors.divider};
  border-radius: ${props => props.theme.borderRadius.md};
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.md};
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const ActionIcon = styled.div`
  font-size: 2rem;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const ActionName = styled.div`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  text-align: center;
`;

const ActionDescription = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.text.secondary};
  text-align: center;
  margin-top: ${props => props.theme.spacing.xs};
`;

// Quick-Actions-Widget-Props
export interface QuickActionsWidgetProps extends Omit<WidgetProps, 'children'> {}

// Quick-Actions-Widget-Komponente
export const QuickActionsWidget: React.FC<QuickActionsWidgetProps> = (props) => {
  const navigate = useNavigate();
  
  // Definiere Aktionen
  const actions: Action[] = [
    {
      id: '1',
      name: 'Dienste',
      icon: '🌐',
      description: 'Dienste verwalten',
      onClick: () => navigate('/services'),
    },
    {
      id: '2',
      name: 'MCP-Server',
      icon: '🖥️',
      description: 'MCP-Server verwalten',
      onClick: () => navigate('/mcp-servers'),
    },
    {
      id: '3',
      name: 'Workflows',
      icon: '🔄',
      description: 'Workflows verwalten',
      onClick: () => navigate('/workflows'),
    },
    {
      id: '4',
      name: 'Docker',
      icon: '🐳',
      description: 'Docker verwalten',
      onClick: () => navigate('/docker'),
    },
    {
      id: '5',
      name: 'Monitoring',
      icon: '📈',
      description: 'Monitoring anzeigen',
      onClick: () => navigate('/monitoring'),
    },
    {
      id: '6',
      name: 'Einstellungen',
      icon: '⚙️',
      description: 'Einstellungen ändern',
      onClick: () => navigate('/settings'),
    },
  ];
  
  return (
    <Widget {...props}>
      <ActionsGrid>
        {actions.map(action => (
          <ActionItem
            key={action.id}
            onClick={action.onClick}
            aria-label={action.description}
          >
            <ActionIcon>{action.icon}</ActionIcon>
            <ActionName>{action.name}</ActionName>
            <ActionDescription>{action.description}</ActionDescription>
          </ActionItem>
        ))}
      </ActionsGrid>
    </Widget>
  );
};

export default QuickActionsWidget;