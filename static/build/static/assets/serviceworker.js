var staticCacheName = 'noman';
self.addEventListener('install', function(event) {
    self.skipWaiting();
    event.waitUntil(caches.open(staticCacheName).then(function(cache) {
        console.log('Opened cache');
        return cache.addAll([
            'user/offline',
            '/static/assets/favicon.ico',
            '/static/assets/css/login.css',
        ]).then(function(){
            console.log('Assets added to cache');
        }).catch(err => console.log('Error while fetching assets', err));
    }));
});


self.addEventListener('fetch', function(event) {
    // console.log(434343);
var requestUrl = new URL(event.request.url);
    
    if(event.request.mode === 'navigate' || (event.request.method === 'GET' && event.request.headers.get('accept').includes('text/html'))) {        
        event.respondWith(
            fetch(event.request.url).catch(error => {
                return caches.match('/user/offline'); 
            })
        );        
    } else{        
        event.respondWith(caches.match(event.request).then(function (response) {
            return response || fetch(event.request);  
        }));        
    }
});

self.addEventListener('activate', function(event){
    event.waitUntil(caches.keys().then((keyList) => {
        return Promise.all(keyList.map((key) => {
            if (key !== staticCacheName) {
                console.log('[ServiceWorker] Removing old cache', key);
                return caches.delete(key);
            }
        }));
    }));
});