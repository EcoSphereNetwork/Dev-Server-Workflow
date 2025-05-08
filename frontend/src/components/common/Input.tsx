// src/components/common/Input.tsx
import React, { forwardRef } from 'react';
import { default as SmolituxInput } from '../../smolitux-ui/@smolitux/core/src/components/Input/Input';

// Mapping der Varianten
const variantMapping = {
  'outlined': 'outline',
  'filled': 'filled',
  'standard': 'flushed'
};

// Mapping der Groessen
const sizeMapping = {
  'small': 'sm',
  'medium': 'md',
  'large': 'lg'
};

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
  error?: boolean;
  fullWidth?: boolean;
  startAdornment?: React.ReactNode;
  endAdornment?: React.ReactNode;
  variant?: 'outlined' | 'filled' | 'standard';
  size?: 'small' | 'medium' | 'large';
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      helperText,
      error = false,
      fullWidth = false,
      startAdornment,
      endAdornment,
      variant = 'outlined',
      size = 'medium',
      disabled = false,
      ...props
    },
    ref
  ) => {
    // Konvertiere die Variante und Groesse in das Format, das von smolitux-ui erwartet wird
    const smolituxVariant = variantMapping[variant] || 'outline';
    const smolituxSize = sizeMapping[size] || 'md';

    return (
      <SmolituxInput
        ref={ref}
        label={label}
        helperText={helperText}
        isInvalid={error}
        isFullWidth={fullWidth}
        leftAddon={startAdornment}
        rightAddon={endAdornment}
        variant={smolituxVariant}
        size={smolituxSize}
        isDisabled={disabled}
        {...props}
      />
    );
  }
);

Input.displayName = 'Input';

export default Input;
