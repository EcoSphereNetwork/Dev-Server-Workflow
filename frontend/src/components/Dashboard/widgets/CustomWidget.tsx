/**
 * Custom-Widget
 * 
 * Ein benutzerdefiniertes Widget, das vom Benutzer angepasst werden kann.
 */

import React, { useState } from 'react';
import styled from 'styled-components';
import Widget, { WidgetProps } from '../Widget';
import { Button, Input } from '../../../design-system';

// Styled-Components für das Widget
const CustomContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const CustomContent = styled.div`
  flex: 1;
  padding: ${props => props.theme.spacing.md};
  background-color: ${props => props.theme.colors.background.paper};
  border-radius: ${props => props.theme.borderRadius.md};
  margin-bottom: ${props => props.theme.spacing.md};
  white-space: pre-wrap;
  overflow-wrap: break-word;
  overflow-y: auto;
`;

const CustomControls = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.md};
`;

const ColorPicker = styled.input`
  width: 40px;
  height: 40px;
  padding: 0;
  border: none;
  border-radius: ${props => props.theme.borderRadius.sm};
  cursor: pointer;
  
  &::-webkit-color-swatch-wrapper {
    padding: 0;
  }
  
  &::-webkit-color-swatch {
    border: none;
    border-radius: ${props => props.theme.borderRadius.sm};
  }
`;

const FontSizeSelector = styled.select`
  padding: ${props => props.theme.spacing.sm};
  border: 1px solid ${props => props.theme.colors.divider};
  border-radius: ${props => props.theme.borderRadius.sm};
  background-color: ${props => props.theme.colors.background.paper};
  color: ${props => props.theme.colors.text.primary};
  
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
`;

// Custom-Widget-Props
export interface CustomWidgetProps extends Omit<WidgetProps, 'children'> {}

// Custom-Widget-Komponente
export const CustomWidget: React.FC<CustomWidgetProps> = (props) => {
  // State für benutzerdefinierten Inhalt
  const [content, setContent] = useState<string>('Hier können Sie Ihren eigenen Text eingeben...');
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [backgroundColor, setBackgroundColor] = useState<string>('#ffffff');
  const [textColor, setTextColor] = useState<string>('#000000');
  const [fontSize, setFontSize] = useState<string>('16px');
  
  // Bearbeiten starten
  const handleEdit = () => {
    setIsEditing(true);
  };
  
  // Bearbeiten speichern
  const handleSave = () => {
    setIsEditing(false);
  };
  
  // Bearbeiten abbrechen
  const handleCancel = () => {
    setIsEditing(false);
  };
  
  return (
    <Widget {...props}>
      <CustomContainer>
        {isEditing ? (
          <>
            <Input
              as="textarea"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              style={{ 
                height: '200px', 
                backgroundColor, 
                color: textColor, 
                fontSize,
                resize: 'vertical',
              }}
            />
            <div style={{ marginTop: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <label htmlFor="background-color">Hintergrundfarbe:</label>
                <ColorPicker
                  id="background-color"
                  type="color"
                  value={backgroundColor}
                  onChange={(e) => setBackgroundColor(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <label htmlFor="text-color">Textfarbe:</label>
                <ColorPicker
                  id="text-color"
                  type="color"
                  value={textColor}
                  onChange={(e) => setTextColor(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <label htmlFor="font-size">Schriftgröße:</label>
                <FontSizeSelector
                  id="font-size"
                  value={fontSize}
                  onChange={(e) => setFontSize(e.target.value)}
                >
                  <option value="12px">Klein</option>
                  <option value="16px">Mittel</option>
                  <option value="20px">Groß</option>
                  <option value="24px">Sehr groß</option>
                </FontSizeSelector>
              </div>
            </div>
            <CustomControls>
              <Button variant="text" onClick={handleCancel}>
                Abbrechen
              </Button>
              <Button variant="primary" onClick={handleSave}>
                Speichern
              </Button>
            </CustomControls>
          </>
        ) : (
          <>
            <CustomContent
              style={{ 
                backgroundColor, 
                color: textColor, 
                fontSize,
              }}
            >
              {content}
            </CustomContent>
            <Button variant="outlined" onClick={handleEdit} fullWidth>
              Bearbeiten
            </Button>
          </>
        )}
      </CustomContainer>
    </Widget>
  );
};

export default CustomWidget;