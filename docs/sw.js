const CACHE_NAME = 'scripture-stories-cache-v1';

// Install event: pre-cache application shell and external scripts
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll([
                './',
                './index.html',
                'https://unpkg.com/vue@3/dist/vue.global.js',
                'https://cdn.tailwindcss.com'
            ]).catch(err => {
                console.warn('Pre-caching on install failed (safe to ignore if offline/dev):', err);
            });
        })
    );
    self.skipWaiting();
});

// Activate event: clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch event: serve cached resources or fetch and cache them
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Only intercept GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    const isSameOrigin = url.origin === self.location.origin;
    const isAPI = url.pathname.startsWith('/api/');
    // Match common image formats or paths pointing to the scripture images CDN
    const isImage = url.hostname.includes('churchofjesuschrist.org') || 
                    url.pathname.match(/\.(webp|png|jpg|jpeg|gif|svg)$/i);
    const isCDN = url.hostname.includes('unpkg.com') || url.hostname.includes('cdn.tailwindcss.com');

    if (isSameOrigin || isAPI || isImage || isCDN) {
        event.respondWith(
            caches.open(CACHE_NAME).then(async (cache) => {
                const cachedResponse = await cache.match(event.request);
                if (cachedResponse) {
                    return cachedResponse;
                }

                try {
                    // For cross-origin images, fetch using mode: 'no-cors' if normal fetch fails
                    // or force it to ensure we don't trigger CORS blocks on the client-side.
                    let fetchRequest = event.request;
                    if (isImage && !isSameOrigin) {
                        fetchRequest = new Request(event.request.url, {
                            method: 'GET',
                            headers: event.request.headers,
                            mode: 'no-cors',
                            credentials: 'omit'
                        });
                    }

                    const response = await fetch(fetchRequest);

                    // Cache the response if it is valid (status 200) or an opaque response (status 0)
                    if (response && (response.status === 200 || response.status === 0)) {
                        // Avoid caching dynamic or error responses
                        await cache.put(event.request, response.clone());
                    }
                    return response;
                } catch (error) {
                    console.error('Fetch and cache failed for:', event.request.url, error);
                    throw error;
                }
            })
        );
    }
});
