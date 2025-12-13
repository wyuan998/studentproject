import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: [
        'vue',
        'vue-router',
        'pinia',
        {
          'axios': [
            'default as axios',
            'AxiosInstance as AxiosInstance',
            'AxiosError as AxiosError'
          ]
        },
        // 'dayjs',
        // {
        //   'mitt': 'default as mitt'
        // },
        // {
        //   'nprogress': 'default as nprogress'
        // },
        // {
        //   'js-cookie': 'default as Cookies'
        // },
        // {
        //   'lodash-es': [
        //     'default as _',
        //     'camelCase as _camelCase',
        //     'kebabCase as _kebabCase'
        //   ]
        // }
      ],
      dts: true,
      eslintrc: {
        enabled: true
      },
      vueTemplateCompilerOptions: {
        options: {
          compilerOptions: {
            isCustomElement: (tag) => tag.includes('-')
          }
        }
      }
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: true
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@views': resolve(__dirname, 'src/views'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@api': resolve(__dirname, 'src/api'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@types': resolve(__dirname, 'src/types'),
      '@assets': resolve(__dirname, 'src/assets'),
      '@styles': resolve(__dirname, 'src/styles'),
      '@router': resolve(__dirname, 'src/router'),
      '@directives': resolve(__dirname, 'src/directives'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@config': resolve(__dirname, 'src/config')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000/api/v1',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        }
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  }
})