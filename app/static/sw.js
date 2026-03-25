const CACHE_NAME = "bunny-shell-v20260323-ui-service-153";
const SHELL_URL = "/";
const PRECACHE_URLS = [
  "/",
  "/static/styles.css?v=20260323-ui-service-153",
  "/static/app.js?v=20260323-ui-service-153",
  "/static/site.webmanifest?v=20260323-ui-service-153",
  "/static/bunny-transparent.png?v=20260323-ui-service-153",
  "/static/bunny1.png?v=20260323-ui-service-153",
  "/static/bunny-share-card.png?v=20260323-ui-service-153",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
          return Promise.resolve();
        }),
      ),
    ).then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") {
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(SHELL_URL, copy)).catch(() => {});
          return response;
        })
        .catch(async () => {
          const cached = await caches.match(SHELL_URL);
          if (cached) {
            return cached;
          }
          return new Response("Bunny is offline.", {
            status: 503,
            headers: { "Content-Type": "text/plain; charset=utf-8" },
          });
        }),
    );
    return;
  }

  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) {
        return cached;
      }
      return fetch(request);
    }),
  );
});

self.addEventListener("push", (event) => {
  const payload = event.data ? event.data.json() : {};
  const title = payload.title || "Bunny notification";
  const options = {
    body: payload.body || "",
    icon: payload.icon || "/static/bunny-transparent.png?v=20260323-ui-service-153",
    badge: payload.badge || "/static/bunny-transparent.png?v=20260323-ui-service-153",
    tag: payload.tag || "bunny-notification",
    data: payload.data || { url: "/" },
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const targetUrl = event.notification.data?.url || "/";
  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((clients) => {
      for (const client of clients) {
        if ("focus" in client) {
          client.postMessage({ type: "notification_click", url: targetUrl });
          return client.focus();
        }
      }
      if (self.clients.openWindow) {
        return self.clients.openWindow(targetUrl);
      }
      return undefined;
    }),
  );
});
