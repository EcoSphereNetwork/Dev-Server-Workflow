// src/components/common/Alert.tsx
import React from 'react';
import { default as SmolituxAlert } from '../../smolitux-ui/@smolitux/core/src/components/Alert/Alert';

// Mapping der Varianten
const variantMapping = {
  'success': 'success',
  'warning': 'warning',
  'error': 'error',
  'info': 'info'
};

type AlertVariant = 'success' | 'warning' | 'error' | 'info';

interface AlertProps {
  variant?: AlertVariant;
  children: React.ReactNode;
  onClose?: () => void;
  className?: string;
  style?: React.CSSProperties;
}

export const Alert: React.FC<AlertProps> = ({
  variant = 'info',
  children,
  onClose,
  className,
  style
}) => {
  // Konvertiere die Variante in das Format, das von smolitux-ui erwartet wird
  const smolituxVariant = variantMapping[variant] || 'info';

  return (
    <SmolituxAlert
      status={smolituxVariant}
      onClose={onClose}
      className={className}
      style={style}
    >
      {children}
    </SmolituxAlert>
  );
};

export default Alert;
