/**
 * Metrics-Widget
 * 
 * Zeigt Metriken in Form von Diagrammen an.
 */

import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import Widget, { WidgetProps } from '../Widget';

// Styled-Components für das Widget
const MetricsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
  height: 100%;
`;

const ChartContainer = styled.div`
  flex: 1;
  position: relative;
  min-height: 200px;
`;

const Canvas = styled.canvas`
  width: 100%;
  height: 100%;
`;

const MetricsTabs = styled.div`
  display: flex;
  border-bottom: 1px solid ${props => props.theme.colors.divider};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const MetricsTab = styled.button<{ $active: boolean }>`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background-color: ${props => props.$active ? props.theme.colors.background.paper : 'transparent'};
  border: none;
  border-bottom: 2px solid ${props => props.$active ? props.theme.colors.primary : 'transparent'};
  cursor: pointer;
  font-weight: ${props => props.$active ? props.theme.typography.fontWeight.medium : props.theme.typography.fontWeight.regular};
  color: ${props => props.$active ? props.theme.colors.primary : props.theme.colors.text.primary};
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.theme.colors.background.paper};
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

// Metrics-Widget-Props
export interface MetricsWidgetProps extends Omit<WidgetProps, 'children'> {}

// Metrics-Widget-Komponente
export const MetricsWidget: React.FC<MetricsWidgetProps> = (props) => {
  const [activeTab, setActiveTab] = useState<'cpu' | 'memory' | 'disk' | 'network'>('cpu');
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Simuliere Daten für Diagramme
  const generateData = (points: number) => {
    const data = [];
    let value = 50;
    
    for (let i = 0; i < points; i++) {
      // Zufällige Änderung zwischen -5 und 5
      const change = Math.random() * 10 - 5;
      
      // Stelle sicher, dass der Wert zwischen 0 und 100 bleibt
      value = Math.max(0, Math.min(100, value + change));
      
      data.push(value);
    }
    
    return data;
  };
  
  // Zeichne das Diagramm
  const drawChart = (ctx: CanvasRenderingContext2D, data: number[], color: string) => {
    const width = ctx.canvas.width;
    const height = ctx.canvas.height;
    const padding = 20;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    
    // Lösche vorheriges Diagramm
    ctx.clearRect(0, 0, width, height);
    
    // Zeichne Hintergrund
    ctx.fillStyle = '#f5f5f5';
    ctx.fillRect(padding, padding, chartWidth, chartHeight);
    
    // Zeichne Achsen
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Zeichne Linien für 25%, 50%, 75%
    ctx.strokeStyle = '#ddd';
    ctx.beginPath();
    ctx.moveTo(padding, padding + chartHeight * 0.25);
    ctx.lineTo(width - padding, padding + chartHeight * 0.25);
    ctx.moveTo(padding, padding + chartHeight * 0.5);
    ctx.lineTo(width - padding, padding + chartHeight * 0.5);
    ctx.moveTo(padding, padding + chartHeight * 0.75);
    ctx.lineTo(width - padding, padding + chartHeight * 0.75);
    ctx.stroke();
    
    // Zeichne Beschriftungen
    ctx.fillStyle = '#666';
    ctx.font = '10px Arial';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText('100%', padding - 5, padding);
    ctx.fillText('75%', padding - 5, padding + chartHeight * 0.25);
    ctx.fillText('50%', padding - 5, padding + chartHeight * 0.5);
    ctx.fillText('25%', padding - 5, padding + chartHeight * 0.75);
    ctx.fillText('0%', padding - 5, height - padding);
    
    // Zeichne Daten
    const step = chartWidth / (data.length - 1);
    
    // Zeichne Linie
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, height - padding - (data[0] / 100) * chartHeight);
    
    for (let i = 1; i < data.length; i++) {
      const x = padding + i * step;
      const y = height - padding - (data[i] / 100) * chartHeight;
      ctx.lineTo(x, y);
    }
    
    ctx.stroke();
    
    // Zeichne Fläche unter der Linie
    ctx.fillStyle = `${color}33`;
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(padding, height - padding - (data[0] / 100) * chartHeight);
    
    for (let i = 1; i < data.length; i++) {
      const x = padding + i * step;
      const y = height - padding - (data[i] / 100) * chartHeight;
      ctx.lineTo(x, y);
    }
    
    ctx.lineTo(width - padding, height - padding);
    ctx.closePath();
    ctx.fill();
  };
  
  // Aktualisiere das Diagramm
  useEffect(() => {
    if (!canvasRef.current) return;
    
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;
    
    // Setze Canvas-Größe
    const dpr = window.devicePixelRatio || 1;
    const rect = canvasRef.current.getBoundingClientRect();
    canvasRef.current.width = rect.width * dpr;
    canvasRef.current.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    
    // Generiere Daten basierend auf aktivem Tab
    const data = generateData(24);
    
    // Wähle Farbe basierend auf aktivem Tab
    let color;
    switch (activeTab) {
      case 'cpu':
        color = '#2196f3'; // Blau
        break;
      case 'memory':
        color = '#4caf50'; // Grün
        break;
      case 'disk':
        color = '#ff9800'; // Orange
        break;
      case 'network':
        color = '#9c27b0'; // Lila
        break;
      default:
        color = '#2196f3';
    }
    
    // Zeichne Diagramm
    drawChart(ctx, data, color);
    
    // Aktualisiere Diagramm alle 5 Sekunden
    const interval = setInterval(() => {
      const newData = generateData(24);
      drawChart(ctx, newData, color);
    }, 5000);
    
    return () => clearInterval(interval);
  }, [activeTab]);
  
  return (
    <Widget {...props}>
      <MetricsContainer>
        <MetricsTabs>
          <MetricsTab
            $active={activeTab === 'cpu'}
            onClick={() => setActiveTab('cpu')}
            aria-label="CPU-Auslastung anzeigen"
          >
            CPU
          </MetricsTab>
          <MetricsTab
            $active={activeTab === 'memory'}
            onClick={() => setActiveTab('memory')}
            aria-label="Speicher-Auslastung anzeigen"
          >
            Speicher
          </MetricsTab>
          <MetricsTab
            $active={activeTab === 'disk'}
            onClick={() => setActiveTab('disk')}
            aria-label="Festplatten-Auslastung anzeigen"
          >
            Festplatte
          </MetricsTab>
          <MetricsTab
            $active={activeTab === 'network'}
            onClick={() => setActiveTab('network')}
            aria-label="Netzwerk-Auslastung anzeigen"
          >
            Netzwerk
          </MetricsTab>
        </MetricsTabs>
        
        <ChartContainer>
          <Canvas ref={canvasRef} />
        </ChartContainer>
      </MetricsContainer>
    </Widget>
  );
};

export default MetricsWidget;