/**
 * Responsive design utilities for creating responsive layouts.
 */

import { useEffect, useState, useMemo } from 'react';

// Breakpoint definitions
export const breakpoints = {
  xs: 0,
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
  xxl: 1400
};

export type Breakpoint = keyof typeof breakpoints;

/**
 * Custom hook for detecting the current breakpoint.
 * 
 * @returns The current breakpoint
 */
export function useBreakpoint(): Breakpoint {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('xs');

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      
      if (width >= breakpoints.xxl) {
        setBreakpoint('xxl');
      } else if (width >= breakpoints.xl) {
        setBreakpoint('xl');
      } else if (width >= breakpoints.lg) {
        setBreakpoint('lg');
      } else if (width >= breakpoints.md) {
        setBreakpoint('md');
      } else if (width >= breakpoints.sm) {
        setBreakpoint('sm');
      } else {
        setBreakpoint('xs');
      }
    };

    // Set initial breakpoint
    handleResize();

    // Add event listener
    window.addEventListener('resize', handleResize);

    // Clean up
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return breakpoint;
}

/**
 * Custom hook for detecting if the current breakpoint matches a query.
 * 
 * @param query The breakpoint query
 * @returns Whether the current breakpoint matches the query
 */
export function useBreakpointMatch(query: string): boolean {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    
    const handleChange = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    // Set initial value
    setMatches(mediaQuery.matches);

    // Add event listener
    mediaQuery.addEventListener('change', handleChange);

    // Clean up
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, [query]);

  return matches;
}

/**
 * Custom hook for detecting if the current breakpoint is up to a certain size.
 * 
 * @param breakpoint The breakpoint to check
 * @returns Whether the current viewport is up to the specified breakpoint
 */
export function useBreakpointUp(breakpoint: Breakpoint): boolean {
  const query = `(min-width: ${breakpoints[breakpoint]}px)`;
  return useBreakpointMatch(query);
}

/**
 * Custom hook for detecting if the current breakpoint is down to a certain size.
 * 
 * @param breakpoint The breakpoint to check
 * @returns Whether the current viewport is down to the specified breakpoint
 */
export function useBreakpointDown(breakpoint: Breakpoint): boolean {
  const nextBreakpoint = getNextBreakpoint(breakpoint);
  const query = nextBreakpoint
    ? `(max-width: ${breakpoints[nextBreakpoint] - 0.02}px)`
    : 'all';
  return useBreakpointMatch(query);
}

/**
 * Custom hook for detecting if the current breakpoint is between two sizes.
 * 
 * @param min The minimum breakpoint
 * @param max The maximum breakpoint
 * @returns Whether the current viewport is between the specified breakpoints
 */
export function useBreakpointBetween(min: Breakpoint, max: Breakpoint): boolean {
  const nextBreakpoint = getNextBreakpoint(max);
  const minQuery = `(min-width: ${breakpoints[min]}px)`;
  const maxQuery = nextBreakpoint
    ? `(max-width: ${breakpoints[nextBreakpoint] - 0.02}px)`
    : 'all';
  
  const minMatches = useBreakpointMatch(minQuery);
  const maxMatches = useBreakpointMatch(maxQuery);
  
  return minMatches && maxMatches;
}

/**
 * Custom hook for detecting if the current breakpoint is exactly a certain size.
 * 
 * @param breakpoint The breakpoint to check
 * @returns Whether the current viewport is exactly the specified breakpoint
 */
export function useBreakpointOnly(breakpoint: Breakpoint): boolean {
  const nextBreakpoint = getNextBreakpoint(breakpoint);
  const minQuery = `(min-width: ${breakpoints[breakpoint]}px)`;
  const maxQuery = nextBreakpoint
    ? `(max-width: ${breakpoints[nextBreakpoint] - 0.02}px)`
    : 'all';
  
  const minMatches = useBreakpointMatch(minQuery);
  const maxMatches = useBreakpointMatch(maxQuery);
  
  return minMatches && maxMatches;
}

/**
 * Custom hook for getting responsive values based on the current breakpoint.
 * 
 * @param values Object with values for different breakpoints
 * @returns The value for the current breakpoint
 */
export function useResponsiveValue<T>(values: Partial<Record<Breakpoint, T>>): T | undefined {
  const breakpoint = useBreakpoint();
  
  return useMemo(() => {
    // Get all breakpoints in descending order
    const breakpointOrder: Breakpoint[] = ['xxl', 'xl', 'lg', 'md', 'sm', 'xs'];
    
    // Find the current breakpoint index
    const currentIndex = breakpointOrder.indexOf(breakpoint);
    
    // Try to find a value for the current breakpoint or any smaller breakpoint
    for (let i = currentIndex; i < breakpointOrder.length; i++) {
      const bp = breakpointOrder[i];
      if (values[bp] !== undefined) {
        return values[bp];
      }
    }
    
    // If no value is found, return undefined
    return undefined;
  }, [breakpoint, values]);
}

/**
 * Custom hook for detecting device type.
 * 
 * @returns The detected device type
 */
export function useDeviceType(): 'mobile' | 'tablet' | 'desktop' {
  const [deviceType, setDeviceType] = useState<'mobile' | 'tablet' | 'desktop'>('desktop');

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      
      if (width < breakpoints.md) {
        setDeviceType('mobile');
      } else if (width < breakpoints.lg) {
        setDeviceType('tablet');
      } else {
        setDeviceType('desktop');
      }
    };

    // Set initial device type
    handleResize();

    // Add event listener
    window.addEventListener('resize', handleResize);

    // Clean up
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return deviceType;
}

/**
 * Custom hook for detecting orientation.
 * 
 * @returns The current orientation
 */
export function useOrientation(): 'portrait' | 'landscape' {
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>(
    window.innerHeight > window.innerWidth ? 'portrait' : 'landscape'
  );

  useEffect(() => {
    const handleResize = () => {
      setOrientation(
        window.innerHeight > window.innerWidth ? 'portrait' : 'landscape'
      );
    };

    // Set initial orientation
    handleResize();

    // Add event listener
    window.addEventListener('resize', handleResize);

    // Clean up
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return orientation;
}

/**
 * Custom hook for detecting touch capability.
 * 
 * @returns Whether the device has touch capability
 */
export function useTouchCapability(): boolean {
  const [hasTouch, setHasTouch] = useState(false);

  useEffect(() => {
    // Check for touch capability
    const hasTouch =
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0 ||
      (navigator as any).msMaxTouchPoints > 0;
    
    setHasTouch(hasTouch);
  }, []);

  return hasTouch;
}

/**
 * Custom hook for detecting hover capability.
 * 
 * @returns Whether the device has hover capability
 */
export function useHoverCapability(): boolean {
  const [hasHover, setHasHover] = useState(true);

  useEffect(() => {
    // Check for hover capability using media query
    const mediaQuery = window.matchMedia('(hover: hover)');
    
    const handleChange = (event: MediaQueryListEvent) => {
      setHasHover(event.matches);
    };

    // Set initial value
    setHasHover(mediaQuery.matches);

    // Add event listener
    mediaQuery.addEventListener('change', handleChange);

    // Clean up
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  return hasHover;
}

/**
 * Custom hook for detecting reduced motion preference.
 * 
 * @returns Whether the user prefers reduced motion
 */
export function usePrefersReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    // Check for reduced motion preference using media query
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    // Set initial value
    setPrefersReducedMotion(mediaQuery.matches);

    // Add event listener
    mediaQuery.addEventListener('change', handleChange);

    // Clean up
    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  return prefersReducedMotion;
}

/**
 * Custom hook for detecting color scheme preference.
 * 
 * @returns The preferred color scheme
 */
export function usePrefersColorScheme(): 'light' | 'dark' | 'no-preference' {
  const [colorScheme, setColorScheme] = useState<'light' | 'dark' | 'no-preference'>('light');

  useEffect(() => {
    // Check for dark mode preference using media query
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const lightModeQuery = window.matchMedia('(prefers-color-scheme: light)');
    
    const handleChange = () => {
      if (darkModeQuery.matches) {
        setColorScheme('dark');
      } else if (lightModeQuery.matches) {
        setColorScheme('light');
      } else {
        setColorScheme('no-preference');
      }
    };

    // Set initial value
    handleChange();

    // Add event listeners
    darkModeQuery.addEventListener('change', handleChange);
    lightModeQuery.addEventListener('change', handleChange);

    // Clean up
    return () => {
      darkModeQuery.removeEventListener('change', handleChange);
      lightModeQuery.removeEventListener('change', handleChange);
    };
  }, []);

  return colorScheme;
}

/**
 * Custom hook for detecting screen size.
 * 
 * @returns The current screen size
 */
export function useScreenSize(): { width: number; height: number } {
  const [screenSize, setScreenSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });

  useEffect(() => {
    const handleResize = () => {
      setScreenSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    // Add event listener
    window.addEventListener('resize', handleResize);

    // Clean up
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return screenSize;
}

/**
 * Custom hook for detecting if an element is visible in the viewport.
 * 
 * @param options IntersectionObserver options
 * @returns [ref, isVisible] tuple
 */
export function useElementVisibility<T extends HTMLElement>(
  options: IntersectionObserverInit = {}
): [React.RefObject<T>, boolean] {
  const [isVisible, setIsVisible] = useState(false);
  const ref = React.useRef<T>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      setIsVisible(entry.isIntersecting);
    }, options);

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [options]);

  return [ref, isVisible];
}

// Helper function to get the next breakpoint
function getNextBreakpoint(breakpoint: Breakpoint): Breakpoint | null {
  const breakpointOrder: Breakpoint[] = ['xs', 'sm', 'md', 'lg', 'xl', 'xxl'];
  const index = breakpointOrder.indexOf(breakpoint);
  
  if (index === -1 || index === breakpointOrder.length - 1) {
    return null;
  }
  
  return breakpointOrder[index + 1];
}