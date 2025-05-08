// src/components/common/Button.tsx
import React from 'react';
import { default as SmolituxButton } from '../../smolitux-ui/@smolitux/core/src/components/Button/Button';

// Mapping der Varianten
const variantMapping = {
  primary: 'primary',
  secondary: 'secondary',
  success: 'success',
  warning: 'warning',
  error: 'danger',
  info: 'info',
  text: 'ghost',
  outlined: 'outline'
};

// Mapping der Größen
const sizeMapping = {
  small: 'sm',
  medium: 'md',
  large: 'lg'
};

// Typen für die Button-Komponente
type ButtonVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' | 'text' | 'outlined';
type ButtonSize = 'small' | 'medium' | 'large';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  loading?: boolean;
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  startIcon,
  endIcon,
  loading = false,
  disabled = false,
  children,
  ...props
}) => {
  // Konvertiere die Variante und Größe in das Format, das von smolitux-ui erwartet wird
  const smolituxVariant = variantMapping[variant] || 'primary';
  const smolituxSize = sizeMapping[size] || 'md';

  return (
    <SmolituxButton
      variant={smolituxVariant}
      size={smolituxSize}
      fullWidth={fullWidth}
      leftIcon={startIcon}
      rightIcon={endIcon}
      isLoading={loading}
      disabled={disabled || loading}
      {...props}
    >
      {children}
    </SmolituxButton>
  );
};

export default Button;