/**
 * Accessibility utilities for improving application accessibility.
 */

import { useEffect, useRef, useState, KeyboardEvent } from 'react';

/**
 * Custom hook for managing focus trapping within a component.
 * 
 * @param active Whether the focus trap is active
 * @param options Configuration options
 * @returns Ref to attach to the container element
 */
export function useFocusTrap<T extends HTMLElement>(
  active: boolean = true,
  options: {
    initialFocus?: () => HTMLElement | null;
    returnFocus?: boolean;
    escapeDeactivates?: boolean;
    onDeactivate?: () => void;
  } = {}
) {
  const containerRef = useRef<T>(null);
  const previousActiveElement = useRef<Element | null>(null);

  useEffect(() => {
    if (!active || !containerRef.current) {
      return;
    }

    // Save current active element to restore focus later
    previousActiveElement.current = document.activeElement;

    // Get all focusable elements within the container
    const getFocusableElements = () => {
      if (!containerRef.current) return [];
      
      return Array.from(
        containerRef.current.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )
      ).filter(el => !el.hasAttribute('disabled') && el.getAttribute('tabindex') !== '-1');
    };

    // Set initial focus
    const setInitialFocus = () => {
      if (options.initialFocus) {
        const initialElement = options.initialFocus();
        if (initialElement) {
          initialElement.focus();
          return;
        }
      }

      // If no initial focus element is specified, focus the first focusable element
      const focusableElements = getFocusableElements();
      if (focusableElements.length > 0) {
        focusableElements[0].focus();
      }
    };

    // Handle tab key to keep focus within the container
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        const focusableElements = getFocusableElements();
        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        // If shift+tab on first element, move to last element
        if (event.shiftKey && document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
        // If tab on last element, move to first element
        else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
      // Handle escape key to deactivate the focus trap
      else if (event.key === 'Escape' && options.escapeDeactivates) {
        if (options.onDeactivate) {
          options.onDeactivate();
        }
      }
    };

    // Set initial focus
    setInitialFocus();

    // Add event listener for keydown
    const container = containerRef.current;
    container.addEventListener('keydown', handleKeyDown as any);

    return () => {
      // Remove event listener
      container.removeEventListener('keydown', handleKeyDown as any);

      // Restore focus when the focus trap is deactivated
      if (options.returnFocus !== false && previousActiveElement.current instanceof HTMLElement) {
        previousActiveElement.current.focus();
      }
    };
  }, [active, options.initialFocus, options.returnFocus, options.escapeDeactivates, options.onDeactivate]);

  return containerRef;
}

/**
 * Custom hook for managing keyboard navigation in lists.
 * 
 * @param itemCount Number of items in the list
 * @param options Configuration options
 * @returns Object with current index and key event handler
 */
export function useKeyboardNavigation(
  itemCount: number,
  options: {
    initialIndex?: number;
    vertical?: boolean;
    horizontal?: boolean;
    loop?: boolean;
    onSelect?: (index: number) => void;
  } = {}
) {
  const [currentIndex, setCurrentIndex] = useState(options.initialIndex || 0);

  const handleKeyDown = (event: KeyboardEvent) => {
    let newIndex = currentIndex;

    // Vertical navigation (up/down)
    if (options.vertical !== false) {
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        newIndex = currentIndex + 1;
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        newIndex = currentIndex - 1;
      }
    }

    // Horizontal navigation (left/right)
    if (options.horizontal !== false) {
      if (event.key === 'ArrowRight') {
        event.preventDefault();
        newIndex = currentIndex + 1;
      } else if (event.key === 'ArrowLeft') {
        event.preventDefault();
        newIndex = currentIndex - 1;
      }
    }

    // Handle looping
    if (options.loop) {
      if (newIndex < 0) {
        newIndex = itemCount - 1;
      } else if (newIndex >= itemCount) {
        newIndex = 0;
      }
    } else {
      // Clamp index without looping
      newIndex = Math.max(0, Math.min(itemCount - 1, newIndex));
    }

    // Update index if changed
    if (newIndex !== currentIndex) {
      setCurrentIndex(newIndex);
    }

    // Handle selection (Enter or Space)
    if ((event.key === 'Enter' || event.key === ' ') && options.onSelect) {
      event.preventDefault();
      options.onSelect(currentIndex);
    }
  };

  return {
    currentIndex,
    setCurrentIndex,
    handleKeyDown
  };
}

/**
 * Custom hook for announcing messages to screen readers.
 * 
 * @returns Function to announce messages
 */
export function useAnnouncer() {
  const [announcements, setAnnouncements] = useState<string[]>([]);
  
  useEffect(() => {
    // Create or get the announcer element
    let announcer = document.getElementById('a11y-announcer');
    if (!announcer) {
      announcer = document.createElement('div');
      announcer.id = 'a11y-announcer';
      announcer.setAttribute('aria-live', 'polite');
      announcer.setAttribute('aria-atomic', 'true');
      announcer.style.position = 'absolute';
      announcer.style.width = '1px';
      announcer.style.height = '1px';
      announcer.style.padding = '0';
      announcer.style.overflow = 'hidden';
      announcer.style.clip = 'rect(0, 0, 0, 0)';
      announcer.style.whiteSpace = 'nowrap';
      announcer.style.border = '0';
      document.body.appendChild(announcer);
    }
    
    // Update the announcer with the latest announcement
    if (announcements.length > 0) {
      const latestAnnouncement = announcements[announcements.length - 1];
      announcer.textContent = latestAnnouncement;
      
      // Clear announcements after a delay
      const timerId = setTimeout(() => {
        setAnnouncements([]);
      }, 3000);
      
      return () => clearTimeout(timerId);
    }
  }, [announcements]);
  
  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    setAnnouncements(prev => [...prev, message]);
    
    // For assertive announcements, also use the assertive announcer
    if (priority === 'assertive') {
      let assertiveAnnouncer = document.getElementById('a11y-announcer-assertive');
      if (!assertiveAnnouncer) {
        assertiveAnnouncer = document.createElement('div');
        assertiveAnnouncer.id = 'a11y-announcer-assertive';
        assertiveAnnouncer.setAttribute('aria-live', 'assertive');
        assertiveAnnouncer.setAttribute('aria-atomic', 'true');
        assertiveAnnouncer.style.position = 'absolute';
        assertiveAnnouncer.style.width = '1px';
        assertiveAnnouncer.style.height = '1px';
        assertiveAnnouncer.style.padding = '0';
        assertiveAnnouncer.style.overflow = 'hidden';
        assertiveAnnouncer.style.clip = 'rect(0, 0, 0, 0)';
        assertiveAnnouncer.style.whiteSpace = 'nowrap';
        assertiveAnnouncer.style.border = '0';
        document.body.appendChild(assertiveAnnouncer);
      }
      
      assertiveAnnouncer.textContent = message;
    }
  };
  
  return announce;
}

/**
 * Custom hook for managing skip links for keyboard navigation.
 * 
 * @param links Array of skip link configurations
 * @returns Object with refs to attach to target elements
 */
export function useSkipLinks(
  links: Array<{ id: string; label: string }>
) {
  const refs = links.reduce<Record<string, React.RefObject<HTMLElement>>>((acc, link) => {
    acc[link.id] = useRef<HTMLElement>(null);
    return acc;
  }, {});
  
  useEffect(() => {
    // Create skip link container if it doesn't exist
    let skipLinkContainer = document.getElementById('skip-link-container');
    if (!skipLinkContainer) {
      skipLinkContainer = document.createElement('div');
      skipLinkContainer.id = 'skip-link-container';
      skipLinkContainer.style.position = 'absolute';
      skipLinkContainer.style.top = '0';
      skipLinkContainer.style.left = '0';
      skipLinkContainer.style.zIndex = '9999';
      document.body.prepend(skipLinkContainer);
    }
    
    // Clear existing skip links
    skipLinkContainer.innerHTML = '';
    
    // Create skip links
    links.forEach(link => {
      const skipLink = document.createElement('a');
      skipLink.href = `#${link.id}`;
      skipLink.textContent = link.label;
      skipLink.className = 'skip-link';
      skipLink.style.position = 'absolute';
      skipLink.style.top = '-40px';
      skipLink.style.left = '0';
      skipLink.style.padding = '8px 16px';
      skipLink.style.background = '#000';
      skipLink.style.color = '#fff';
      skipLink.style.zIndex = '9999';
      skipLink.style.textDecoration = 'none';
      skipLink.style.transition = 'top 0.2s';
      skipLink.style.borderRadius = '0 0 4px 0';
      skipLink.style.fontWeight = 'bold';
      
      // Show skip link on focus
      skipLink.addEventListener('focus', () => {
        skipLink.style.top = '0';
      });
      
      // Hide skip link on blur
      skipLink.addEventListener('blur', () => {
        skipLink.style.top = '-40px';
      });
      
      // Handle click to focus target element
      skipLink.addEventListener('click', (event) => {
        event.preventDefault();
        const targetRef = refs[link.id];
        if (targetRef && targetRef.current) {
          targetRef.current.tabIndex = -1;
          targetRef.current.focus();
          targetRef.current.scrollIntoView({ behavior: 'smooth' });
        }
      });
      
      skipLinkContainer.appendChild(skipLink);
    });
    
    return () => {
      // Clean up skip links on unmount
      if (skipLinkContainer) {
        skipLinkContainer.innerHTML = '';
      }
    };
  }, [links, refs]);
  
  return refs;
}

/**
 * Utility for checking contrast ratio between two colors.
 * 
 * @param foreground Foreground color in hex format
 * @param background Background color in hex format
 * @returns Contrast ratio
 */
export function getContrastRatio(foreground: string, background: string): number {
  // Convert hex to RGB
  const hexToRgb = (hex: string): [number, number, number] => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return [r, g, b];
  };
  
  // Calculate relative luminance
  const getLuminance = (rgb: [number, number, number]): number => {
    const [r, g, b] = rgb.map(c => {
      const channel = c / 255;
      return channel <= 0.03928
        ? channel / 12.92
        : Math.pow((channel + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  
  const foregroundRgb = hexToRgb(foreground);
  const backgroundRgb = hexToRgb(background);
  
  const foregroundLuminance = getLuminance(foregroundRgb);
  const backgroundLuminance = getLuminance(backgroundRgb);
  
  const lighter = Math.max(foregroundLuminance, backgroundLuminance);
  const darker = Math.min(foregroundLuminance, backgroundLuminance);
  
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Utility for checking if a contrast ratio meets WCAG standards.
 * 
 * @param ratio Contrast ratio
 * @param level WCAG level (AA or AAA)
 * @param size Text size (normal or large)
 * @returns Whether the contrast ratio meets the standard
 */
export function meetsContrastStandard(
  ratio: number,
  level: 'AA' | 'AAA' = 'AA',
  size: 'normal' | 'large' = 'normal'
): boolean {
  if (level === 'AA') {
    return size === 'normal' ? ratio >= 4.5 : ratio >= 3;
  } else {
    return size === 'normal' ? ratio >= 7 : ratio >= 4.5;
  }
}

/**
 * Utility for generating accessible color combinations.
 * 
 * @param baseColor Base color in hex format
 * @param targetContrast Target contrast ratio
 * @returns Object with foreground and background colors
 */
export function generateAccessibleColors(
  baseColor: string,
  targetContrast: number = 4.5
): { foreground: string; background: string } {
  // Convert hex to RGB
  const hexToRgb = (hex: string): [number, number, number] => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return [r, g, b];
  };
  
  // Convert RGB to hex
  const rgbToHex = (rgb: [number, number, number]): string => {
    return '#' + rgb.map(c => {
      const hex = Math.round(c).toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join('');
  };
  
  // Calculate relative luminance
  const getLuminance = (rgb: [number, number, number]): number => {
    const [r, g, b] = rgb.map(c => {
      const channel = c / 255;
      return channel <= 0.03928
        ? channel / 12.92
        : Math.pow((channel + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  
  const baseRgb = hexToRgb(baseColor);
  const baseLuminance = getLuminance(baseRgb);
  
  // Determine if we need a lighter or darker color
  const needsDarker = baseLuminance > 0.5;
  
  // Generate a contrasting color
  let contrastingRgb: [number, number, number];
  
  if (needsDarker) {
    // Start with black and adjust until we meet the target contrast
    contrastingRgb = [0, 0, 0];
    let currentContrast = (baseLuminance + 0.05) / (getLuminance(contrastingRgb) + 0.05);
    
    while (currentContrast > targetContrast && contrastingRgb[0] < 255) {
      contrastingRgb = contrastingRgb.map(c => Math.min(255, c + 5)) as [number, number, number];
      currentContrast = (baseLuminance + 0.05) / (getLuminance(contrastingRgb) + 0.05);
    }
  } else {
    // Start with white and adjust until we meet the target contrast
    contrastingRgb = [255, 255, 255];
    let currentContrast = (getLuminance(contrastingRgb) + 0.05) / (baseLuminance + 0.05);
    
    while (currentContrast > targetContrast && contrastingRgb[0] > 0) {
      contrastingRgb = contrastingRgb.map(c => Math.max(0, c - 5)) as [number, number, number];
      currentContrast = (getLuminance(contrastingRgb) + 0.05) / (baseLuminance + 0.05);
    }
  }
  
  return {
    foreground: needsDarker ? rgbToHex(contrastingRgb) : baseColor,
    background: needsDarker ? baseColor : rgbToHex(contrastingRgb)
  };
}

/**
 * Utility for checking if a color is accessible for color blindness.
 * 
 * @param color1 First color in hex format
 * @param color2 Second color in hex format
 * @param type Type of color blindness
 * @returns Whether the colors are distinguishable
 */
export function isColorBlindFriendly(
  color1: string,
  color2: string,
  type: 'protanopia' | 'deuteranopia' | 'tritanopia' = 'deuteranopia'
): boolean {
  // Convert hex to RGB
  const hexToRgb = (hex: string): [number, number, number] => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return [r, g, b];
  };
  
  // Simulate color blindness
  const simulateColorBlindness = (
    rgb: [number, number, number],
    type: 'protanopia' | 'deuteranopia' | 'tritanopia'
  ): [number, number, number] => {
    const [r, g, b] = rgb;
    
    if (type === 'protanopia') {
      // Red-blind
      return [
        0.567 * r + 0.433 * g + 0.0 * b,
        0.558 * r + 0.442 * g + 0.0 * b,
        0.0 * r + 0.242 * g + 0.758 * b
      ];
    } else if (type === 'deuteranopia') {
      // Green-blind
      return [
        0.625 * r + 0.375 * g + 0.0 * b,
        0.7 * r + 0.3 * g + 0.0 * b,
        0.0 * r + 0.3 * g + 0.7 * b
      ];
    } else {
      // Blue-blind
      return [
        0.95 * r + 0.05 * g + 0.0 * b,
        0.0 * r + 0.433 * g + 0.567 * b,
        0.0 * r + 0.475 * g + 0.525 * b
      ];
    }
  };
  
  // Calculate color difference
  const getColorDifference = (
    rgb1: [number, number, number],
    rgb2: [number, number, number]
  ): number => {
    const [r1, g1, b1] = rgb1;
    const [r2, g2, b2] = rgb2;
    
    // Use CIEDE2000 color difference formula (simplified)
    const deltaR = r1 - r2;
    const deltaG = g1 - g2;
    const deltaB = b1 - b2;
    
    return Math.sqrt(deltaR * deltaR + deltaG * deltaG + deltaB * deltaB);
  };
  
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);
  
  const simulatedRgb1 = simulateColorBlindness(rgb1, type);
  const simulatedRgb2 = simulateColorBlindness(rgb2, type);
  
  const difference = getColorDifference(simulatedRgb1, simulatedRgb2);
  
  // A difference of 100 or more is generally considered distinguishable
  return difference >= 100;
}