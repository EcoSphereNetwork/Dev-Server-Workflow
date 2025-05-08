// Service Worker for Dev-Server-Workflow Web UI
// This provides offline support and caching for the web UI

const CACHE_NAME = 'dev-server-workflow-v1';
const URLS_TO_CACHE = [
  '/',
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/media/logo.png',
  '/manifest.json',
  '/favicon.ico'
];

// Install event - cache assets
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  
  // Perform install steps
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Opened cache');
        return cache.addAll(URLS_TO_CACHE);
      })
      .then(() => {
        console.log('Service Worker: All resources cached');
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  
  const cacheWhitelist = [CACHE_NAME];
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            console.log('Service Worker: Deleting old cache', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker: Activated');
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  console.log('Service Worker: Fetching', event.request.url);
  
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Cache hit - return response
        if (response) {
          console.log('Service Worker: Found in cache', event.request.url);
          return response;
        }
        
        // Clone the request because it's a one-time use stream
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest)
          .then((response) => {
            // Check if we received a valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              console.log('Service Worker: Invalid response', event.request.url);
              return response;
            }
            
            // Clone the response because it's a one-time use stream
            const responseToCache = response.clone();
            
            caches.open(CACHE_NAME)
              .then((cache) => {
                console.log('Service Worker: Caching new resource', event.request.url);
                cache.put(event.request, responseToCache);
              });
            
            return response;
          })
          .catch((error) => {
            console.log('Service Worker: Fetch failed', error);
            
            // Check if the request is for an HTML page
            if (event.request.headers.get('accept').includes('text/html')) {
              return caches.match('/offline.html');
            }
          });
      })
  );
});

// Message event - handle messages from the client
self.addEventListener('message', (event) => {
  console.log('Service Worker: Message received', event.data);
  
  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
});

// Push event - handle push notifications
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push received', event);
  
  const title = 'Dev-Server-Workflow';
  const options = {
    body: event.data.text(),
    icon: '/static/media/logo.png',
    badge: '/static/media/badge.png'
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click event - handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification click received', event);
  
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow('/')
  );
});

// Sync event - handle background sync
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Sync event received', event);
  
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

// Function to sync data
const syncData = async () => {
  try {
    const dataToSync = await getDataToSync();
    
    if (dataToSync.length === 0) {
      return;
    }
    
    const responses = await Promise.all(
      dataToSync.map(async (item) => {
        const response = await fetch('/api/sync', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(item)
        });
        
        if (response.ok) {
          return item.id;
        }
        
        return null;
      })
    );
    
    const successfulIds = responses.filter(id => id !== null);
    
    if (successfulIds.length > 0) {
      await removeFromSyncQueue(successfulIds);
    }
  } catch (error) {
    console.error('Service Worker: Sync failed', error);
  }
};

// Function to get data to sync
const getDataToSync = async () => {
  const db = await openDatabase();
  const tx = db.transaction('sync-store', 'readonly');
  const store = tx.objectStore('sync-store');
  
  return new Promise((resolve, reject) => {
    const request = store.getAll();
    
    request.onsuccess = (event) => {
      resolve(event.target.result);
    };
    
    request.onerror = (event) => {
      reject(event.target.error);
    };
  });
};

// Function to remove items from sync queue
const removeFromSyncQueue = async (ids) => {
  const db = await openDatabase();
  const tx = db.transaction('sync-store', 'readwrite');
  const store = tx.objectStore('sync-store');
  
  return Promise.all(
    ids.map((id) => {
      return new Promise((resolve, reject) => {
        const request = store.delete(id);
        
        request.onsuccess = () => {
          resolve();
        };
        
        request.onerror = (event) => {
          reject(event.target.error);
        };
      });
    })
  );
};

// Function to open IndexedDB database
const openDatabase = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('dev-server-workflow-db', 1);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      if (!db.objectStoreNames.contains('sync-store')) {
        db.createObjectStore('sync-store', { keyPath: 'id' });
      }
    };
    
    request.onsuccess = (event) => {
      resolve(event.target.result);
    };
    
    request.onerror = (event) => {
      reject(event.target.error);
    };
  });
};