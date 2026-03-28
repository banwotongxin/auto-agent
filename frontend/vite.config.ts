import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  //解决跨域问题
  server:{
    proxy:{
      '/api':{
        target:'http://localhost:8000',
        changeOrigin:true,
        rewrite:(path)=>path.replace(/^\/api/,'')
      },
      '/research':{
        target:'http://localhost:8000/api/v1',
        changeOrigin:true,
        rewrite:(path)=>path.replace(/^\/research/,'/research')
      }
    },
    port:5173,
    open:true//启动时自动打开服务器
  }
})
