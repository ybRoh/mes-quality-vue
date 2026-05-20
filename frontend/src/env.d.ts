/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'element-plus/es/locale/lang/ko' {
  const ko: any
  export default ko
}

import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    public?: boolean
    roles?: string[]
  }
}
