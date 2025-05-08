// src/components/common/Card.tsx
import React from 'react';
import { default as SmolituxCard } from '../../smolitux-ui/@smolitux/core/src/components/Card/Card';

// Mapping der Elevation zu Shadow
const elevationMapping = {
  'none': 'none',
  'sm': 'sm',
  'md': 'md',
  'lg': 'lg'
};

// Mapping des Paddings
const paddingMapping = {
  'none': false,
  'sm': 'sm',
  'md': 'md',
  'lg': 'lg'
};

interface CardProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  elevation?: 'none' | 'sm' | 'md' | 'lg';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  footer,
  elevation = 'md',
  padding = 'md',
  fullWidth = false,
  className,
}) => {
  // Konvertiere die Werte in das Format, das von smolitux-ui erwartet wird
  const noPadding = padding === 'none';
  
  return (
    <SmolituxCard
      title={title}
      subtitle={subtitle}
      footer={footer}
      noPadding={noPadding}
      className={className}
      style={{ 
        width: fullWidth ? '100%' : 'auto',
        boxShadow: elevation !== 'none' ? `var(--shadow-${elevationMapping[elevation]})` : 'none'
      }}
    >
      {children}
    </SmolituxCard>
  );
};

export default Card;