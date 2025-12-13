/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 环境变量类型声明
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_VERSION: string
  readonly VITE_DEFAULT_AVATAR: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 扩展原生类型
declare module '*.scss' {
  const content: string
  export default content
}