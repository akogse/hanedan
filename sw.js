// Çevrimdışı oynanış: sayfa her güncellemede yenilenir; görsel/ses/video bir kez iner ve güncellemelerde korunur.
const V = 'hanedan-1795164515';
self.addEventListener('install', (e) => { self.skipWaiting(); e.waitUntil(caches.open(V).then((c) => c.addAll(['./', './index.html', './manifest.webmanifest']))); });
const VARLIK = 'hanedan-varliklar-1'; // görsel, ses, video: güncellemelerde silinmez
self.addEventListener('activate', (e) => { e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== V && k !== VARLIK).map((k) => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', (e) => {
  const r = e.request;
  if (r.method !== 'GET' || r.headers.has('range')) return; // videolar parça parça gelir: önbelleğe alınmaz
  const url = new URL(r.url);
  if (url.origin !== location.origin) return;
  const page = r.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('index.html');
  if (page) { // sayfa: önce ağ (güncelleme gelsin), yoksa önbellek
    e.respondWith(fetch(r, { cache: 'no-cache' }).then((res) => { const cp = res.clone(); caches.open(V).then((c) => c.put(r, cp)); return res; }).catch(() => caches.match(r).then((m) => m || caches.match('./'))));
    return;
  }
  // varlıklar: adreste içerik parmak izi (?v=) var; aynı adres hep aynı dosyadır, önbellekte varsa ağa hiç gidilmez
  e.respondWith(caches.open(VARLIK).then((c) => c.match(r).then((m) => m || fetch(r).then((res) => { if (res.ok) c.put(r, res.clone()); return res; }))));
});
