<template>
  <el-dialog
    v-model="visible"
    title="全局搜索"
    width="600px"
    :modal="true"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    class="global-search-dialog"
    @opened="handleOpened"
    @closed="handleClosed"
  >
    <div class="search-container">
      <el-input
        ref="searchInputRef"
        v-model="searchQuery"
        placeholder="搜索学生、教师、课程..."
        size="large"
        clearable
        @input="handleSearch"
        @keydown.enter="handleSelect"
        @keydown.up="handleArrowUp"
        @keydown.down="handleArrowDown"
        @keydown.escape="handleClose"
      >
        <template #prefix>
          <el-icon class="search-icon">
            <Search />
          </el-icon>
        </template>
      </el-input>

      <div v-if="loading" class="search-loading">
        <el-icon class="is-loading">
          <Loading />
        </el-icon>
        <span>搜索中...</span>
      </div>

      <div v-else-if="searchResults.length > 0" class="search-results">
        <div
          v-for="(result, index) in searchResults"
          :key="result.id"
          class="search-item"
          :class="{ active: selectedIndex === index }"
          @click="handleResultClick(result)"
          @mouseenter="selectedIndex = index"
        >
          <el-avatar :size="40" :src="result.avatar">
            {{ result.name.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="result-info">
            <div class="result-title">{{ result.name }}</div>
            <div class="result-type">{{ getTypeLabel(result.type) }}</div>
            <div v-if="result.description" class="result-description">
              {{ result.description }}
            </div>
          </div>
          <el-tag :type="getTagType(result.type)" size="small">
            {{ getTypeLabel(result.type) }}
          </el-tag>
        </div>
      </div>

      <div v-else-if="searchQuery && !loading" class="search-empty">
        <el-empty description="未找到相关结果" :image-size="80" />
      </div>

      <div v-else class="search-tips">
        <div class="tips-title">搜索提示</div>
        <div class="tips-content">
          <div>• 输入学生姓名、学号进行搜索</div>
          <div>• 输入教师姓名、工号进行搜索</div>
          <div>• 输入课程名称、课程代码进行搜索</div>
          <div>• 使用 ↑↓ 键选择结果，Enter 键跳转</div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="search-footer">
        <span class="footer-text">按 ESC 关闭</span>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { studentApi, teacherApi } from '@/api/user'

interface Props {
  visible: boolean
}

interface SearchResult {
  id: number
  name: string
  type: 'student' | 'teacher' | 'course'
  description?: string
  avatar?: string
  url: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const router = useRouter()

// 响应式数据
const searchQuery = ref('')
const searchResults = ref<SearchResult[]>([])
const loading = ref(false)
const selectedIndex = ref(0)
const searchInputRef = ref()

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 方法
const handleOpened = () => {
  nextTick(() => {
    searchInputRef.value?.focus()
    searchQuery.value = ''
    searchResults.value = []
    selectedIndex.value = 0
  })
}

const handleClosed = () => {
  searchQuery.value = ''
  searchResults.value = []
  selectedIndex.value = 0
}

const handleSearch = async (query: string) => {
  if (!query.trim()) {
    searchResults.value = []
    return
  }

  loading.value = true
  selectedIndex.value = 0

  try {
    const results: SearchResult[] = []

    // 搜索学生
    try {
      const studentResponse = await studentApi.searchStudents(query)
      if (studentResponse.data?.data) {
        const students = studentResponse.data.data
        results.push(...students.map(student => ({
          id: student.id,
          name: student.real_name,
          type: 'student' as const,
          description: `学号: ${student.student_id} | 专业: ${student.major}`,
          avatar: student.avatar,
          url: `/students/detail/${student.id}`
        })))
      }
    } catch (error) {
      console.error('Search students error:', error)
    }

    // 搜索教师
    try {
      const teacherResponse = await teacherApi.searchTeachers(query)
      if (teacherResponse.data?.data) {
        const teachers = teacherResponse.data.data
        results.push(...teachers.map(teacher => ({
          id: teacher.id,
          name: teacher.real_name,
          type: 'teacher' as const,
          description: `工号: ${teacher.teacher_id} | 部门: ${teacher.department}`,
          avatar: teacher.avatar,
          url: `/teachers/detail/${teacher.id}`
        })))
      }
    } catch (error) {
      console.error('Search teachers error:', error)
    }

    // 限制结果数量
    searchResults.value = results.slice(0, 10)
  } catch (error) {
    console.error('Search error:', error)
    ElMessage.error('搜索失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleSelect = () => {
  if (searchResults.value.length > 0 && selectedIndex.value >= 0) {
    const result = searchResults.value[selectedIndex.value]
    handleResultClick(result)
  }
}

const handleResultClick = (result: SearchResult) => {
  router.push(result.url)
  visible.value = false
}

const handleArrowUp = () => {
  if (searchResults.value.length === 0) return
  selectedIndex.value = (selectedIndex.value - 1 + searchResults.value.length) % searchResults.value.length
}

const handleArrowDown = () => {
  if (searchResults.value.length === 0) return
  selectedIndex.value = (selectedIndex.value + 1) % searchResults.value.length
}

const handleClose = () => {
  visible.value = false
}

const getTypeLabel = (type: string) => {
  const labels = {
    student: '学生',
    teacher: '教师',
    course: '课程'
  }
  return labels[type as keyof typeof labels] || type
}

const getTagType = (type: string) => {
  const types = {
    student: 'primary',
    teacher: 'success',
    course: 'warning'
  }
  return types[type as keyof typeof types] || 'info'
}

// 监听搜索查询变化
const debouncedSearch = debounce(handleSearch, 300)
watch(searchQuery, debouncedSearch)

// 防抖函数
function debounce(func: Function, wait: number) {
  let timeout: NodeJS.Timeout
  return function executedFunction(...args: any[]) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}
</script>

<style lang="scss" scoped>
.global-search-dialog {
  :deep(.el-dialog) {
    border-radius: 12px;
    overflow: hidden;
  }

  :deep(.el-dialog__header) {
    padding: 16px 20px;
    border-bottom: 1px solid var(--el-border-color-light);
  }

  :deep(.el-dialog__body) {
    padding: 20px;
  }

  :deep(.el-dialog__footer) {
    padding: 12px 20px;
    border-top: 1px solid var(--el-border-color-light);
  }
}

.search-container {
  .search-icon {
    color: var(--el-text-color-placeholder);
  }

  .search-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
    color: var(--el-text-color-regular);
    gap: 8px;
  }

  .search-results {
    max-height: 400px;
    overflow-y: auto;
    margin-top: 16px;

    .search-item {
      display: flex;
      align-items: center;
      padding: 12px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      margin-bottom: 4px;

      &:hover,
      &.active {
        background-color: var(--el-fill-color-light);
      }

      .result-info {
        flex: 1;
        margin-left: 12px;
        min-width: 0;

        .result-title {
          font-size: 14px;
          font-weight: 600;
          color: var(--el-text-color-primary);
          margin-bottom: 4px;
        }

        .result-type {
          font-size: 12px;
          color: var(--el-text-color-secondary);
          margin-bottom: 2px;
        }

        .result-description {
          font-size: 12px;
          color: var(--el-text-color-placeholder);
          line-height: 1.4;
        }
      }
    }
  }

  .search-empty {
    padding: 40px 0;
    text-align: center;
  }

  .search-tips {
    margin-top: 16px;
    padding: 16px;
    background-color: var(--el-fill-color-light);
    border-radius: 8px;

    .tips-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      margin-bottom: 8px;
    }

    .tips-content {
      font-size: 13px;
      color: var(--el-text-color-regular);
      line-height: 1.6;

      div {
        margin-bottom: 2px;
      }
    }
  }
}

.search-footer {
  display: flex;
  justify-content: center;
  align-items: center;

  .footer-text {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }
}
</style>