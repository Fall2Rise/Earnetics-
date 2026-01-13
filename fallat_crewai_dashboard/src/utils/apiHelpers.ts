/**
 * API Helper Utilities for Optimization
 * Provides request cancellation, deduplication, and retry logic
 */

interface RequestCache {
  [key: string]: {
    promise: Promise<unknown>;
    timestamp: number;
    abortController: AbortController;
  };
}

const requestCache: RequestCache = {};
const CACHE_TTL = 5000; // 5 seconds cache for duplicate requests

/**
 * Creates a fetch wrapper with timeout and abort support
 */
export function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs = 10000
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const fetchOptions: RequestInit = {
    ...options,
    signal: controller.signal,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  return fetch(url, fetchOptions)
    .finally(() => clearTimeout(timeoutId));
}

/**
 * Request deduplication - prevents duplicate simultaneous requests
 */
export async function dedupeRequest<T>(
  key: string,
  requestFn: () => Promise<T>,
  ttl = CACHE_TTL
): Promise<T> {
  const now = Date.now();
  const cached = requestCache[key];

  // If cached request exists and is still valid, return it
  if (cached && (now - cached.timestamp) < ttl) {
    return cached.promise as Promise<T>;
  }

  // Create new request
  const controller = new AbortController();
  const promise = requestFn().catch((error) => {
    // Clean up cache on error
    delete requestCache[key];
    throw error;
  });

  // Cache the request
  requestCache[key] = {
    promise,
    timestamp: now,
    abortController: controller,
  };

  // Clean up cache after TTL
  setTimeout(() => {
    if (requestCache[key]?.timestamp === now) {
      delete requestCache[key];
    }
  }, ttl);

  return promise;
}

/**
 * Retry logic with exponential backoff
 */
export async function retryRequest<T>(
  requestFn: () => Promise<T>,
  maxRetries = 3,
  initialDelay = 1000
): Promise<T> {
  let lastError: Error | unknown;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      
      // Don't retry on abort errors
      if (error instanceof Error && error.name === 'AbortError') {
        throw error;
      }
      
      // Don't retry on 4xx errors (client errors)
      if (error instanceof Response && error.status >= 400 && error.status < 500) {
        throw error;
      }
      
      if (attempt < maxRetries) {
        const delay = initialDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError;
}

/**
 * Cancel all pending requests for a given key pattern
 */
export function cancelRequests(pattern?: string): void {
  if (pattern) {
    Object.keys(requestCache).forEach((key) => {
      if (key.includes(pattern)) {
        requestCache[key].abortController.abort();
        delete requestCache[key];
      }
    });
  } else {
    // Cancel all requests
    Object.values(requestCache).forEach(({ abortController }) => {
      abortController.abort();
    });
    Object.keys(requestCache).forEach((key) => delete requestCache[key]);
  }
}

// Note: useVisibilityPause removed - use visibility API directly in components for better control
