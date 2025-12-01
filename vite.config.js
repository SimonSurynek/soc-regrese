import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'


// ...existing code...
export default defineConfig({
  // nechte base zakomentované pro lokální běh
  // base: process.env.NODE_ENV === 'production' ? '/soc-regrese/' : '/',
   base: '/soc-regrese/',
  plugins: [vue()],
})
// ...existing code...
