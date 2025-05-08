// src/components/AIAssistant.tsx
import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { Button, Input, Card } from '../design-system';

// Typen für Nachrichten
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  isLoading?: boolean;
  actions?: Array<{
    id: string;
    label: string;
    onClick: () => void;
  }>;
}

// Typen für Vorschläge
interface Suggestion {
  id: string;
  text: string;
  onClick: () => void;
}

// Typen für Kontext
interface Context {
  page: string;
  selectedItem?: string;
  recentActions: string[];
}

// Props für den KI-Assistenten
interface AIAssistantProps {
  isOpen: boolean;
  onClose: () => void;
}

// Styled-Components für den KI-Assistenten
const AssistantContainer = styled.div<{ $isOpen: boolean }>`
  position: fixed;
  bottom: ${props => props.theme.spacing.md};
  right: ${props => props.theme.spacing.md};
  width: ${props => props.$isOpen ? '400px' : '60px'};
  height: ${props => props.$isOpen ? '600px' : '60px'};
  background-color: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.lg};
  box-shadow: ${props => props.theme.shadows.xl};
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width 0.3s ${props => props.theme.transitions.easing.easeInOut}, 
              height 0.3s ${props => props.theme.transitions.easing.easeInOut};
  z-index: ${props => props.theme.zIndex.modal - 100};
`;

const AssistantHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.md};
  background-color: ${props => props.theme.colors.primary};
  color: white;
`;

const AssistantTitle = styled.h3`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.md};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: ${props => props.theme.typography.fontSize.lg};
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    opacity: 0.8;
  }
  
  &:focus-visible {
    outline: 2px solid white;
    outline-offset: 2px;
  }
`;

const AssistantContent = styled.div<{ $isOpen: boolean }>`
  flex: 1;
  display: ${props => props.$isOpen ? 'flex' : 'none'};
  flex-direction: column;
  overflow: hidden;
`;

const MessagesContainer = styled.div`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const MessageBubble = styled.div<{ $sender: 'user' | 'assistant' }>`
  max-width: 80%;
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.lg};
  background-color: ${props => props.$sender === 'user' 
    ? props.theme.colors.primary + '20' 
    : props.theme.colors.background.default};
  align-self: ${props => props.$sender === 'user' ? 'flex-end' : 'flex-start'};
  box-shadow: ${props => props.theme.shadows.sm};
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    ${props => props.$sender === 'user' ? 'right' : 'left'}: -8px;
    width: 0;
    height: 0;
    border: 8px solid transparent;
    border-top-color: ${props => props.$sender === 'user' 
      ? props.theme.colors.primary + '20' 
      : props.theme.colors.background.default};
    border-bottom: 0;
    margin-left: -8px;
    margin-bottom: -8px;
  }
`;

const MessageText = styled.p`
  margin: 0;
  white-space: pre-wrap;
`;

const MessageTimestamp = styled.div`
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => props.theme.colors.text.secondary};
  margin-top: ${props => props.theme.spacing.xs};
  text-align: right;
`;

const MessageActions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.xs};
  margin-top: ${props => props.theme.spacing.sm};
`;

const InputContainer = styled.div`
  padding: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.divider};
`;

const SuggestionsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.xs};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const SuggestionButton = styled.button`
  background-color: ${props => props.theme.colors.background.default};
  border: 1px solid ${props => props.theme.colors.divider};
  border-radius: ${props => props.theme.borderRadius.full};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  font-size: ${props => props.theme.typography.fontSize.sm};
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.theme.colors.background.paper};
    border-color: ${props => props.theme.colors.primary};
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const AssistantButton = styled.button<{ $isOpen: boolean }>`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  cursor: pointer;
  display: ${props => props.$isOpen ? 'none' : 'flex'};
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: ${props => props.theme.shadows.md};
  transition: transform 0.2s, background-color 0.2s;
  
  &:hover {
    transform: scale(1.05);
    background-color: ${props => props.theme.colors.primaryDark};
  }
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

const LoadingDots = styled.div`
  display: inline-flex;
  align-items: center;
  
  &::after {
    content: '.';
    animation: dots 1.5s steps(5, end) infinite;
    
    @keyframes dots {
      0%, 20% { content: '.'; }
      40% { content: '..'; }
      60% { content: '...'; }
      80%, 100% { content: ''; }
    }
  }
`;

// KI-Assistent-Komponente
const AIAssistant: React.FC<AIAssistantProps> = ({ isOpen, onClose }) => {
  // State für Nachrichten und Eingabe
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Kontext für den Assistenten
  const [context, setContext] = useState<Context>({
    page: 'dashboard',
    recentActions: [],
  });
  
  // Vorschläge basierend auf dem Kontext
  const suggestions: Suggestion[] = [
    {
      id: '1',
      text: 'Wie starte ich einen Dienst?',
      onClick: () => handleSendMessage('Wie starte ich einen Dienst?'),
    },
    {
      id: '2',
      text: 'Zeige mir die Systemauslastung',
      onClick: () => handleSendMessage('Zeige mir die Systemauslastung'),
    },
    {
      id: '3',
      text: 'Hilfe zu Docker',
      onClick: () => handleSendMessage('Ich brauche Hilfe mit Docker'),
    },
    {
      id: '4',
      text: 'Workflow erstellen',
      onClick: () => handleSendMessage('Wie erstelle ich einen neuen Workflow?'),
    },
  ];
  
  // Initialisiere den Assistenten mit einer Begrüßungsnachricht
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: '0',
          text: 'Hallo! Ich bin Ihr KI-Assistent. Wie kann ich Ihnen heute helfen?',
          sender: 'assistant',
          timestamp: new Date(),
        },
      ]);
    }
  }, [messages]);
  
  // Scrolle zum Ende der Nachrichten, wenn neue Nachrichten hinzugefügt werden
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Aktualisiere den Kontext basierend auf der aktuellen Seite
  useEffect(() => {
    // In einer realen Anwendung würde hier der Kontext basierend auf der aktuellen Seite aktualisiert werden
    // Zum Beispiel durch Abfragen des Routers oder durch Übergabe als Prop
    
    // Simuliere eine Kontextaktualisierung
    const updateContext = () => {
      const pages = ['dashboard', 'services', 'mcp-servers', 'workflows', 'docker'];
      const randomPage = pages[Math.floor(Math.random() * pages.length)];
      
      setContext(prevContext => ({
        ...prevContext,
        page: randomPage,
      }));
    };
    
    // Aktualisiere den Kontext alle 30 Sekunden
    const interval = setInterval(updateContext, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  // Sende eine Nachricht
  const handleSendMessage = (text: string) => {
    if (!text.trim()) return;
    
    // Füge die Nachricht des Benutzers hinzu
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInput('');
    
    // Simuliere eine Antwort des Assistenten
    setIsTyping(true);
    
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: generateResponse(text, context),
        sender: 'assistant',
        timestamp: new Date(),
        actions: generateActions(text, context),
      };
      
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
      setIsTyping(false);
      
      // Aktualisiere den Kontext
      setContext(prevContext => ({
        ...prevContext,
        recentActions: [...prevContext.recentActions, text].slice(-5),
      }));
    }, 1000 + Math.random() * 2000); // Zufällige Verzögerung zwischen 1 und 3 Sekunden
  };
  
  // Generiere eine Antwort basierend auf der Eingabe und dem Kontext
  const generateResponse = (input: string, context: Context): string => {
    const lowerInput = input.toLowerCase();
    
    // Einfache Antwortlogik basierend auf Schlüsselwörtern
    if (lowerInput.includes('hallo') || lowerInput.includes('hi') || lowerInput.includes('hey')) {
      return 'Hallo! Wie kann ich Ihnen helfen?';
    }
    
    if (lowerInput.includes('danke') || lowerInput.includes('dank')) {
      return 'Gerne! Kann ich Ihnen noch mit etwas anderem helfen?';
    }
    
    if (lowerInput.includes('hilfe')) {
      return 'Ich kann Ihnen bei verschiedenen Aufgaben helfen, wie z.B. Dienste verwalten, Workflows erstellen oder Informationen zu Docker bereitstellen. Was möchten Sie wissen?';
    }
    
    if (lowerInput.includes('dienst') && (lowerInput.includes('start') || lowerInput.includes('starten'))) {
      return 'Um einen Dienst zu starten, gehen Sie zur Dienste-Seite, wählen Sie den gewünschten Dienst aus und klicken Sie auf den "Starten"-Button. Alternativ können Sie auch auf der Detailseite des Dienstes den "Starten"-Button verwenden.';
    }
    
    if (lowerInput.includes('dienst') && (lowerInput.includes('stop') || lowerInput.includes('stoppen'))) {
      return 'Um einen Dienst zu stoppen, gehen Sie zur Dienste-Seite, wählen Sie den laufenden Dienst aus und klicken Sie auf den "Stoppen"-Button. Alternativ können Sie auch auf der Detailseite des Dienstes den "Stoppen"-Button verwenden.';
    }
    
    if (lowerInput.includes('docker')) {
      return 'Docker ist eine Plattform zur Containerisierung von Anwendungen. In unserem System können Sie Docker-Container über die Docker-Seite verwalten. Dort können Sie Container starten, stoppen, erstellen und löschen. Was möchten Sie genau mit Docker machen?';
    }
    
    if (lowerInput.includes('workflow') && (lowerInput.includes('erstell') || lowerInput.includes('neu'))) {
      return 'Um einen neuen Workflow zu erstellen, gehen Sie zur Workflows-Seite und klicken Sie auf den "Neuer Workflow"-Button. Dort können Sie dann die einzelnen Schritte des Workflows definieren und konfigurieren.';
    }
    
    if (lowerInput.includes('system') && (lowerInput.includes('auslastung') || lowerInput.includes('status'))) {
      return 'Die aktuelle Systemauslastung können Sie auf dem Dashboard einsehen. Dort finden Sie Widgets für CPU-Auslastung, Speichernutzung und Festplattennutzung. Möchten Sie detailliertere Informationen sehen, können Sie zur Monitoring-Seite wechseln.';
    }
    
    // Kontextbasierte Antworten
    if (context.page === 'dashboard') {
      return 'Auf dem Dashboard können Sie einen Überblick über Ihr System erhalten. Sie sehen hier wichtige Metriken und den Status Ihrer Dienste. Sie können die Widgets nach Ihren Bedürfnissen anpassen, indem Sie auf "Widget hinzufügen" klicken oder bestehende Widgets verschieben.';
    }
    
    if (context.page === 'services') {
      return 'Auf der Dienste-Seite können Sie alle integrierten Dienste verwalten. Sie können Dienste starten, stoppen, neustarten oder deren Details anzeigen. Wenn Sie einen neuen Dienst hinzufügen möchten, klicken Sie auf den "Neuen Dienst hinzufügen"-Button.';
    }
    
    // Fallback-Antwort
    return 'Ich verstehe Ihre Anfrage nicht vollständig. Können Sie bitte genauer erläutern, wobei Sie Hilfe benötigen?';
  };
  
  // Generiere Aktionen basierend auf der Eingabe und dem Kontext
  const generateActions = (input: string, context: Context) => {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('dienst') && (lowerInput.includes('start') || lowerInput.includes('starten'))) {
      return [
        {
          id: 'action-1',
          label: 'Zur Dienste-Seite',
          onClick: () => {
            // In einer realen Anwendung würde hier zur Dienste-Seite navigiert werden
            console.log('Navigiere zur Dienste-Seite');
          },
        },
      ];
    }
    
    if (lowerInput.includes('docker')) {
      return [
        {
          id: 'action-2',
          label: 'Docker-Dokumentation öffnen',
          onClick: () => {
            window.open('https://docs.docker.com', '_blank');
          },
        },
        {
          id: 'action-3',
          label: 'Zur Docker-Seite',
          onClick: () => {
            // In einer realen Anwendung würde hier zur Docker-Seite navigiert werden
            console.log('Navigiere zur Docker-Seite');
          },
        },
      ];
    }
    
    return [];
  };
  
  // Formatiere Zeitstempel
  const formatTimestamp = (date: Date): string => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  return (
    <AssistantContainer $isOpen={isOpen}>
      {isOpen ? (
        <>
          <AssistantHeader>
            <AssistantTitle>KI-Assistent</AssistantTitle>
            <CloseButton onClick={onClose} aria-label="Assistent schließen">
              &times;
            </CloseButton>
          </AssistantHeader>
          
          <AssistantContent $isOpen={isOpen}>
            <MessagesContainer>
              {messages.map(message => (
                <MessageBubble key={message.id} $sender={message.sender}>
                  <MessageText>
                    {message.isLoading ? <LoadingDots>Schreibe</LoadingDots> : message.text}
                  </MessageText>
                  <MessageTimestamp>{formatTimestamp(message.timestamp)}</MessageTimestamp>
                  
                  {message.actions && message.actions.length > 0 && (
                    <MessageActions>
                      {message.actions.map(action => (
                        <Button
                          key={action.id}
                          variant="outlined"
                          size="sm"
                          onClick={action.onClick}
                        >
                          {action.label}
                        </Button>
                      ))}
                    </MessageActions>
                  )}
                </MessageBubble>
              ))}
              
              {isTyping && (
                <MessageBubble $sender="assistant">
                  <LoadingDots>Schreibe</LoadingDots>
                </MessageBubble>
              )}
              
              <div ref={messagesEndRef} />
            </MessagesContainer>
            
            <InputContainer>
              <SuggestionsContainer>
                {suggestions.map(suggestion => (
                  <SuggestionButton
                    key={suggestion.id}
                    onClick={suggestion.onClick}
                  >
                    {suggestion.text}
                  </SuggestionButton>
                ))}
              </SuggestionsContainer>
              
              <Input
                placeholder="Nachricht eingeben..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSendMessage(input);
                  }
                }}
                endIcon={
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleSendMessage(input)}
                    disabled={!input.trim()}
                  >
                    Senden
                  </Button>
                }
              />
            </InputContainer>
          </AssistantContent>
        </>
      ) : (
        <AssistantButton
          $isOpen={isOpen}
          onClick={onClose}
          aria-label="KI-Assistent öffnen"
        >
          🤖
        </AssistantButton>
      )}
    </AssistantContainer>
  );
};

export default AIAssistant;