/**
 * Container-Komponente
 * 
 * Eine responsive Container-Komponente, die den Inhalt zentriert und
 * eine maximale Breite auf verschiedenen Bildschirmgrößen festlegt.
 */

import React, { forwardRef, HTMLAttributes, ReactNode } from 'react';
import styled, { css } from 'styled-components';
import { Theme } from '../../theme';

// Container-Größen
export type ContainerSize = 'sm' | 'md' | 'lg' | 'xl' | 'fluid';

// Container-Props
export interface ContainerProps extends HTMLAttributes<HTMLDivElement> {
  /** Die Größe des Containers */
  size?: ContainerSize;
  /** Ob der Container Padding haben soll */
  noPadding?: boolean;
  /** Zusätzliche CSS-Klasse */
  className?: string;
  /** Kinder-Elemente */
  children: ReactNode;
}

// Styled-Components für den Container
interface StyledContainerProps {
  $size: ContainerSize;
  $noPadding: boolean;
  theme: Theme;
}

// Größen-Styles
const getSizeStyles = (props: StyledContainerProps) => {
  const { $size, theme } = props;
  
  switch ($size) {
    case 'sm':
      return css`
        max-width: 540px;
      `;
    
    case 'md':
      return css`
        max-width: 720px;
        
        @media (max-width: ${theme.breakpoints.md}) {
          max-width: 540px;
        }
      `;
    
    case 'lg':
      return css`
        max-width: 960px;
        
        @media (max-width: ${theme.breakpoints.lg}) {
          max-width: 720px;
        }
        
        @media (max-width: ${theme.breakpoints.md}) {
          max-width: 540px;
        }
      `;
    
    case 'xl':
      return css`
        max-width: 1140px;
        
        @media (max-width: ${theme.breakpoints.xl}) {
          max-width: 960px;
        }
        
        @media (max-width: ${theme.breakpoints.lg}) {
          max-width: 720px;
        }
        
        @media (max-width: ${theme.breakpoints.md}) {
          max-width: 540px;
        }
      `;
    
    case 'fluid':
      return css`
        max-width: none;
      `;
    
    default:
      return css`
        max-width: 1140px;
        
        @media (max-width: ${theme.breakpoints.xl}) {
          max-width: 960px;
        }
        
        @media (max-width: ${theme.breakpoints.lg}) {
          max-width: 720px;
        }
        
        @media (max-width: ${theme.breakpoints.md}) {
          max-width: 540px;
        }
      `;
  }
};

// Haupt-Styled-Component
const StyledContainer = styled.div<StyledContainerProps>`
  width: 100%;
  margin-right: auto;
  margin-left: auto;
  box-sizing: border-box;
  
  /* Padding */
  padding-left: ${props => props.$noPadding ? '0' : props.theme.spacing.md};
  padding-right: ${props => props.$noPadding ? '0' : props.theme.spacing.md};
  
  /* Größen-Styles */
  ${getSizeStyles}
`;

// Container-Komponente
export const Container = forwardRef<HTMLDivElement, ContainerProps>(
  (
    {
      size = 'lg',
      noPadding = false,
      className,
      children,
      ...rest
    },
    ref
  ) => {
    return (
      <StyledContainer
        ref={ref}
        $size={size}
        $noPadding={noPadding}
        className={className}
        {...rest}
      >
        {children}
      </StyledContainer>
    );
  }
);

Container.displayName = 'Container';

export default Container;