// 强制重置存储的工具函数
export const forceResetStorage = () => {
  console.log('=== 强制重置存储 ===')

  // 清除所有localStorage
  const keys = []
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i)
    if (key) {
      keys.push(key)
      console.log('删除localStorage key:', key, localStorage.getItem(key))
    }
  }

  keys.forEach(key => localStorage.removeItem(key))

  // 清除sessionStorage
  for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i)
    if (key) {
      sessionStorage.removeItem(key)
    }
  }

  console.log('存储已清除，即将刷新页面')

  // 强制刷新页面
  window.location.reload()
}

// 检查当前存储状态
export const checkStorageState = () => {
  console.log('=== 存储状态检查 ===')
  console.log('localStorage:')
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i)
    if (key) {
      console.log(`  ${key}: ${localStorage.getItem(key)}`)
    }
  }
  console.log('sessionStorage:')
  for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i)
    if (key) {
      console.log(`  ${key}: ${sessionStorage.getItem(key)}`)
    }
  }
}