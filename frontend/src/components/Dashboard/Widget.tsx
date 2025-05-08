/**
 * Dashboard-Widget-Komponente
 * 
 * Eine anpassbare Widget-Komponente für das Dashboard.
 */

import React, { useState } from 'react';
import styled from 'styled-components';
import { Card } from '../../design-system';

// Widget-Größen
export type WidgetSize = 'small' | 'medium' | 'large' | 'full';

// Widget-Typen
export type WidgetType = 
  | 'systemStatus' 
  | 'mcpStatus' 
  | 'serviceStatus' 
  | 'recentActivity'
  | 'quickActions'
  | 'metrics'
  | 'notifications'
  | 'weather'
  | 'news'
  | 'custom';

// Widget-Props
export interface WidgetProps {
  /** Die ID des Widgets */
  id: string;
  /** Der Titel des Widgets */
  title: string;
  /** Der Typ des Widgets */
  type: WidgetType;
  /** Die Größe des Widgets */
  size?: WidgetSize;
  /** Ob das Widget minimiert ist */
  minimized?: boolean;
  /** Ob das Widget anpassbar ist */
  customizable?: boolean;
  /** Ob das Widget entfernt werden kann */
  removable?: boolean;
  /** Callback beim Entfernen des Widgets */
  onRemove?: (id: string) => void;
  /** Callback beim Minimieren des Widgets */
  onMinimize?: (id: string, minimized: boolean) => void;
  /** Callback beim Ändern der Größe des Widgets */
  onResize?: (id: string, size: WidgetSize) => void;
  /** Zusätzliche CSS-Klasse */
  className?: string;
  /** Kinder-Elemente (der Inhalt des Widgets) */
  children: React.ReactNode;
}

// Styled-Components für das Widget
const WidgetContainer = styled(Card)<{ $size: WidgetSize; $minimized: boolean }>`
  height: ${props => props.$minimized ? 'auto' : getWidgetHeight(props.$size)};
  transition: height 0.3s ease-in-out;
  margin-bottom: ${props => props.theme.spacing.md};
  
  ${props => props.$minimized && `
    .widget-content {
      display: none;
    }
  `}
`;

// Widget-Header
const WidgetHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

// Widget-Titel
const WidgetTitle = styled.h3`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.md};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

// Widget-Aktionen
const WidgetActions = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
`;

// Widget-Aktion
const WidgetAction = styled.button`
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

// Widget-Inhalt
const WidgetContent = styled.div`
  padding-top: ${props => props.theme.spacing.md};
  height: 100%;
`;

// Funktion zum Ermitteln der Widget-Höhe
const getWidgetHeight = (size: WidgetSize): string => {
  switch (size) {
    case 'small':
      return '200px';
    case 'medium':
      return '300px';
    case 'large':
      return '400px';
    case 'full':
      return '100%';
    default:
      return '300px';
  }
};

// Widget-Komponente
export const Widget: React.FC<WidgetProps> = ({
  id,
  title,
  type,
  size = 'medium',
  minimized = false,
  customizable = true,
  removable = true,
  onRemove,
  onMinimize,
  onResize,
  className,
  children,
}) => {
  const [isMinimized, setIsMinimized] = useState(minimized);
  const [currentSize, setCurrentSize] = useState(size);
  
  // Minimieren-Handler
  const handleMinimize = () => {
    const newMinimized = !isMinimized;
    setIsMinimized(newMinimized);
    if (onMinimize) {
      onMinimize(id, newMinimized);
    }
  };
  
  // Größe-ändern-Handler
  const handleResize = () => {
    const sizes: WidgetSize[] = ['small', 'medium', 'large', 'full'];
    const currentIndex = sizes.indexOf(currentSize);
    const nextIndex = (currentIndex + 1) % sizes.length;
    const newSize = sizes[nextIndex];
    
    setCurrentSize(newSize);
    if (onResize) {
      onResize(id, newSize);
    }
  };
  
  // Entfernen-Handler
  const handleRemove = () => {
    if (onRemove) {
      onRemove(id);
    }
  };
  
  return (
    <WidgetContainer
      $size={currentSize}
      $minimized={isMinimized}
      className={className}
      headerActions={
        <WidgetActions>
          {customizable && (
            <WidgetAction
              onClick={handleResize}
              aria-label={`Widget-Größe ändern (aktuell: ${currentSize})`}
              title="Größe ändern"
            >
              {currentSize === 'small' ? '🔍' : currentSize === 'medium' ? '📊' : currentSize === 'large' ? '📈' : '📉'}
            </WidgetAction>
          )}
          <WidgetAction
            onClick={handleMinimize}
            aria-label={isMinimized ? 'Widget maximieren' : 'Widget minimieren'}
            title={isMinimized ? 'Maximieren' : 'Minimieren'}
          >
            {isMinimized ? '🔽' : '🔼'}
          </WidgetAction>
          {removable && (
            <WidgetAction
              onClick={handleRemove}
              aria-label="Widget entfernen"
              title="Entfernen"
            >
              ❌
            </WidgetAction>
          )}
        </WidgetActions>
      }
      title={title}
    >
      <WidgetContent className="widget-content">
        {children}
      </WidgetContent>
    </WidgetContainer>
  );
};

export default Widget;