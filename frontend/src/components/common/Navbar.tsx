// src/components/common/Navbar.tsx
import React from 'react';
import styled from 'styled-components';
import { colors, spacing, shadows, zIndex } from '../../theme';

interface NavbarProps {
  children?: React.ReactNode;
  position?: 'fixed' | 'absolute' | 'sticky' | 'static' | 'relative';
  color?: 'primary' | 'secondary' | 'default' | 'transparent';
  elevation?: boolean;
  className?: string;
}

const getBackgroundColor = (color: 'primary' | 'secondary' | 'default' | 'transparent') => {
  switch (color) {
    case 'primary':
      return colors.primary.main;
    case 'secondary':
      return colors.secondary.main;
    case 'default':
      return colors.background.paper;
    case 'transparent':
      return 'transparent';
    default:
      return colors.background.paper;
  }
};

const getTextColor = (color: 'primary' | 'secondary' | 'default' | 'transparent') => {
  switch (color) {
    case 'primary':
      return colors.primary.contrastText;
    case 'secondary':
      return colors.secondary.contrastText;
    case 'default':
    case 'transparent':
      return colors.text.primary;
    default:
      return colors.text.primary;
  }
};

const NavbarContainer = styled.header<{
  $position: 'fixed' | 'absolute' | 'sticky' | 'static' | 'relative';
  $color: 'primary' | 'secondary' | 'default' | 'transparent';
  $elevation: boolean;
}>`
  display: flex;
  align-items: center;
  width: 100%;
  height: 64px;
  padding: 0 ${spacing.md}px;
  position: ${(props) => props.$position};
  top: 0;
  left: 0;
  right: 0;
  z-index: ${zIndex.appBar};
  background-color: ${(props) => getBackgroundColor(props.$color)};
  color: ${(props) => getTextColor(props.$color)};
  box-shadow: ${(props) => (props.$elevation ? shadows.sm : 'none')};
`;

export const Navbar: React.FC<NavbarProps> = ({
  children,
  position = 'static',
  color = 'default',
  elevation = true,
  className,
}) => {
  return (
    <NavbarContainer
      $position={position}
      $color={color}
      $elevation={elevation}
      className={className}
    >
      {children}
    </NavbarContainer>
  );
};

export default Navbar;