/**
 * Button-Komponente
 * 
 * Eine zugängliche, anpassbare Button-Komponente, die verschiedene Varianten,
 * Größen und Zustände unterstützt.
 */

import React, { forwardRef, ButtonHTMLAttributes, ReactNode } from 'react';
import styled, { css } from 'styled-components';
import { Theme } from '../../theme';

// Button-Varianten
export type ButtonVariant = 'primary' | 'secondary' | 'outlined' | 'text' | 'error';

// Button-Größen
export type ButtonSize = 'sm' | 'md' | 'lg';

// Button-Props
export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Die Variante des Buttons */
  variant?: ButtonVariant;
  /** Die Größe des Buttons */
  size?: ButtonSize;
  /** Ob der Button die volle Breite einnehmen soll */
  fullWidth?: boolean;
  /** Ob der Button deaktiviert ist */
  disabled?: boolean;
  /** Ob der Button gerade lädt */
  isLoading?: boolean;
  /** Icon vor dem Text */
  startIcon?: ReactNode;
  /** Icon nach dem Text */
  endIcon?: ReactNode;
  /** Zusätzliche CSS-Klasse */
  className?: string;
  /** Kinder-Elemente (in der Regel der Text) */
  children: ReactNode;
}

// Styled-Components für den Button
interface StyledButtonProps {
  $variant: ButtonVariant;
  $size: ButtonSize;
  $fullWidth: boolean;
  $isLoading: boolean;
  theme: Theme;
}

// Varianten-Styles
const getVariantStyles = (props: StyledButtonProps) => {
  const { $variant, theme } = props;
  
  switch ($variant) {
    case 'primary':
      return css`
        background-color: ${theme.colors.primary};
        color: white;
        border: none;
        
        &:hover:not(:disabled) {
          background-color: ${theme.colors.primaryDark};
        }
        
        &:active:not(:disabled) {
          background-color: ${theme.colors.primaryDark};
          transform: translateY(1px);
        }
      `;
    
    case 'secondary':
      return css`
        background-color: ${theme.colors.secondary};
        color: white;
        border: none;
        
        &:hover:not(:disabled) {
          background-color: ${theme.colors.secondaryDark};
        }
        
        &:active:not(:disabled) {
          background-color: ${theme.colors.secondaryDark};
          transform: translateY(1px);
        }
      `;
    
    case 'outlined':
      return css`
        background-color: transparent;
        color: ${theme.colors.primary};
        border: 1px solid ${theme.colors.primary};
        
        &:hover:not(:disabled) {
          background-color: rgba(33, 150, 243, 0.04);
        }
        
        &:active:not(:disabled) {
          background-color: rgba(33, 150, 243, 0.12);
          transform: translateY(1px);
        }
      `;
    
    case 'text':
      return css`
        background-color: transparent;
        color: ${theme.colors.primary};
        border: none;
        
        &:hover:not(:disabled) {
          background-color: rgba(33, 150, 243, 0.04);
        }
        
        &:active:not(:disabled) {
          background-color: rgba(33, 150, 243, 0.12);
          transform: translateY(1px);
        }
      `;
    
    case 'error':
      return css`
        background-color: ${theme.colors.error};
        color: white;
        border: none;
        
        &:hover:not(:disabled) {
          background-color: ${theme.colors.error}e0;
        }
        
        &:active:not(:disabled) {
          background-color: ${theme.colors.error}e0;
          transform: translateY(1px);
        }
      `;
    
    default:
      return css`
        background-color: ${theme.colors.primary};
        color: white;
        border: none;
        
        &:hover:not(:disabled) {
          background-color: ${theme.colors.primaryDark};
        }
        
        &:active:not(:disabled) {
          background-color: ${theme.colors.primaryDark};
          transform: translateY(1px);
        }
      `;
  }
};

// Größen-Styles
const getSizeStyles = (props: StyledButtonProps) => {
  const { $size, theme } = props;
  
  switch ($size) {
    case 'sm':
      return css`
        padding: ${theme.spacing.xs} ${theme.spacing.sm};
        font-size: ${theme.typography.fontSize.sm};
      `;
    
    case 'md':
      return css`
        padding: ${theme.spacing.sm} ${theme.spacing.md};
        font-size: ${theme.typography.fontSize.md};
      `;
    
    case 'lg':
      return css`
        padding: ${theme.spacing.md} ${theme.spacing.lg};
        font-size: ${theme.typography.fontSize.lg};
      `;
    
    default:
      return css`
        padding: ${theme.spacing.sm} ${theme.spacing.md};
        font-size: ${theme.typography.fontSize.md};
      `;
  }
};

// Loading-Styles
const getLoadingStyles = (props: StyledButtonProps) => {
  const { $isLoading } = props;
  
  if ($isLoading) {
    return css`
      position: relative;
      color: transparent;
      pointer-events: none;
      
      &::after {
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        width: 1em;
        height: 1em;
        margin-top: -0.5em;
        margin-left: -0.5em;
        border-radius: 50%;
        border: 2px solid currentColor;
        border-color: transparent currentColor currentColor currentColor;
        animation: button-loading-spinner 0.6s linear infinite;
      }
      
      @keyframes button-loading-spinner {
        from {
          transform: rotate(0deg);
        }
        to {
          transform: rotate(360deg);
        }
      }
    `;
  }
  
  return '';
};

// Haupt-Styled-Component
const StyledButton = styled.button<StyledButtonProps>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-sizing: border-box;
  outline: 0;
  border-radius: ${props => props.theme.borderRadius.md};
  cursor: pointer;
  user-select: none;
  vertical-align: middle;
  text-decoration: none;
  font-family: ${props => props.theme.typography.fontFamily.primary};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  line-height: 1.75;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  min-width: 64px;
  transition: background-color 0.25s, box-shadow 0.25s, border-color 0.25s;
  
  /* Varianten-Styles */
  ${getVariantStyles}
  
  /* Größen-Styles */
  ${getSizeStyles}
  
  /* Volle Breite */
  width: ${props => props.$fullWidth ? '100%' : 'auto'};
  
  /* Loading-Styles */
  ${getLoadingStyles}
  
  /* Deaktiviert-Styles */
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    box-shadow: none;
  }
  
  /* Focus-Styles für Barrierefreiheit */
  &:focus-visible {
    outline: 2px solid ${props => props.theme.colors.primary};
    outline-offset: 2px;
  }
  
  /* Icon-Styles */
  .button-start-icon {
    margin-right: ${props => props.theme.spacing.xs};
    display: inline-flex;
  }
  
  .button-end-icon {
    margin-left: ${props => props.theme.spacing.xs};
    display: inline-flex;
  }
`;

// Button-Komponente
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      fullWidth = false,
      disabled = false,
      isLoading = false,
      startIcon,
      endIcon,
      className,
      children,
      ...rest
    },
    ref
  ) => {
    return (
      <StyledButton
        ref={ref}
        $variant={variant}
        $size={size}
        $fullWidth={fullWidth}
        $isLoading={isLoading}
        disabled={disabled || isLoading}
        className={className}
        {...rest}
      >
        {startIcon && <span className="button-start-icon">{startIcon}</span>}
        {children}
        {endIcon && <span className="button-end-icon">{endIcon}</span>}
      </StyledButton>
    );
  }
);

Button.displayName = 'Button';

export default Button;