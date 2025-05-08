// src/components/common/Sidebar.tsx
import React, { useState } from 'react';
import styled from 'styled-components';
import { colors, spacing, shadows, transitions, zIndex } from '../../theme';

interface SidebarProps {
  children: React.ReactNode;
  width?: number;
  open?: boolean;
  onToggle?: () => void;
  position?: 'left' | 'right';
  variant?: 'permanent' | 'temporary' | 'persistent';
  className?: string;
}

interface SidebarItemProps {
  icon?: React.ReactNode;
  label: string;
  active?: boolean;
  onClick?: () => void;
  className?: string;
}

const SidebarContainer = styled.aside<{
  $width: number;
  $open: boolean;
  $position: 'left' | 'right';
  $variant: 'permanent' | 'temporary' | 'persistent';
}>`
  display: flex;
  flex-direction: column;
  width: ${(props) => (props.$open ? `${props.$width}px` : props.$variant === 'permanent' ? `${props.$width}px` : '64px')};
  height: 100%;
  background-color: ${colors.background.paper};
  color: ${colors.text.primary};
  box-shadow: ${shadows.md};
  z-index: ${zIndex.drawer};
  overflow-x: hidden;
  overflow-y: auto;
  transition: width ${transitions.duration.standard}ms ${transitions.easing.easeInOut};
  
  ${(props) => props.$variant === 'temporary' && `
    position: fixed;
    top: 0;
    ${props.$position}: 0;
    transform: translateX(${props.$open ? '0' : props.$position === 'left' ? '-100%' : '100%'});
    transition: transform ${transitions.duration.standard}ms ${transitions.easing.easeInOut};
  `}
`;

const SidebarHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 ${spacing.md}px;
  border-bottom: 1px solid ${colors.divider};
`;

const SidebarLogo = styled.div`
  font-size: 1.25rem;
  font-weight: 500;
`;

const SidebarToggle = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  color: ${colors.text.primary};
  padding: ${spacing.xs}px;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.04);
    border-radius: 50%;
  }
  
  &:focus {
    outline: none;
  }
`;

const SidebarContent = styled.div`
  flex: 1;
  padding: ${spacing.md}px 0;
`;

const SidebarFooter = styled.div`
  padding: ${spacing.md}px;
  border-top: 1px solid ${colors.divider};
`;

const StyledSidebarItem = styled.div<{
  $active: boolean;
}>`
  display: flex;
  align-items: center;
  padding: ${spacing.sm}px ${spacing.md}px;
  cursor: pointer;
  color: ${(props) => (props.$active ? colors.primary.main : colors.text.primary)};
  background-color: ${(props) => (props.$active ? colors.primary.light + '1A' : 'transparent')};
  border-left: ${(props) => (props.$active ? `3px solid ${colors.primary.main}` : '3px solid transparent')};
  
  &:hover {
    background-color: ${(props) => (props.$active ? colors.primary.light + '1A' : 'rgba(0, 0, 0, 0.04)')};
  }
  
  .icon {
    margin-right: ${spacing.md}px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
  }
  
  .label {
    font-size: 0.875rem;
    white-space: nowrap;
  }
`;

export const SidebarItem: React.FC<SidebarItemProps> = ({
  icon,
  label,
  active = false,
  onClick,
  className,
}) => {
  return (
    <StyledSidebarItem $active={active} onClick={onClick} className={className}>
      {icon && <div className="icon">{icon}</div>}
      <div className="label">{label}</div>
    </StyledSidebarItem>
  );
};

export const Sidebar: React.FC<SidebarProps> = ({
  children,
  width = 240,
  open = true,
  onToggle,
  position = 'left',
  variant = 'persistent',
  className,
}) => {
  return (
    <SidebarContainer
      $width={width}
      $open={open}
      $position={position}
      $variant={variant}
      className={className}
    >
      <SidebarHeader>
        <SidebarLogo>Dev-Server</SidebarLogo>
        {onToggle && (
          <SidebarToggle onClick={onToggle}>
            {open ? '◀' : '▶'}
          </SidebarToggle>
        )}
      </SidebarHeader>
      <SidebarContent>{children}</SidebarContent>
    </SidebarContainer>
  );
};

export default Sidebar;