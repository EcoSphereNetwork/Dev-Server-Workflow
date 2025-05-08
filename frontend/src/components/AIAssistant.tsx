// src/components/AIAssistant.tsx
import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import Button from './common/Button';
import { colors, shadows, transitions } from '../theme';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

interface AIAssistantProps {
  isOpen: boolean;
  onClose: () => void;
}

const AssistantContainer = styled.div<{ $isOpen: boolean }>`
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: ${props => props.$isOpen ? '400px' : '60px'};
  height: ${props => props.$isOpen ? '600px' : '60px'};
  background-color: ${colors.background.paper};
  border-radius: 12px;
  box-shadow: ${shadows.lg};
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all ${transitions.duration.standard}ms ${transitions.easing.easeInOut};
  z-index: 1000;
`;

const AssistantHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: ${colors.primary.main};
  color: white;
`;

const AssistantTitle = styled.h3`
  margin: 0;
  font-size: 1rem;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
  
  &:hover {
    opacity: 0.8;
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const Message = styled.div<{ $sender: 'user' | 'assistant' }>`
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  align-self: ${props => props.$sender === 'user' ? 'flex-end' : 'flex-start'};
  background-color: ${props => props.$sender === 'user' ? colors.primary.main : colors.background.default};
  color: ${props => props.$sender === 'user' ? 'white' : colors.text.primary};
  box-shadow: ${shadows.sm};
`;

const InputContainer = styled.div`
  display: flex;
  padding: 12px;
  border-top: 1px solid ${colors.divider};
`;

const Input = styled.input`
  flex: 1;
  padding: 10px 14px;
  border: 1px solid ${colors.divider};
  border-radius: 20px;
  margin-right: 8px;
  
  &:focus {
    outline: none;
    border-color: ${colors.primary.main};
  }
`;

const AssistantButton = styled.button<{ $isOpen: boolean }>`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: ${colors.primary.main};
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.5rem;
  position: absolute;
  bottom: 0;
  right: 0;
  box-shadow: ${shadows.md};
  transition: transform ${transitions.duration.standard}ms ${transitions.easing.easeInOut};
  transform: ${props => props.$isOpen ? 'scale(0)' : 'scale(1)'};
  
  &:hover {
    background-color: ${colors.primary.dark};
  }
`;

const AIAssistant: React.FC<AIAssistantProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hallo! Ich bin der Dev-Server KI-Assistent. Wie kann ich dir helfen?',
      sender: 'assistant',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    
    // Hier würde in einer realen Anwendung der API-Aufruf an den KI-Assistenten erfolgen
    // Simulierte Antwort für die Entwicklung
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `Ich verarbeite deine Anfrage: "${input}"`,
        sender: 'assistant',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <>
      <AssistantContainer $isOpen={isOpen}>
        {isOpen && (
          <>
            <AssistantHeader>
              <AssistantTitle>Dev-Server KI-Assistent</AssistantTitle>
              <CloseButton onClick={onClose}>&times;</CloseButton>
            </AssistantHeader>
            <MessagesContainer>
              {messages.map(message => (
                <Message key={message.id} $sender={message.sender}>
                  {message.text}
                </Message>
              ))}
              <div ref={messagesEndRef} />
            </MessagesContainer>
            <InputContainer>
              <Input
                type="text"
                placeholder="Stelle eine Frage..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
              />
              <Button variant="primary" onClick={handleSendMessage}>
                Senden
              </Button>
            </InputContainer>
          </>
        )}
      </AssistantContainer>
      <AssistantButton $isOpen={isOpen} onClick={onClose}>
        🤖
      </AssistantButton>
    </>
  );
};

export default AIAssistant;