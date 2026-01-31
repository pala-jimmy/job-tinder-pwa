// Simple service worker for PWA support
self.addEventListener('install', (event) => {
  console.log('Service Worker installing.');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activating.');
  return self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Basic fetch handler - just pass through for now
  event.respondWith(fetch(event.request));
});
