/**
 * Modal-Komponente
 * 
 * Eine barrierefreie Modal-Komponente mit Fokus-Trap und Keyboard-Navigation.
 */

import React, { forwardRef, HTMLAttributes, ReactNode, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { createPortal } from 'react-dom';
import { useFocusTrap } from '../../hooks/useA11y';
import { Theme } from '../../theme';

// Modal-Größen
export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

// Modal-Props
export interface ModalProps extends HTMLAttributes<HTMLDivElement> {
  /** Ob das Modal geöffnet ist */
  isOpen: boolean;
  /** Callback beim Schließen des Modals */
  onClose: () => void;
  /** Der Titel des Modals */
  title?: ReactNode;
  /** Die Größe des Modals */
  size?: ModalSize;
  /** Ob das Modal beim Klick auf den Hintergrund geschlossen werden soll */
  closeOnBackdropClick?: boolean;
  /** Ob das Modal beim Drücken der Escape-Taste geschlossen werden soll */
  closeOnEsc?: boolean;
  /** Ob das Modal zentriert werden soll */
  centered?: boolean;
  /** Ob das Modal einen Schließen-Button haben soll */
  showCloseButton?: boolean;
  /** Der Footer des Modals */
  footer?: ReactNode;
  /** Zusätzliche CSS-Klasse */
  className?: string;
  /** Kinder-Elemente (der Inhalt des Modals) */
  children: ReactNode;
}

// Styled-Components für das Modal
interface StyledModalProps {
  $size: ModalSize;
  $centered: boolean;
  theme: Theme;
}

// Größen-Styles
const getModalSize = (size: ModalSize, theme: Theme) => {
  switch (size) {
    case 'sm':
      return '300px';
    case 'md':
      return '500px';
    case 'lg':
      return '800px';
    case 'xl':
      return '1100px';
    case 'full':
      return '90%';
    default:
      return '500px';
  }
};

// Modal-Backdrop
const ModalBackdrop = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: ${props => props.$centered ? 'center' : 'flex-start'};
  justify-content: center;
  z-index: ${props => props.theme.zIndex.modal};
  overflow-y: auto;
  padding: ${props => props.theme.spacing.md};
  box-sizing: border-box;
`;

// Modal-Container
const ModalContainer = styled.div<StyledModalProps>`
  background-color: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.md};
  box-shadow: ${props => props.theme.shadows.xl};
  width: 100%;
  max-width: ${props => getModalSize(props.$size, props.theme)};
  max-height: ${props => props.$size === 'full' ? '90%' : 'auto'};
  margin: ${props => props.$centered ? '0' : `${props.theme.spacing.xl} 0`};
  display: flex;
  flex-direction: column;
  overflow: hidden;
  
  @media (max-width: ${props => props.theme.breakpoints.sm}) {
    max-width: 100%;
    border-radius: ${props => props.$size === 'full' ? '0' : props.theme.borderRadius.md};
  }
`;

// Modal-Header
const ModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.md};
  border-bottom: 1px solid ${props => props.theme.colors.divider};
`;

// Modal-Titel
const ModalTitle = styled.h2`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  color: ${props => props.theme.colors.text.primary};
`;

// Schließen-Button
const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  font-size: ${props => props.theme.typography.fontSize.xl};
  color: ${props => props.theme.colors.text.secondary};
  padding: ${props => props.theme.spacing.xs};
  margin: -${props => props.theme.spacing.xs};
  border-radius: ${props => props.theme.borderRadius.sm};
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

// Modal-Body
const ModalBody = styled.div`
  padding: ${props => props.theme.spacing.md};
  overflow-y: auto;
  flex: 1;
`;

// Modal-Footer
const ModalFooter = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.divider};
  gap: ${props => props.theme.spacing.sm};
`;

// Modal-Komponente
export const Modal = forwardRef<HTMLDivElement, ModalProps>(
  (
    {
      isOpen,
      onClose,
      title,
      size = 'md',
      closeOnBackdropClick = true,
      closeOnEsc = true,
      centered = true,
      showCloseButton = true,
      footer,
      className,
      children,
      ...rest
    },
    ref
  ) => {
    // Verwende den Fokus-Trap-Hook
    const { containerRef } = useFocusTrap(isOpen);
    
    // Speichere das vorherige aktive Element
    const previousActiveElement = useRef<HTMLElement | null>(null);
    
    // Event-Handler für Escape-Taste
    const handleKeyDown = (event: KeyboardEvent) => {
      if (closeOnEsc && event.key === 'Escape') {
        onClose();
      }
    };
    
    // Event-Handler für Klick auf den Hintergrund
    const handleBackdropClick = (event: React.MouseEvent<HTMLDivElement>) => {
      if (closeOnBackdropClick && event.target === event.currentTarget) {
        onClose();
      }
    };
    
    // Füge Event-Listener hinzu und speichere das vorherige aktive Element
    useEffect(() => {
      if (isOpen) {
        // Speichere das vorherige aktive Element
        previousActiveElement.current = document.activeElement as HTMLElement;
        
        // Füge Event-Listener für Escape-Taste hinzu
        document.addEventListener('keydown', handleKeyDown);
        
        // Verhindere das Scrollen des Body
        document.body.style.overflow = 'hidden';
        
        // Cleanup
        return () => {
          document.removeEventListener('keydown', handleKeyDown);
          document.body.style.overflow = '';
          
          // Fokussiere das vorherige aktive Element
          if (previousActiveElement.current) {
            previousActiveElement.current.focus();
          }
        };
      }
    }, [isOpen, closeOnEsc]);
    
    // Rendere nichts, wenn das Modal geschlossen ist
    if (!isOpen) return null;
    
    // Rendere das Modal in einem Portal
    return createPortal(
      <ModalBackdrop 
        $centered={centered} 
        onClick={handleBackdropClick}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
      >
        <ModalContainer
          ref={(node) => {
            // Setze beide Refs
            if (typeof ref === 'function') {
              ref(node);
            } else if (ref) {
              ref.current = node;
            }
            containerRef.current = node;
          }}
          $size={size}
          $centered={centered}
          className={className}
          {...rest}
        >
          {(title || showCloseButton) && (
            <ModalHeader>
              {title && <ModalTitle id="modal-title">{title}</ModalTitle>}
              {showCloseButton && (
                <CloseButton 
                  onClick={onClose}
                  aria-label="Schließen"
                >
                  &times;
                </CloseButton>
              )}
            </ModalHeader>
          )}
          
          <ModalBody>
            {children}
          </ModalBody>
          
          {footer && <ModalFooter>{footer}</ModalFooter>}
        </ModalContainer>
      </ModalBackdrop>,
      document.body
    );
  }
);

Modal.displayName = 'Modal';

export default Modal;