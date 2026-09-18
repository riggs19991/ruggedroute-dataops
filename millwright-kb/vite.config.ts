import { readFileSync } from 'node:fs'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

// VITE_BASE lets the same build serve from a sub-path (GitHub Pages: /ruggedroute-dataops/).
// Leave it unset for root hosting and for the Capacitor native apps.
const SUPABASE_HOST = 'tzucpijgyjhpgwukjsau.supabase.co'
// Build id: the commit on CI, the time locally. Figure URLs carry it (?v=) so a new build never
// shows a diagram the service worker cached from an older one.
const BUILD_ID = (process.env.GITHUB_SHA || '').slice(0, 7) || String(Date.now()).slice(-7)
const PKG_VERSION = JSON.parse(readFileSync(new URL('./package.json', import.meta.url), 'utf8')).version as string

// version.json: the published version marker the running app compares itself against on every
// open (src/lib/updates.ts). Not precached, served with Cache-Control: no-cache (public/_headers).
const versionJson = (): Plugin => ({
  name: 'mw-version-json',
  generateBundle() {
    this.emitFile({ type: 'asset', fileName: 'version.json', source: JSON.stringify({ build: BUILD_ID, version: PKG_VERSION, builtAt: new Date().toISOString() }) })
  },
})

export default defineConfig({
  base: process.env.VITE_BASE || '/',
  define: { __BUILD_ID__: JSON.stringify(BUILD_ID) },
  plugins: [
    react(),
    versionJson(),
    VitePWA({
      // 'prompt': a new build waits until the reader taps Update (src/lib/updates.ts, UpdateBanner).
      registerType: 'prompt',
      includeAssets: ['icon-180.png', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png', 'logo.svg', 'brand/amp-logo.png'],
      manifest: {
        id: '/',
        name: 'Millwright Knowledge Base',
        short_name: 'Millwright KB',
        description: 'Searchable millwright procedures, charts, formulas and manuals for students and instructors.',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        background_color: '#0f1b2d',
        theme_color: '#0f1b2d',
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
        globPatterns: ['**/*.{js,css,html,png,svg,woff2,webmanifest}'],
        globIgnores: ['img/**', 'photos/**', '**/*.woff', 'version.json', '_headers'],
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/img\//, /^\/assets\//, /\.[a-z0-9]+$/i],
        cleanupOutdatedCaches: true,
        // A freshly installed worker takes the page at once (offline from the first visit); a NEW build
        // still waits for the reader's Update tap because skipWaiting is off in prompt mode.
        clientsClaim: true,
        runtimeCaching: [
          {
            // Diagrams and photos: cache on first view, keep for a month. URLs are versioned per
            // build (?v=BUILD_ID), so a redrawn figure with the same file name is fetched fresh.
            urlPattern: ({ url }) => url.pathname.startsWith('/img/') || url.pathname.startsWith('/photos/'),
            handler: 'CacheFirst',
            options: { cacheName: 'mw-diagrams', expiration: { maxEntries: 900, maxAgeSeconds: 30 * 24 * 3600 }, cacheableResponse: { statuses: [0, 200] } },
          },
          {
            // Articles, categories and bookmarks read through the REST API: network first so a
            // re-seed shows at once; fall back to the last copy so opened articles work offline.
            urlPattern: ({ url, request }) => url.host === SUPABASE_HOST && request.method === 'GET' && /^\/rest\/v1\/(mw_articles|mw_categories|mw_bookmarks)/.test(url.pathname),
            handler: 'NetworkFirst',
            options: { cacheName: 'mw-api', networkTimeoutSeconds: 4, expiration: { maxEntries: 600, maxAgeSeconds: 7 * 24 * 3600 }, cacheableResponse: { statuses: [0, 200] } },
          },
        ],
      },
    }),
  ],
})
