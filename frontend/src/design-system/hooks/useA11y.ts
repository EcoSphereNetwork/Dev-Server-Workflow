/**
 * Barrierefreiheits-Hooks
 * 
 * Eine Sammlung von Hooks für die Verbesserung der Barrierefreiheit.
 */

import { useRef, useEffect, useCallback, KeyboardEvent } from 'react';

/**
 * Hook für die Verwaltung von Fokus-Traps
 * Verhindert, dass der Fokus aus einem bestimmten Bereich entweicht
 */
export const useFocusTrap = (isActive: boolean = true) => {
  const containerRef = useRef<HTMLElement | null>(null);
  const startSentinelRef = useRef<HTMLDivElement | null>(null);
  const endSentinelRef = useRef<HTMLDivElement | null>(null);
  
  // Finde alle fokussierbaren Elemente innerhalb des Containers
  const getFocusableElements = useCallback(() => {
    if (!containerRef.current) return [];
    
    const focusableElements = containerRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    return Array.from(focusableElements) as HTMLElement[];
  }, []);
  
  // Fokussiere das erste Element
  const focusFirstElement = useCallback(() => {
    const focusableElements = getFocusableElements();
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }
  }, [getFocusableElements]);
  
  // Fokussiere das letzte Element
  const focusLastElement = useCallback(() => {
    const focusableElements = getFocusableElements();
    if (focusableElements.length > 0) {
      focusableElements[focusableElements.length - 1].focus();
    }
  }, [getFocusableElements]);
  
  // Event-Handler für den Start-Sentinel
  const handleStartSentinelFocus = useCallback(() => {
    focusLastElement();
  }, [focusLastElement]);
  
  // Event-Handler für den End-Sentinel
  const handleEndSentinelFocus = useCallback(() => {
    focusFirstElement();
  }, [focusFirstElement]);
  
  // Aktiviere die Fokus-Trap
  useEffect(() => {
    if (!isActive || !containerRef.current) return;
    
    // Erstelle die Sentinel-Elemente
    const startSentinel = document.createElement('div');
    startSentinel.tabIndex = 0;
    startSentinel.style.position = 'absolute';
    startSentinel.style.width = '1px';
    startSentinel.style.height = '1px';
    startSentinel.style.overflow = 'hidden';
    startSentinel.style.clip = 'rect(0 0 0 0)';
    startSentinel.setAttribute('aria-hidden', 'true');
    startSentinel.addEventListener('focus', handleStartSentinelFocus);
    
    const endSentinel = document.createElement('div');
    endSentinel.tabIndex = 0;
    endSentinel.style.position = 'absolute';
    endSentinel.style.width = '1px';
    endSentinel.style.height = '1px';
    endSentinel.style.overflow = 'hidden';
    endSentinel.style.clip = 'rect(0 0 0 0)';
    endSentinel.setAttribute('aria-hidden', 'true');
    endSentinel.addEventListener('focus', handleEndSentinelFocus);
    
    // Füge die Sentinel-Elemente hinzu
    containerRef.current.insertBefore(startSentinel, containerRef.current.firstChild);
    containerRef.current.appendChild(endSentinel);
    
    // Speichere die Referenzen
    startSentinelRef.current = startSentinel;
    endSentinelRef.current = endSentinel;
    
    // Fokussiere das erste Element
    focusFirstElement();
    
    // Cleanup
    return () => {
      startSentinel.removeEventListener('focus', handleStartSentinelFocus);
      endSentinel.removeEventListener('focus', handleEndSentinelFocus);
      
      if (startSentinelRef.current && startSentinelRef.current.parentNode) {
        startSentinelRef.current.parentNode.removeChild(startSentinelRef.current);
      }
      
      if (endSentinelRef.current && endSentinelRef.current.parentNode) {
        endSentinelRef.current.parentNode.removeChild(endSentinelRef.current);
      }
    };
  }, [isActive, focusFirstElement, handleStartSentinelFocus, handleEndSentinelFocus]);
  
  return { containerRef, focusFirstElement, focusLastElement };
};

/**
 * Hook für die Verwaltung von Keyboard-Navigation
 * Ermöglicht die Navigation durch Elemente mit Pfeiltasten
 */
export const useKeyboardNavigation = <T extends HTMLElement>(
  itemsCount: number,
  options: {
    vertical?: boolean;
    horizontal?: boolean;
    loop?: boolean;
    onSelect?: (index: number) => void;
    onNavigate?: (index: number) => void;
  } = {}
) => {
  const {
    vertical = true,
    horizontal = false,
    loop = true,
    onSelect,
    onNavigate,
  } = options;
  
  const containerRef = useRef<T | null>(null);
  const [activeIndex, setActiveIndex] = React.useState<number>(-1);
  
  // Setze den aktiven Index
  const setActive = useCallback((index: number) => {
    if (index >= 0 && index < itemsCount) {
      setActiveIndex(index);
      onNavigate?.(index);
    }
  }, [itemsCount, onNavigate]);
  
  // Event-Handler für Tastatureingaben
  const handleKeyDown = useCallback((event: KeyboardEvent<T>) => {
    let newIndex = activeIndex;
    
    switch (event.key) {
      case 'ArrowUp':
        if (vertical) {
          event.preventDefault();
          newIndex = activeIndex - 1;
          if (newIndex < 0) {
            newIndex = loop ? itemsCount - 1 : 0;
          }
          setActive(newIndex);
        }
        break;
      
      case 'ArrowDown':
        if (vertical) {
          event.preventDefault();
          newIndex = activeIndex + 1;
          if (newIndex >= itemsCount) {
            newIndex = loop ? 0 : itemsCount - 1;
          }
          setActive(newIndex);
        }
        break;
      
      case 'ArrowLeft':
        if (horizontal) {
          event.preventDefault();
          newIndex = activeIndex - 1;
          if (newIndex < 0) {
            newIndex = loop ? itemsCount - 1 : 0;
          }
          setActive(newIndex);
        }
        break;
      
      case 'ArrowRight':
        if (horizontal) {
          event.preventDefault();
          newIndex = activeIndex + 1;
          if (newIndex >= itemsCount) {
            newIndex = loop ? 0 : itemsCount - 1;
          }
          setActive(newIndex);
        }
        break;
      
      case 'Home':
        event.preventDefault();
        setActive(0);
        break;
      
      case 'End':
        event.preventDefault();
        setActive(itemsCount - 1);
        break;
      
      case 'Enter':
      case ' ':
        if (activeIndex >= 0 && onSelect) {
          event.preventDefault();
          onSelect(activeIndex);
        }
        break;
      
      default:
        break;
    }
  }, [activeIndex, itemsCount, loop, vertical, horizontal, setActive, onSelect]);
  
  return {
    containerRef,
    activeIndex,
    setActiveIndex: setActive,
    handleKeyDown,
  };
};

/**
 * Hook für die Verwaltung von ARIA-Ankündigungen
 * Ermöglicht das Ankündigen von Nachrichten für Screenreader
 */
export const useAnnouncer = () => {
  const [message, setMessage] = React.useState('');
  const announcerRef = useRef<HTMLDivElement | null>(null);
  
  // Erstelle den Announcer
  useEffect(() => {
    // Erstelle das Announcer-Element
    const announcer = document.createElement('div');
    announcer.setAttribute('aria-live', 'polite');
    announcer.setAttribute('aria-atomic', 'true');
    announcer.style.position = 'absolute';
    announcer.style.width = '1px';
    announcer.style.height = '1px';
    announcer.style.overflow = 'hidden';
    announcer.style.clip = 'rect(0 0 0 0)';
    
    // Füge das Announcer-Element hinzu
    document.body.appendChild(announcer);
    
    // Speichere die Referenz
    announcerRef.current = announcer;
    
    // Cleanup
    return () => {
      if (announcerRef.current && announcerRef.current.parentNode) {
        announcerRef.current.parentNode.removeChild(announcerRef.current);
      }
    };
  }, []);
  
  // Aktualisiere den Announcer
  useEffect(() => {
    if (announcerRef.current && message) {
      announcerRef.current.textContent = message;
      
      // Lösche die Nachricht nach einer kurzen Verzögerung
      const timer = setTimeout(() => {
        setMessage('');
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [message]);
  
  // Funktion zum Ankündigen einer Nachricht
  const announce = useCallback((text: string) => {
    setMessage(text);
  }, []);
  
  return { announce };
};

export default {
  useFocusTrap,
  useKeyboardNavigation,
  useAnnouncer,
};