/**
 * News-Widget
 * 
 * Zeigt Neuigkeiten und Updates an.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Widget, { WidgetProps } from '../Widget';

// Neuigkeit-Typ
interface NewsItem {
  id: string;
  title: string;
  summary: string;
  content: string;
  source: string;
  date: string;
  image?: string;
  url?: string;
}

// Styled-Components für das Widget
const NewsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
  max-height: 100%;
  overflow-y: auto;
`;

const NewsItemContainer = styled.div`
  display: flex;
  flex-direction: column;
  background-color: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.md};
  overflow: hidden;
  box-shadow: ${props => props.theme.shadows.sm};
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const NewsImage = styled.div<{ $image?: string }>`
  height: 150px;
  background-image: url(${props => props.$image || 'https://via.placeholder.com/400x150'});
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
`;

const NewsContent = styled.div`
  padding: ${props => props.theme.spacing.md};
`;

const NewsTitle = styled.h3`
  margin: 0 0 ${props => props.theme.spacing.sm} 0;
  font-size: ${props => props.theme.typography.fontSize.md};
  font-weight: ${props => props.theme.typography.fontWeight.bold};
`;

const NewsSummary = styled.p`
  margin: 0 0 ${props => props.theme.spacing.sm} 0;
  font-size: ${props => props.theme.typography.fontSize.sm};
  color: ${props => props.theme.colors.text.secondary};
`;

const NewsMeta = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.text.secondary};
`;

const NewsSource = styled.span``;

const NewsDate = styled.span``;

const NewsLink = styled.a`
  display: inline-block;
  margin-top: ${props => props.theme.spacing.sm};
  color: ${props => props.theme.colors.primary};
  text-decoration: none;
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  
  &:hover {
    text-decoration: underline;
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

// News-Widget-Props
export interface NewsWidgetProps extends Omit<WidgetProps, 'children'> {}

// News-Widget-Komponente
export const NewsWidget: React.FC<NewsWidgetProps> = (props) => {
  // State für Neuigkeiten
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Simuliere Laden von Neuigkeiten
  useEffect(() => {
    const mockNews: NewsItem[] = [
      {
        id: '1',
        title: 'Neue Version des Dev-Servers veröffentlicht',
        summary: 'Die neue Version 2.0 des Dev-Servers wurde veröffentlicht. Sie enthält zahlreiche Verbesserungen und neue Funktionen.',
        content: 'Die neue Version 2.0 des Dev-Servers wurde veröffentlicht. Sie enthält zahlreiche Verbesserungen und neue Funktionen, darunter eine verbesserte Benutzeroberfläche, bessere Leistung und neue Integrationen.',
        source: 'Dev-Server-Blog',
        date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 Tage zuvor
        image: 'https://via.placeholder.com/400x150?text=Dev-Server+2.0',
        url: 'https://example.com/dev-server-2.0',
      },
      {
        id: '2',
        title: 'Wartungsarbeiten am Wochenende',
        summary: 'Am kommenden Wochenende werden Wartungsarbeiten durchgeführt. Der Server wird für einige Stunden nicht verfügbar sein.',
        content: 'Am kommenden Wochenende werden Wartungsarbeiten durchgeführt. Der Server wird für einige Stunden nicht verfügbar sein. Wir empfehlen, wichtige Arbeiten vorher abzuschließen.',
        source: 'System-Administrator',
        date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 Tag zuvor
        url: 'https://example.com/maintenance',
      },
      {
        id: '3',
        title: 'Neue Integrationen verfügbar',
        summary: 'Es sind neue Integrationen für den Dev-Server verfügbar. Sie können jetzt mit weiteren Diensten verbunden werden.',
        content: 'Es sind neue Integrationen für den Dev-Server verfügbar. Sie können jetzt mit weiteren Diensten verbunden werden, darunter GitHub, GitLab, Jira und Slack.',
        source: 'Dev-Server-Team',
        date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 Tage zuvor
        image: 'https://via.placeholder.com/400x150?text=Neue+Integrationen',
        url: 'https://example.com/integrations',
      },
    ];
    
    // Simuliere Laden
    setTimeout(() => {
      setNews(mockNews);
      setLoading(false);
    }, 1000);
  }, []);
  
  // Formatiere Datum
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };
  
  return (
    <Widget {...props}>
      {loading ? (
        <div>Lade Neuigkeiten...</div>
      ) : news.length === 0 ? (
        <div>Keine Neuigkeiten verfügbar.</div>
      ) : (
        <NewsContainer>
          {news.map(item => (
            <NewsItemContainer key={item.id}>
              {item.image && <NewsImage $image={item.image} />}
              <NewsContent>
                <NewsTitle>{item.title}</NewsTitle>
                <NewsSummary>{item.summary}</NewsSummary>
                <NewsMeta>
                  <NewsSource>{item.source}</NewsSource>
                  <NewsDate>{formatDate(item.date)}</NewsDate>
                </NewsMeta>
                {item.url && (
                  <NewsLink 
                    href={item.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    aria-label={`Mehr lesen über: ${item.title}`}
                  >
                    Mehr lesen →
                  </NewsLink>
                )}
              </NewsContent>
            </NewsItemContainer>
          ))}
        </NewsContainer>
      )}
    </Widget>
  );
};

export default NewsWidget;