// Çevrimdışı oynanış: açılan her dosya önbelleğe alınır; oyun güncellenince eski önbellek silinir.
const V = 'hanedan-1793015458';
self.addEventListener('install', (e) => { self.skipWaiting(); e.waitUntil(caches.open(V).then((c) => c.addAll(['./', './index.html', './manifest.webmanifest']))); });
self.addEventListener('activate', (e) => { e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== V).map((k) => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', (e) => {
  const r = e.request;
  if (r.method !== 'GET' || r.headers.has('range')) return; // videolar parça parça gelir: önbelleğe alınmaz
  const url = new URL(r.url);
  const page = r.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('index.html');
  if (page) { // sayfa: önce ağ (güncelleme gelsin), yoksa önbellek
    e.respondWith(fetch(r).then((res) => { const cp = res.clone(); caches.open(V).then((c) => c.put(r, cp)); return res; }).catch(() => caches.match(r).then((m) => m || caches.match('./'))));
    return;
  }
  e.respondWith(caches.match(r).then((m) => m || fetch(r).then((res) => { if (res.ok && url.origin === location.origin) { const cp = res.clone(); caches.open(V).then((c) => c.put(r, cp)); } return res; })));
});
