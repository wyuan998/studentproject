import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 状态
  const sidebarCollapsed = ref(false)
  const theme = ref<'light' | 'dark'>('light')
  const language = ref<'zh-CN' | 'en-US'>('zh-CN')
  const loading = ref(false)
  const breadcrumbs = ref<Array<{ title: string; path?: string }>>([])
  const pageLoading = ref(false)
  const device = ref<'desktop' | 'mobile' | 'tablet'>('desktop')
  const screenBreakpoint = ref(0)

  // 计算属性
  const isDarkMode = computed(() => theme.value === 'dark')
  const isMobile = computed(() => device.value === 'mobile')
  const isTablet = computed(() => device.value === 'tablet')
  const isDesktop = computed(() => device.value === 'desktop')

  // 侧边栏控制
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  const collapseSidebar = () => {
    sidebarCollapsed.value = true
  }

  const expandSidebar = () => {
    sidebarCollapsed.value = false
  }

  // 主题控制
  const setTheme = (newTheme: 'light' | 'dark') => {
    theme.value = newTheme
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }

  const toggleTheme = () => {
    const newTheme = theme.value === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
  }

  const initTheme = () => {
    const storedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null
    if (storedTheme) {
      setTheme(storedTheme)
    } else {
      // 根据系统主题设置默认主题
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      setTheme(prefersDark ? 'dark' : 'light')
    }
  }

  // 语言控制
  const setLanguage = (lang: 'zh-CN' | 'en-US') => {
    language.value = lang
    localStorage.setItem('language', lang)
  }

  const initLanguage = () => {
    const storedLanguage = localStorage.getItem('language') as 'zh-CN' | 'en-US' | null
    if (storedLanguage) {
      language.value = storedLanguage
    } else {
      // 根据浏览器语言设置默认语言
      const browserLanguage = navigator.language.toLowerCase()
      if (browserLanguage.includes('zh')) {
        language.value = 'zh-CN'
      } else {
        language.value = 'en-US'
      }
    }
  }

  // 加载控制
  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const setPageLoading = (isLoading: boolean) => {
    pageLoading.value = isLoading
  }

  // 面包屑控制
  const setBreadcrumbs = (newBreadcrumbs: Array<{ title: string; path?: string }>) => {
    breadcrumbs.value = newBreadcrumbs
  }

  const addBreadcrumb = (breadcrumb: { title: string; path?: string }) => {
    breadcrumbs.value.push(breadcrumb)
  }

  const clearBreadcrumbs = () => {
    breadcrumbs.value = []
  }

  // 设备检测
  const detectDevice = () => {
    const width = window.innerWidth

    if (width < 768) {
      device.value = 'mobile'
      sidebarCollapsed.value = true
    } else if (width < 1024) {
      device.value = 'tablet'
    } else {
      device.value = 'desktop'
    }

    screenBreakpoint.value = width
  }

  // 加载用户信息
  const loadUserInfo = async () => {
    // 这里可以调用用户API加载信息
    // const userStore = useUserStore()
    // if (userStore.isAuthenticated && !userStore.userInfo) {
    //   await userStore.getUserInfo()
    // }
  }

  // 加载菜单
  const loadMenus = async () => {
    // 这里可以调用菜单API
  }

  // 获取页面标题
  const getPageTitle = (pageTitle?: string) => {
    if (pageTitle) {
      return `${pageTitle} - 学生信息管理系统`
    }
    return '学生信息管理系统'
  }

  // 设置页面标题
  const setPageTitle = (title?: string) => {
    document.title = getPageTitle(title)
  }

  // 初始化应用
  const initApp = async () => {
    setLoading(true)

    try {
      // 初始化主题
      initTheme()

      // 初始化语言
      initLanguage()

      // 检测设备
      detectDevice()

      // 监听窗口大小变化
      window.addEventListener('resize', detectDevice)

      // 监听系统主题变化
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
          setTheme(e.matches ? 'dark' : 'light')
        }
      })

      // 加载用户信息
      await loadUserInfo()

      // 加载菜单
      await loadMenus()

    } catch (error) {
      console.error('App initialization error:', error)
    } finally {
      setLoading(false)
    }
  }

  return {
    // 状态
    sidebarCollapsed,
    theme,
    language,
    loading,
    breadcrumbs,
    pageLoading,
    device,
    screenBreakpoint,

    // 计算属性
    isDarkMode,
    isMobile,
    isTablet,
    isDesktop,

    // 方法
    toggleSidebar,
    collapseSidebar,
    expandSidebar,
    setTheme,
    toggleTheme,
    initTheme,
    setLanguage,
    initLanguage,
    setLoading,
    setPageLoading,
    setBreadcrumbs,
    addBreadcrumb,
    clearBreadcrumbs,
    detectDevice,
    loadUserInfo,
    loadMenus,
    getPageTitle,
    setPageTitle,
    initApp
  }
})