// Service Worker Registration for Dev-Server-Workflow Web UI
// This registers the service worker for offline support

// Check if service workers are supported
const isServiceWorkerSupported = 'serviceWorker' in navigator;

// Register the service worker
export function register() {
  if (isServiceWorkerSupported && (process.env.NODE_ENV === 'production' || window.location.hostname === 'localhost')) {
    const publicUrl = new URL(process.env.PUBLIC_URL, window.location.href);
    
    // If the public URL is on a different origin than our page, we can't use service workers
    if (publicUrl.origin !== window.location.origin) {
      console.warn('Service worker cannot be registered because the public URL is on a different origin');
      return;
    }
    
    window.addEventListener('load', () => {
      const swUrl = `${process.env.PUBLIC_URL}/serviceWorker.js`;
      
      if (process.env.NODE_ENV === 'production') {
        // Use the standard service worker registration in production
        registerValidSW(swUrl);
      } else {
        // Check if the service worker can be found in development
        checkValidServiceWorker(swUrl);
      }
      
      // Add event listeners for service worker updates
      setupServiceWorkerUpdateListeners();
    });
  } else {
    console.log('Service workers are not supported in this browser');
  }
}

// Register a valid service worker
function registerValidSW(swUrl) {
  navigator.serviceWorker
    .register(swUrl)
    .then((registration) => {
      console.log('Service worker registered successfully:', registration);
      
      registration.onupdatefound = () => {
        const installingWorker = registration.installing;
        
        if (!installingWorker) {
          return;
        }
        
        installingWorker.onstatechange = () => {
          if (installingWorker.state === 'installed') {
            if (navigator.serviceWorker.controller) {
              // At this point, the updated precached content has been fetched,
              // but the previous service worker will still serve the older content
              console.log('New content is available and will be used when all tabs for this page are closed');
              
              // Dispatch an event to notify the app that a new version is available
              window.dispatchEvent(new CustomEvent('serviceWorkerUpdate', {
                detail: registration
              }));
            } else {
              // At this point, everything has been precached
              console.log('Content is cached for offline use');
              
              // Dispatch an event to notify the app that content is cached for offline use
              window.dispatchEvent(new CustomEvent('serviceWorkerCached'));
            }
          }
        };
      };
    })
    .catch((error) => {
      console.error('Error during service worker registration:', error);
    });
}

// Check if the service worker is valid
function checkValidServiceWorker(swUrl) {
  // Check if the service worker can be found
  fetch(swUrl, {
    headers: { 'Service-Worker': 'script' }
  })
    .then((response) => {
      // Ensure service worker exists, and that we really are getting a JS file
      const contentType = response.headers.get('content-type');
      
      if (response.status === 404 || (contentType != null && contentType.indexOf('javascript') === -1)) {
        // No service worker found. Probably a different app. Reload the page
        navigator.serviceWorker.ready.then((registration) => {
          registration.unregister().then(() => {
            window.location.reload();
          });
        });
      } else {
        // Service worker found. Proceed as normal
        registerValidSW(swUrl);
      }
    })
    .catch(() => {
      console.log('No internet connection found. App is running in offline mode');
    });
}

// Set up event listeners for service worker updates
function setupServiceWorkerUpdateListeners() {
  // Listen for the serviceWorkerUpdate event
  window.addEventListener('serviceWorkerUpdate', (event) => {
    const registration = event.detail;
    
    // Create a UI element to notify the user of the update
    const updateNotification = document.createElement('div');
    updateNotification.className = 'update-notification';
    updateNotification.innerHTML = `
      <div class="update-notification-content">
        <p>Eine neue Version ist verfügbar!</p>
        <button id="update-app-button">Aktualisieren</button>
      </div>
    `;
    
    // Add the notification to the DOM
    document.body.appendChild(updateNotification);
    
    // Add event listener to the update button
    document.getElementById('update-app-button').addEventListener('click', () => {
      if (registration.waiting) {
        // Send a message to the service worker to skip waiting
        registration.waiting.postMessage({ action: 'skipWaiting' });
      }
    });
  });
  
  // Listen for controlling service worker changes
  let refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (refreshing) return;
    refreshing = true;
    window.location.reload();
  });
}

// Unregister the service worker
export function unregister() {
  if (isServiceWorkerSupported) {
    navigator.serviceWorker.ready
      .then((registration) => {
        registration.unregister();
      })
      .catch((error) => {
        console.error('Error unregistering service worker:', error);
      });
  }
}