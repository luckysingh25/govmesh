import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backendTarget = process.env.VITE_DEV_PROXY_TARGET || 'http://127.0.0.1:8000'

const proxyErrorHandler = (proxy) => {
  proxy.on('error', (err, req, res) => {
    // Gracefully handle backend disconnects/restarts without spewing AggregateError in terminal
    if (res && !res.headersSent && typeof res.writeHead === 'function') {
      res.writeHead(503, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({ error: 'Backend gateway currently reconnecting', code: err.code }))
    }
  })
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: backendTarget,
        changeOrigin: true,
        configure: proxyErrorHandler,
      },
      '/health': {
        target: backendTarget,
        changeOrigin: true,
        configure: proxyErrorHandler,
      }
    }
  }
})
