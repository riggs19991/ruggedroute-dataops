import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

// VITE_BASE lets the same build serve from a sub-path (GitHub Pages: /ruggedroute-dataops/).
// Leave it unset for root hosting and for the Capacitor native apps.
const SUPABASE_HOST = 'tzucpijgyjhpgwukjsau.supabase.co'

export default defineConfig({
  base: process.env.VITE_BASE || '/',
  plugins: [
    react(),
    VitePWA({
      registerType: 'prompt',
      includeAssets: ['icon-180.png', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png'],
      manifest: {
        id: '/',
        name: 'Millwright Knowledge Base',
        short_name: 'Millwright KB',
        description: 'Searchable millwright procedures, charts, formulas and manuals for students and instructors.',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        background_color: '#0f172a',
        theme_color: '#0f172a',
        orientation: 'any',
        categories: ['education', 'productivity'],
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // App shell: everything Vite emits plus the icons. Diagrams are cached on first view (below).
        globPatterns: ['**/*.{js,css,html,png,webmanifest}'],
        globIgnores: ['img/**'],
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/img\//, /^\/assets\//, /\.[a-z0-9]+$/i],
        cleanupOutdatedCaches: true,
        runtimeCaching: [
          {
            // The 155 diagrams: cache on first view, keep for a month.
            urlPattern: ({ url }) => url.pathname.startsWith('/img/'),
            handler: 'CacheFirst',
            options: { cacheName: 'mw-diagrams', expiration: { maxEntries: 400, maxAgeSeconds: 30 * 24 * 3600 }, cacheableResponse: { statuses: [0, 200] } },
          },
          {
            // Articles, categories and bookmarks read through the REST API: serve the last copy
            // while refreshing, so opened articles and the A-Z index work offline.
            urlPattern: ({ url, request }) => url.host === SUPABASE_HOST && request.method === 'GET' && /^\/rest\/v1\/(mw_articles|mw_categories|mw_bookmarks)/.test(url.pathname),
            handler: 'StaleWhileRevalidate',
            options: { cacheName: 'mw-api', expiration: { maxEntries: 600, maxAgeSeconds: 7 * 24 * 3600 }, cacheableResponse: { statuses: [0, 200] } },
          },
        ],
      },
    }),
  ],
})
