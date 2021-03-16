// TODO переписать и подключить

const CACHE_NAME = 'my-web-app-cache';
const urlsToCache = [
    '/',
];
const urlOfApi = [
    '/api_schedule/',
    '/api_get_done/',
    '/api_get_backpack/'
];

// При установке воркера мы должны закешировать часть данных (статику).
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches
            .open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache.concat(urlOfApi)))
            // `skipWaiting()` необходим, потому что мы хотим активировать SW
            // и контролировать его сразу, а не после перезагрузки.
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (event) => {
    // `self.clients.claim()` позволяет SW начать перехватывать запросы с самого начала,
    // это работает вместе с `skipWaiting()`, позволяя использовать `fallback` с самых первых запросов.
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', function(event) {
    // Можете использовать любую стратегию описанную выше.
    // Если она не отработает корректно, то используейте `Embedded fallback`.
    event.respondWith(trafficSolve(event.request).catch(fetch(event.request)));
});

/**
 * @param {Request} request
 */
function trafficSolve(request) {
    if (request.method === "POST"){
        return fetch(request);
    }
    if (request.url.includes('logout')){
        caches.open(CACHE_NAME).then((cache) =>{
            cache.delete('/');
        })
        return fetch(request);
    }
    if (urlOfApi.includes(request.url)){
        return apiSolve(request);
    }else{
        return staticSolve(request);
    }
}
function apiSolve(request){
    return fetch(request)
        .then((response) => response.ok ? response : fromCache(request))
        .catch(() => fromCache(request))
}

function staticSolve(request) {
    return caches.open(CACHE_NAME).then((cache) =>
        cache.match(request).then((matching) =>
            matching || Promise.reject('no-match')
        )
            .catch(()=>{
                fetch(request)
                    .then((response)=> { cache.put(request, response); return response})
            })
    );
}