/**
 * Performance utilities for optimizing UI rendering and interactions.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * Custom hook for debouncing a value.
 * 
 * @param value The value to debounce
 * @param delay The delay in milliseconds
 * @returns The debounced value
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Custom hook for throttling a function.
 * 
 * @param callback The function to throttle
 * @param delay The delay in milliseconds
 * @returns The throttled function
 */
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): (...args: Parameters<T>) => void {
  const lastCall = useRef<number>(0);
  const lastCallTimer = useRef<NodeJS.Timeout | null>(null);

  return useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();
      const timeSinceLastCall = now - lastCall.current;

      if (timeSinceLastCall >= delay) {
        lastCall.current = now;
        callback(...args);
      } else {
        if (lastCallTimer.current) {
          clearTimeout(lastCallTimer.current);
        }

        lastCallTimer.current = setTimeout(() => {
          lastCall.current = Date.now();
          callback(...args);
        }, delay - timeSinceLastCall);
      }
    },
    [callback, delay]
  );
}

/**
 * Custom hook for memoizing expensive calculations.
 * 
 * @param factory The factory function that produces the value
 * @param deps The dependencies array
 * @returns The memoized value
 */
export function useMemoized<T>(factory: () => T, deps: React.DependencyList): T {
  const ref = useRef<{ value: T; deps: React.DependencyList }>({
    value: undefined as unknown as T,
    deps: []
  });

  const depsChanged = !deps.every(
    (dep, index) => Object.is(dep, ref.current.deps[index])
  );

  if (depsChanged || ref.current.value === undefined) {
    ref.current.value = factory();
    ref.current.deps = deps;
  }

  return ref.current.value;
}

/**
 * Custom hook for detecting when an element is visible in the viewport.
 * 
 * @param options IntersectionObserver options
 * @returns [ref, isVisible] tuple
 */
export function useInView<T extends Element>(
  options: IntersectionObserverInit = {}
): [React.RefObject<T>, boolean] {
  const ref = useRef<T>(null);
  const [isVisible, setIsVisible] = useState(false);

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

/**
 * Custom hook for lazy loading components.
 * 
 * @param factory The factory function that loads the component
 * @returns [Component, isLoading, error] tuple
 */
export function useLazyComponent<T>(
  factory: () => Promise<{ default: React.ComponentType<T> }>
): [React.ComponentType<T> | null, boolean, Error | null] {
  const [Component, setComponent] = useState<React.ComponentType<T> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isMounted = true;

    factory()
      .then(module => {
        if (isMounted) {
          setComponent(() => module.default);
          setIsLoading(false);
        }
      })
      .catch(err => {
        if (isMounted) {
          setError(err);
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [factory]);

  return [Component, isLoading, error];
}

/**
 * Utility for measuring component render performance.
 * 
 * @param componentName The name of the component
 * @param callback Optional callback to execute with the timing information
 * @returns A function to wrap around a component render
 */
export function measureRenderPerformance(
  componentName: string,
  callback?: (timing: { componentName: string; renderTime: number }) => void
) {
  return <T extends (...args: any[]) => React.ReactNode>(
    renderFn: T
  ): ((...args: Parameters<T>) => React.ReactNode) => {
    return (...args: Parameters<T>) => {
      const startTime = performance.now();
      const result = renderFn(...args);
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      if (process.env.NODE_ENV === 'development') {
        console.log(`[Performance] ${componentName} rendered in ${renderTime.toFixed(2)}ms`);
      }

      if (callback) {
        callback({ componentName, renderTime });
      }

      return result;
    };
  };
}

/**
 * Utility for creating a virtualized list renderer.
 * 
 * @param options Configuration options
 * @returns Props for the virtualized list container
 */
export function createVirtualizedList<T>({
  items,
  itemHeight,
  containerHeight,
  overscan = 5,
  renderItem
}: {
  items: T[];
  itemHeight: number;
  containerHeight: number;
  overscan?: number;
  renderItem: (item: T, index: number) => React.ReactNode;
}) {
  const [scrollTop, setScrollTop] = useState(0);

  const totalHeight = items.length * itemHeight;
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.floor((scrollTop + containerHeight) / itemHeight) + overscan
  );

  const visibleItems = items.slice(startIndex, endIndex + 1).map((item, index) => {
    const actualIndex = startIndex + index;
    const top = actualIndex * itemHeight;
    return {
      item,
      index: actualIndex,
      style: {
        position: 'absolute' as const,
        top,
        height: itemHeight,
        left: 0,
        right: 0
      }
    };
  });

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  };

  return {
    containerProps: {
      style: {
        height: containerHeight,
        position: 'relative' as const,
        overflow: 'auto' as const
      },
      onScroll: handleScroll
    },
    innerProps: {
      style: {
        height: totalHeight,
        position: 'relative' as const
      }
    },
    items: visibleItems.map(({ item, index, style }) => ({
      key: index,
      style,
      content: renderItem(item, index)
    }))
  };
}

/**
 * Utility for measuring and reporting web vitals.
 */
export function reportWebVitals(onPerfEntry?: (metric: any) => void) {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
}

/**
 * Utility for implementing React.memo with custom comparison.
 * 
 * @param component The component to memoize
 * @param propsAreEqual Custom comparison function
 * @returns Memoized component
 */
export function memoWithCustomCompare<T extends React.ComponentType<any>>(
  component: T,
  propsAreEqual?: (prevProps: React.ComponentProps<T>, nextProps: React.ComponentProps<T>) => boolean
): T {
  return React.memo(component, propsAreEqual) as T;
}

/**
 * Utility for implementing a resource cache.
 */
export class ResourceCache<K, V> {
  private cache = new Map<K, { value: V; timestamp: number }>();
  private maxSize: number;
  private ttl: number;

  constructor(maxSize = 100, ttl = 5 * 60 * 1000) {
    this.maxSize = maxSize;
    this.ttl = ttl;
  }

  get(key: K): V | undefined {
    const entry = this.cache.get(key);
    if (!entry) return undefined;

    const now = Date.now();
    if (now - entry.timestamp > this.ttl) {
      this.cache.delete(key);
      return undefined;
    }

    return entry.value;
  }

  set(key: K, value: V): void {
    if (this.cache.size >= this.maxSize) {
      // Remove oldest entry
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, { value, timestamp: Date.now() });
  }

  clear(): void {
    this.cache.clear();
  }
}

/**
 * Utility for implementing a request deduplication system.
 */
export class RequestDeduplicator {
  private pendingRequests = new Map<string, Promise<any>>();

  async deduplicate<T>(key: string, requestFn: () => Promise<T>): Promise<T> {
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key) as Promise<T>;
    }

    const promise = requestFn().finally(() => {
      this.pendingRequests.delete(key);
    });

    this.pendingRequests.set(key, promise);
    return promise;
  }
}

/**
 * Utility for implementing a worker pool for offloading heavy computations.
 */
export class WorkerPool {
  private workers: Worker[] = [];
  private queue: { task: any; resolve: (value: any) => void; reject: (reason: any) => void }[] = [];
  private availableWorkers: Worker[] = [];

  constructor(workerScript: string, numWorkers = navigator.hardwareConcurrency || 4) {
    for (let i = 0; i < numWorkers; i++) {
      const worker = new Worker(workerScript);
      worker.onmessage = this.handleWorkerMessage.bind(this, worker);
      worker.onerror = this.handleWorkerError.bind(this, worker);
      this.workers.push(worker);
      this.availableWorkers.push(worker);
    }
  }

  private handleWorkerMessage(worker: Worker, event: MessageEvent) {
    const { result, error, taskId } = event.data;
    const taskIndex = this.queue.findIndex(item => item.task.id === taskId);
    
    if (taskIndex !== -1) {
      const [task] = this.queue.splice(taskIndex, 1);
      if (error) {
        task.reject(new Error(error));
      } else {
        task.resolve(result);
      }
    }
    
    this.availableWorkers.push(worker);
    this.processQueue();
  }

  private handleWorkerError(worker: Worker, error: ErrorEvent) {
    console.error('Worker error:', error);
    
    // Replace the failed worker
    const index = this.workers.indexOf(worker);
    if (index !== -1) {
      this.workers.splice(index, 1);
      const newWorker = new Worker(worker.constructor.toString());
      newWorker.onmessage = this.handleWorkerMessage.bind(this, newWorker);
      newWorker.onerror = this.handleWorkerError.bind(this, newWorker);
      this.workers.push(newWorker);
      this.availableWorkers.push(newWorker);
    }
    
    this.processQueue();
  }

  private processQueue() {
    if (this.queue.length === 0 || this.availableWorkers.length === 0) {
      return;
    }
    
    const worker = this.availableWorkers.pop()!;
    const task = this.queue.shift()!;
    
    try {
      worker.postMessage(task.task);
    } catch (error) {
      task.reject(error);
      this.availableWorkers.push(worker);
      this.processQueue();
    }
  }

  execute<T>(task: any): Promise<T> {
    return new Promise((resolve, reject) => {
      const taskWithId = { ...task, id: Math.random().toString(36).substr(2, 9) };
      this.queue.push({ task: taskWithId, resolve, reject });
      this.processQueue();
    });
  }

  terminate() {
    this.workers.forEach(worker => worker.terminate());
    this.workers = [];
    this.availableWorkers = [];
    this.queue = [];
  }
}