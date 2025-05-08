/**
 * Input-Komponente
 * 
 * Eine zugängliche, anpassbare Input-Komponente mit Label, Hilfetexten,
 * Fehleranzeige und verschiedenen Varianten.
 */

import React, { forwardRef, InputHTMLAttributes, ReactNode, useState } from 'react';
import styled, { css } from 'styled-components';
import { Theme } from '../../theme';

// Input-Varianten
export type InputVariant = 'outlined' | 'filled' | 'standard';

// Input-Größen
export type InputSize = 'sm' | 'md' | 'lg';

// Input-Props
export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Die Variante des Inputs */
  variant?: InputVariant;
  /** Die Größe des Inputs */
  size?: InputSize;
  /** Das Label des Inputs */
  label?: ReactNode;
  /** Die Hilfetext des Inputs */
  helperText?: ReactNode;
  /** Die Fehlermeldung des Inputs */
  error?: ReactNode;
  /** Ob der Input die volle Breite einnehmen soll */
  fullWidth?: boolean;
  /** Ob der Input deaktiviert ist */
  disabled?: boolean;
  /** Ob der Input schreibgeschützt ist */
  readOnly?: boolean;
  /** Ob der Input erforderlich ist */
  required?: boolean;
  /** Icon am Anfang des Inputs */
  startIcon?: ReactNode;
  /** Icon am Ende des Inputs */
  endIcon?: ReactNode;
  /** Zusätzliche CSS-Klasse */
  className?: string;
}

// Styled-Components für den Input
interface StyledInputContainerProps {
  $variant: InputVariant;
  $size: InputSize;
  $fullWidth: boolean;
  $hasError: boolean;
  $disabled: boolean;
  $focused: boolean;
  theme: Theme;
}

// Varianten-Styles
const getVariantStyles = (props: StyledInputContainerProps) => {
  const { $variant, $hasError, $disabled, $focused, theme } = props;
  
  const errorColor = theme.colors.error;
  const primaryColor = theme.colors.primary;
  const disabledColor = theme.colors.text.disabled;
  const borderColor = $hasError 
    ? errorColor 
    : $disabled 
      ? disabledColor 
      : $focused 
        ? primaryColor 
        : theme.colors.divider;
  
  switch ($variant) {
    case 'filled':
      return css`
        background-color: ${$disabled ? 'rgba(0, 0, 0, 0.04)' : 'rgba(0, 0, 0, 0.06)'};
        border-bottom: 2px solid ${borderColor};
        border-radius: ${theme.borderRadius.sm} ${theme.borderRadius.sm} 0 0;
        
        &:hover:not(:disabled) {
          background-color: rgba(0, 0, 0, 0.09);
        }
      `;
    
    case 'standard':
      return css`
        background-color: transparent;
        border-bottom: 1px solid ${borderColor};
        border-radius: 0;
        
        &:hover:not(:disabled) {
          border-bottom: 2px solid ${$hasError ? errorColor : theme.colors.text.primary};
          margin-bottom: -1px;
        }
      `;
    
    case 'outlined':
    default:
      return css`
        background-color: transparent;
        border: 1px solid ${borderColor};
        border-radius: ${theme.borderRadius.md};
        
        &:hover:not(:disabled) {
          border-color: ${$hasError ? errorColor : theme.colors.text.primary};
        }
      `;
  }
};

// Größen-Styles
const getSizeStyles = (props: StyledInputContainerProps) => {
  const { $size, theme } = props;
  
  switch ($size) {
    case 'sm':
      return css`
        padding: ${theme.spacing.xs} ${theme.spacing.sm};
        font-size: ${theme.typography.fontSize.sm};
      `;
    
    case 'lg':
      return css`
        padding: ${theme.spacing.md} ${theme.spacing.lg};
        font-size: ${theme.typography.fontSize.lg};
      `;
    
    case 'md':
    default:
      return css`
        padding: ${theme.spacing.sm} ${theme.spacing.md};
        font-size: ${theme.typography.fontSize.md};
      `;
  }
};

// Container für den gesamten Input (inkl. Label, Helpertext, etc.)
const InputWrapper = styled.div<{ $fullWidth: boolean }>`
  display: inline-flex;
  flex-direction: column;
  position: relative;
  width: ${props => props.$fullWidth ? '100%' : 'auto'};
  min-width: 200px;
`;

// Label-Styles
const InputLabel = styled.label<{ $hasError: boolean; $disabled: boolean; $required: boolean }>`
  margin-bottom: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.typography.fontSize.sm};
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  color: ${props => {
    if (props.$hasError) return props.theme.colors.error;
    if (props.$disabled) return props.theme.colors.text.disabled;
    return props.theme.colors.text.primary;
  }};
  
  ${props => props.$required && css`
    &::after {
      content: " *";
      color: ${props.theme.colors.error};
    }
  `}
`;

// Container für den Input selbst
const StyledInputContainer = styled.div<StyledInputContainerProps>`
  display: flex;
  align-items: center;
  position: relative;
  transition: all 0.2s ease-in-out;
  
  /* Varianten-Styles */
  ${getVariantStyles}
  
  /* Größen-Styles */
  ${getSizeStyles}
  
  /* Focus-Styles */
  ${props => props.$focused && css`
    border-color: ${props.$hasError ? props.theme.colors.error : props.theme.colors.primary};
    box-shadow: 0 0 0 2px ${props.$hasError 
      ? `${props.theme.colors.error}33` 
      : `${props.theme.colors.primary}33`};
  `}
  
  /* Disabled-Styles */
  ${props => props.$disabled && css`
    opacity: 0.6;
    cursor: not-allowed;
    
    & > input {
      cursor: not-allowed;
    }
  `}
`;

// Der eigentliche Input
const StyledInput = styled.input`
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  width: 100%;
  font-family: ${props => props.theme.typography.fontFamily.primary};
  color: ${props => props.theme.colors.text.primary};
  
  &:disabled {
    color: ${props => props.theme.colors.text.disabled};
    cursor: not-allowed;
  }
  
  &::placeholder {
    color: ${props => props.theme.colors.text.hint};
  }
`;

// Icon-Container
const IconContainer = styled.div<{ $position: 'start' | 'end' }>`
  display: flex;
  align-items: center;
  justify-content: center;
  margin-${props => props.$position === 'start' ? 'right' : 'left'}: ${props => props.theme.spacing.xs};
  color: ${props => props.theme.colors.text.secondary};
`;

// Helpertext und Fehlermeldung
const HelperText = styled.div<{ $hasError: boolean; $disabled: boolean }>`
  margin-top: ${props => props.theme.spacing.xs};
  font-size: ${props => props.theme.typography.fontSize.xs};
  color: ${props => {
    if (props.$hasError) return props.theme.colors.error;
    if (props.$disabled) return props.theme.colors.text.disabled;
    return props.theme.colors.text.secondary;
  }};
`;

// Input-Komponente
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      variant = 'outlined',
      size = 'md',
      label,
      helperText,
      error,
      fullWidth = false,
      disabled = false,
      readOnly = false,
      required = false,
      startIcon,
      endIcon,
      className,
      id,
      ...rest
    },
    ref
  ) => {
    const [focused, setFocused] = useState(false);
    const hasError = !!error;
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    
    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
      setFocused(true);
      if (rest.onFocus) rest.onFocus(e);
    };
    
    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setFocused(false);
      if (rest.onBlur) rest.onBlur(e);
    };
    
    return (
      <InputWrapper $fullWidth={fullWidth} className={className}>
        {label && (
          <InputLabel 
            htmlFor={inputId}
            $hasError={hasError}
            $disabled={disabled}
            $required={required}
          >
            {label}
          </InputLabel>
        )}
        
        <StyledInputContainer
          $variant={variant}
          $size={size}
          $fullWidth={fullWidth}
          $hasError={hasError}
          $disabled={disabled}
          $focused={focused}
        >
          {startIcon && (
            <IconContainer $position="start">
              {startIcon}
            </IconContainer>
          )}
          
          <StyledInput
            ref={ref}
            id={inputId}
            disabled={disabled}
            readOnly={readOnly}
            required={required}
            aria-invalid={hasError}
            aria-describedby={helperText || error ? `${inputId}-helper-text` : undefined}
            onFocus={handleFocus}
            onBlur={handleBlur}
            {...rest}
          />
          
          {endIcon && (
            <IconContainer $position="end">
              {endIcon}
            </IconContainer>
          )}
        </StyledInputContainer>
        
        {(helperText || error) && (
          <HelperText 
            id={`${inputId}-helper-text`}
            $hasError={hasError}
            $disabled={disabled}
          >
            {error || helperText}
          </HelperText>
        )}
      </InputWrapper>
    );
  }
);

Input.displayName = 'Input';

export default Input;