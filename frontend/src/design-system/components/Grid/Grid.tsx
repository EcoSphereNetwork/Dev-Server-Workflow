/**
 * Grid-Komponente
 * 
 * Ein flexibles Grid-System für responsive Layouts.
 */

import React, { forwardRef, HTMLAttributes, ReactNode } from 'react';
import styled, { css } from 'styled-components';
import { Theme } from '../../theme';

// Grid-Spalten
export type GridColumns = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 'auto' | 'none';

// Grid-Ausrichtung
export type GridAlignment = 'start' | 'center' | 'end' | 'stretch';

// Grid-Verteilung
export type GridDistribution = 'start' | 'center' | 'end' | 'space-between' | 'space-around' | 'space-evenly';

// Responsive-Werte
export interface ResponsiveValue<T> {
  xs?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
}

// Grid-Container-Props
export interface GridContainerProps extends HTMLAttributes<HTMLDivElement> {
  /** Ob der Container die volle Breite einnehmen soll */
  fluid?: boolean;
  /** Der Abstand zwischen den Grid-Items */
  spacing?: ResponsiveValue<number | string>;
  /** Die Ausrichtung der Items auf der horizontalen Achse */
  justifyContent?: ResponsiveValue<GridDistribution>;
  /** Die Ausrichtung der Items auf der vertikalen Achse */
  alignItems?: ResponsiveValue<GridAlignment>;
  /** Zusätzliche CSS-Klasse */
  className?: string;
  /** Kinder-Elemente */
  children: ReactNode;
}

// Grid-Item-Props
export interface GridItemProps extends HTMLAttributes<HTMLDivElement> {
  /** Die Anzahl der Spalten, die das Item einnehmen soll */
  xs?: GridColumns;
  /** Die Anzahl der Spalten, die das Item auf Tablets einnehmen soll */
  sm?: GridColumns;
  /** Die Anzahl der Spalten, die das Item auf kleinen Desktops einnehmen soll */
  md?: GridColumns;
  /** Die Anzahl der Spalten, die das Item auf mittleren Desktops einnehmen soll */
  lg?: GridColumns;
  /** Die Anzahl der Spalten, die das Item auf großen Desktops einnehmen soll */
  xl?: GridColumns;
  /** Die Ausrichtung des Items */
  alignSelf?: ResponsiveValue<GridAlignment>;
  /** Die Reihenfolge des Items */
  order?: ResponsiveValue<number>;
  /** Zusätzliche CSS-Klasse */
  className?: string;
  /** Kinder-Elemente */
  children: ReactNode;
}

// Styled-Components für den Grid-Container
interface StyledGridContainerProps {
  $fluid: boolean;
  $spacing: ResponsiveValue<number | string>;
  $justifyContent: ResponsiveValue<GridDistribution>;
  $alignItems: ResponsiveValue<GridAlignment>;
  theme: Theme;
}

// Funktion zum Konvertieren von Spacing-Werten
const getSpacingValue = (spacing: number | string, theme: Theme) => {
  if (typeof spacing === 'number') {
    // Wenn es eine Zahl ist, multipliziere mit 8px (Basis-Spacing)
    return `${spacing * 8}px`;
  }
  
  // Wenn es ein String ist, verwende ihn direkt
  return spacing;
};

// Responsive-Styles für den Container
const getResponsiveContainerStyles = (props: StyledGridContainerProps) => {
  const { $spacing, $justifyContent, $alignItems, theme } = props;
  
  // Basis-Styles
  let styles = css`
    display: grid;
    grid-template-columns: repeat(12, 1fr);
  `;
  
  // Spacing
  if ($spacing) {
    if ($spacing.xs !== undefined) {
      styles = css`
        ${styles}
        gap: ${getSpacingValue($spacing.xs, theme)};
      `;
    }
    
    if ($spacing.sm !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.sm}) {
          gap: ${getSpacingValue($spacing.sm, theme)};
        }
      `;
    }
    
    if ($spacing.md !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.md}) {
          gap: ${getSpacingValue($spacing.md, theme)};
        }
      `;
    }
    
    if ($spacing.lg !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.lg}) {
          gap: ${getSpacingValue($spacing.lg, theme)};
        }
      `;
    }
    
    if ($spacing.xl !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.xl}) {
          gap: ${getSpacingValue($spacing.xl, theme)};
        }
      `;
    }
  }
  
  // Justify Content
  if ($justifyContent) {
    if ($justifyContent.xs !== undefined) {
      styles = css`
        ${styles}
        justify-content: ${$justifyContent.xs};
      `;
    }
    
    if ($justifyContent.sm !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.sm}) {
          justify-content: ${$justifyContent.sm};
        }
      `;
    }
    
    if ($justifyContent.md !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.md}) {
          justify-content: ${$justifyContent.md};
        }
      `;
    }
    
    if ($justifyContent.lg !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.lg}) {
          justify-content: ${$justifyContent.lg};
        }
      `;
    }
    
    if ($justifyContent.xl !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.xl}) {
          justify-content: ${$justifyContent.xl};
        }
      `;
    }
  }
  
  // Align Items
  if ($alignItems) {
    if ($alignItems.xs !== undefined) {
      styles = css`
        ${styles}
        align-items: ${$alignItems.xs};
      `;
    }
    
    if ($alignItems.sm !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.sm}) {
          align-items: ${$alignItems.sm};
        }
      `;
    }
    
    if ($alignItems.md !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.md}) {
          align-items: ${$alignItems.md};
        }
      `;
    }
    
    if ($alignItems.lg !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.lg}) {
          align-items: ${$alignItems.lg};
        }
      `;
    }
    
    if ($alignItems.xl !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.xl}) {
          align-items: ${$alignItems.xl};
        }
      `;
    }
  }
  
  return styles;
};

// Haupt-Styled-Component für den Container
const StyledGridContainer = styled.div<StyledGridContainerProps>`
  width: 100%;
  margin-right: auto;
  margin-left: auto;
  box-sizing: border-box;
  
  /* Fluid oder mit max-width */
  ${props => !props.$fluid && css`
    padding-left: ${props.theme.spacing.md};
    padding-right: ${props.theme.spacing.md};
    
    @media (min-width: ${props.theme.breakpoints.sm}) {
      max-width: 540px;
    }
    
    @media (min-width: ${props.theme.breakpoints.md}) {
      max-width: 720px;
    }
    
    @media (min-width: ${props.theme.breakpoints.lg}) {
      max-width: 960px;
    }
    
    @media (min-width: ${props.theme.breakpoints.xl}) {
      max-width: 1140px;
    }
  `}
  
  /* Responsive-Styles */
  ${getResponsiveContainerStyles}
`;

// Styled-Components für das Grid-Item
interface StyledGridItemProps {
  $xs?: GridColumns;
  $sm?: GridColumns;
  $md?: GridColumns;
  $lg?: GridColumns;
  $xl?: GridColumns;
  $alignSelf?: ResponsiveValue<GridAlignment>;
  $order?: ResponsiveValue<number>;
  theme: Theme;
}

// Funktion zum Konvertieren von Spalten-Werten
const getColumnValue = (columns: GridColumns) => {
  if (columns === 'auto') return 'auto';
  if (columns === 'none') return 'none';
  return `span ${columns} / span ${columns}`;
};

// Responsive-Styles für das Item
const getResponsiveItemStyles = (props: StyledGridItemProps) => {
  const { $xs, $sm, $md, $lg, $xl, $alignSelf, $order, theme } = props;
  
  // Basis-Styles
  let styles = css``;
  
  // Grid-Spalten
  if ($xs !== undefined) {
    styles = css`
      ${styles}
      grid-column: ${getColumnValue($xs)};
    `;
  }
  
  if ($sm !== undefined) {
    styles = css`
      ${styles}
      @media (min-width: ${theme.breakpoints.sm}) {
        grid-column: ${getColumnValue($sm)};
      }
    `;
  }
  
  if ($md !== undefined) {
    styles = css`
      ${styles}
      @media (min-width: ${theme.breakpoints.md}) {
        grid-column: ${getColumnValue($md)};
      }
    `;
  }
  
  if ($lg !== undefined) {
    styles = css`
      ${styles}
      @media (min-width: ${theme.breakpoints.lg}) {
        grid-column: ${getColumnValue($lg)};
      }
    `;
  }
  
  if ($xl !== undefined) {
    styles = css`
      ${styles}
      @media (min-width: ${theme.breakpoints.xl}) {
        grid-column: ${getColumnValue($xl)};
      }
    `;
  }
  
  // Align Self
  if ($alignSelf) {
    if ($alignSelf.xs !== undefined) {
      styles = css`
        ${styles}
        align-self: ${$alignSelf.xs};
      `;
    }
    
    if ($alignSelf.sm !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.sm}) {
          align-self: ${$alignSelf.sm};
        }
      `;
    }
    
    if ($alignSelf.md !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.md}) {
          align-self: ${$alignSelf.md};
        }
      `;
    }
    
    if ($alignSelf.lg !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.lg}) {
          align-self: ${$alignSelf.lg};
        }
      `;
    }
    
    if ($alignSelf.xl !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.xl}) {
          align-self: ${$alignSelf.xl};
        }
      `;
    }
  }
  
  // Order
  if ($order) {
    if ($order.xs !== undefined) {
      styles = css`
        ${styles}
        order: ${$order.xs};
      `;
    }
    
    if ($order.sm !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.sm}) {
          order: ${$order.sm};
        }
      `;
    }
    
    if ($order.md !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.md}) {
          order: ${$order.md};
        }
      `;
    }
    
    if ($order.lg !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.lg}) {
          order: ${$order.lg};
        }
      `;
    }
    
    if ($order.xl !== undefined) {
      styles = css`
        ${styles}
        @media (min-width: ${theme.breakpoints.xl}) {
          order: ${$order.xl};
        }
      `;
    }
  }
  
  return styles;
};

// Haupt-Styled-Component für das Item
const StyledGridItem = styled.div<StyledGridItemProps>`
  /* Responsive-Styles */
  ${getResponsiveItemStyles}
`;

// Grid-Container-Komponente
export const GridContainer = forwardRef<HTMLDivElement, GridContainerProps>(
  (
    {
      fluid = false,
      spacing,
      justifyContent,
      alignItems,
      className,
      children,
      ...rest
    },
    ref
  ) => {
    return (
      <StyledGridContainer
        ref={ref}
        $fluid={fluid}
        $spacing={spacing || {}}
        $justifyContent={justifyContent || {}}
        $alignItems={alignItems || {}}
        className={className}
        {...rest}
      >
        {children}
      </StyledGridContainer>
    );
  }
);

GridContainer.displayName = 'GridContainer';

// Grid-Item-Komponente
export const GridItem = forwardRef<HTMLDivElement, GridItemProps>(
  (
    {
      xs,
      sm,
      md,
      lg,
      xl,
      alignSelf,
      order,
      className,
      children,
      ...rest
    },
    ref
  ) => {
    return (
      <StyledGridItem
        ref={ref}
        $xs={xs}
        $sm={sm}
        $md={md}
        $lg={lg}
        $xl={xl}
        $alignSelf={alignSelf}
        $order={order}
        className={className}
        {...rest}
      >
        {children}
      </StyledGridItem>
    );
  }
);

GridItem.displayName = 'GridItem';

export default {
  Container: GridContainer,
  Item: GridItem,
};