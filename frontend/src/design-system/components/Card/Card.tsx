/**
 * Card-Komponente
 * 
 * Eine anpassbare Card-Komponente für die Darstellung von Inhalten in einem
 * abgegrenzten Bereich mit optionalem Header, Footer und verschiedenen Varianten.
 */

import React, { forwardRef, HTMLAttributes, ReactNode } from 'react';
import styled, { css } from 'styled-components';
import { Theme } from '../../theme';

// Card-Varianten
export type CardVariant = 'default' | 'outlined' | 'elevated';

// Card-Props
export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /** Die Variante der Card */
  variant?: CardVariant;
  /** Der Titel der Card (wird im Header angezeigt) */
  title?: ReactNode;
  /** Zusätzliche Aktionen im Header (z.B. Buttons) */
  headerActions?: ReactNode;
  /** Der Footer der Card */
  footer?: ReactNode;
  /** Ob die Card einen Rahmen haben soll */
  noBorder?: boolean;
  /** Ob die Card einen Schatten haben soll */
  noShadow?: boolean;
  /** Ob die Card Padding haben soll */
  noPadding?: boolean;
  /** Zusätzliche CSS-Klasse */
  className?: string;
  /** Kinder-Elemente (der Inhalt der Card) */
  children: ReactNode;
}

// Styled-Components für die Card
interface StyledCardProps {
  $variant: CardVariant;
  $noBorder: boolean;
  $noShadow: boolean;
  $noPadding: boolean;
  theme: Theme;
}

// Varianten-Styles
const getVariantStyles = (props: StyledCardProps) => {
  const { $variant, $noBorder, $noShadow, theme } = props;
  
  switch ($variant) {
    case 'outlined':
      return css`
        background-color: ${theme.colors.surface};
        border: ${$noBorder ? 'none' : `1px solid ${theme.colors.divider}`};
        box-shadow: ${$noShadow ? 'none' : theme.shadows.sm};
      `;
    
    case 'elevated':
      return css`
        background-color: ${theme.colors.surface};
        border: ${$noBorder ? 'none' : 'none'};
        box-shadow: ${$noShadow ? 'none' : theme.shadows.lg};
      `;
    
    case 'default':
    default:
      return css`
        background-color: ${theme.colors.surface};
        border: ${$noBorder ? 'none' : `1px solid ${theme.colors.divider}`};
        box-shadow: ${$noShadow ? 'none' : theme.shadows.md};
      `;
  }
};

// Haupt-Styled-Component
const StyledCard = styled.div<StyledCardProps>`
  display: flex;
  flex-direction: column;
  position: relative;
  border-radius: ${props => props.theme.borderRadius.md};
  overflow: hidden;
  
  /* Varianten-Styles */
  ${getVariantStyles}
  
  /* Transition für Hover-Effekte */
  transition: box-shadow 0.3s ease-in-out, transform 0.3s ease-in-out;
`;

// Card-Header
const CardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.md};
  border-bottom: 1px solid ${props => props.theme.colors.divider};
`;

const CardTitle = styled.h3`
  margin: 0;
  font-size: ${props => props.theme.typography.fontSize.lg};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  color: ${props => props.theme.colors.text.primary};
`;

const CardHeaderActions = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

// Card-Content
const CardContent = styled.div<{ $noPadding: boolean }>`
  flex: 1;
  padding: ${props => props.$noPadding ? '0' : props.theme.spacing.md};
`;

// Card-Footer
const CardFooter = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: ${props => props.theme.spacing.md};
  border-top: 1px solid ${props => props.theme.colors.divider};
  gap: ${props => props.theme.spacing.sm};
`;

// Card-Komponente
export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = 'default',
      title,
      headerActions,
      footer,
      noBorder = false,
      noShadow = false,
      noPadding = false,
      className,
      children,
      ...rest
    },
    ref
  ) => {
    const hasHeader = title || headerActions;
    
    return (
      <StyledCard
        ref={ref}
        $variant={variant}
        $noBorder={noBorder}
        $noShadow={noShadow}
        $noPadding={noPadding}
        className={className}
        {...rest}
      >
        {hasHeader && (
          <CardHeader>
            {title && <CardTitle>{title}</CardTitle>}
            {headerActions && <CardHeaderActions>{headerActions}</CardHeaderActions>}
          </CardHeader>
        )}
        
        <CardContent $noPadding={noPadding}>
          {children}
        </CardContent>
        
        {footer && <CardFooter>{footer}</CardFooter>}
      </StyledCard>
    );
  }
);

Card.displayName = 'Card';

export default Card;