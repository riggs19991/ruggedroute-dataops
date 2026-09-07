import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// VITE_BASE lets the same build serve from a sub-path (GitHub Pages: /ruggedroute-dataops/).
// Leave it unset for root hosting and for the Capacitor native apps.
export default defineConfig({
  base: process.env.VITE_BASE || '/',
  plugins: [react()],
})
