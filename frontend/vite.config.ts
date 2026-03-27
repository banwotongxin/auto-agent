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
        changeOrigin:true,//将本地开发环境中的 /api 请求转发到后端服务器，并在转发前把路径中的 /api 去掉。
        rewrite:(path)=>path.replace(/^\/api/,'')//将匹配到的 /api 替换为空字符串 ''
      }
    },
    port:5173,
    open:true//启动时自动打开服务器
  }
})
