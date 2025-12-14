<template>
  <div class="data-management">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">数据管理</span>
      </template>
    </el-page-header>

    <div class="data-container">
      <!-- 标签页 -->
      <el-tabs v-model="activeTab" class="data-tabs">
        <!-- 数据导入 -->
        <el-tab-pane label="数据导入" name="import">
          <el-card class="import-card">
            <el-steps :active="importStep" finish-status="success">
              <el-step title="选择数据类型" />
              <el-step title="上传文件" />
              <el-step title="预览数据" />
              <el-step title="完成导入" />
            </el-steps>

            <!-- 步骤1: 选择数据类型 -->
            <div v-if="importStep === 0" class="step-content">
              <h3>选择要导入的数据类型</h3>
              <el-row :gutter="20">
                <el-col :span="8" v-for="option in importOptions" :key="option.type">
                  <el-card
                    class="type-card"
                    :class="{ active: selectedType === option.type }"
                    @click="selectedType = option.type"
                  >
                    <el-icon class="type-icon">
                      <component :is="option.icon" />
                    </el-icon>
                    <h4>{{ option.label }}</h4>
                    <p>{{ option.description }}</p>
                  </el-card>
                </el-col>
              </el-row>
              <div class="step-actions">
                <el-button
                  type="primary"
                  @click="nextStep"
                  :disabled="!selectedType"
                >
                  下一步
                </el-button>
              </div>
            </div>

            <!-- 步骤2: 上传文件 -->
            <div v-if="importStep === 1" class="step-content">
              <h3>上传数据文件</h3>
              <el-upload
                class="upload-area"
                drag
                :auto-upload="false"
                :on-change="handleFileChange"
                :file-list="fileList"
                :limit="1"
                accept=".xlsx,.xls,.csv,.json"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  将文件拖拽到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 Excel、CSV、JSON 格式，文件大小不超过10MB
                  </div>
                </template>
              </el-upload>

              <div class="template-hint">
                <el-alert
                  title="需要导入模板吗？"
                  type="info"
                  :closable="false"
                >
                  <template #default>
                    <el-button
                      text
                      type="primary"
                      @click="downloadTemplate"
                    >
                      下载模板
                    </el-button>
                  </template>
                </el-alert>
              </div>

              <div class="step-actions">
                <el-button @click="prevStep">上一步</el-button>
                <el-button
                  type="primary"
                  @click="previewImport"
                  :disabled="!importData.length"
                >
                  下一步
                </el-button>
              </div>
            </div>

            <!-- 步骤3: 预览数据 -->
            <div v-if="importStep === 2" class="step-content">
              <h3>数据预览</h3>

              <el-alert
                :title="`共检测到 ${previewData?.total_rows || 0} 条数据，其中有效数据 ${previewData?.valid_rows || 0} 条`"
                :type="previewData?.error_count ? 'warning' : 'success'"
                :closable="false"
                class="preview-alert"
              />

              <div v-if="previewData?.errors.length" class="error-list">
                <h4>数据错误（前10个）：</h4>
                <el-scrollbar height="200px">
                  <el-alert
                    v-for="(error, index) in previewData.errors"
                    :key="index"
                    :title="error"
                    type="error"
                    :closable="false"
                    class="error-item"
                  />
                </el-scrollbar>
              </div>

              <div v-if="previewData?.preview_data?.length" class="preview-table">
                <h4>数据预览（前5行）：</h4>
                <el-table
                  :data="previewData.preview_data"
                  border
                  style="width: 100%"
                  max-height="400"
                >
                  <el-table-column
                    v-for="field in Object.keys(previewData.preview_data[0] || {})"
                    :key="field"
                    :prop="field"
                    :label="field"
                    show-overflow-tooltip
                  />
                </el-table>
              </div>

              <div class="step-actions">
                <el-button @click="prevStep">上一步</el-button>
                <el-button
                  type="primary"
                  @click="executeImport"
                  :loading="importLoading"
                  :disabled="!previewData?.valid_rows"
                >
                  确认导入
                </el-button>
              </div>
            </div>

            <!-- 步骤4: 完成导入 -->
            <div v-if="importStep === 3" class="step-content">
              <div class="result-content">
                <el-result
                  :icon="importResult?.error_count ? 'warning' : 'success'"
                  :title="importResult?.error_count ? '导入完成（部分失败）' : '导入成功'"
                >
                  <template #sub-title>
                    <p>总计 {{ importResult?.total_rows }} 条数据</p>
                    <p>成功 {{ importResult?.success_count }} 条</p>
                    <p v-if="importResult?.error_count">失败 {{ importResult?.error_count }} 条</p>
                  </template>

                  <template #extra>
                    <div v-if="importResult?.errors?.length" class="error-summary">
                      <h4>导入错误详情：</h4>
                      <el-scrollbar height="200px">
                        <el-alert
                          v-for="(error, index) in importResult.errors"
                          :key="index"
                          :title="error"
                          type="error"
                          :closable="false"
                          class="error-item"
                        />
                      </el-scrollbar>
                    </div>

                    <div class="result-actions">
                      <el-button @click="resetImport">重新导入</el-button>
                      <el-button type="primary" @click="activeTab = 'export'">
                        导出数据
                      </el-button>
                    </div>
                  </template>
                </el-result>
              </div>
            </div>
          </el-card>
        </el-tab-pane>

        <!-- 数据导出 -->
        <el-tab-pane label="数据导出" name="export">
          <el-card class="export-card">
            <el-form
              ref="exportFormRef"
              :model="exportForm"
              label-width="100px"
            >
              <el-form-item label="数据类型" required>
                <el-select v-model="exportForm.type" style="width: 100%">
                  <el-option
                    v-for="option in exportOptions"
                    :key="option.type"
                    :label="option.label"
                    :value="option.type"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="导出格式" required>
                <el-select v-model="exportForm.format" style="width: 100%">
                  <el-option label="Excel (xlsx)" value="xlsx" />
                  <el-option label="CSV" value="csv" />
                  <el-option label="JSON" value="json" />
                </el-select>
              </el-form-item>

              <el-form-item label="导出字段">
                <el-checkbox-group v-model="exportForm.fields">
                  <el-checkbox
                    v-for="field in getExportFields()"
                    :key="field"
                    :label="field"
                  >
                    {{ field }}
                  </el-checkbox>
                </el-checkbox-group>
                <div class="field-actions">
                  <el-button text type="primary" @click="selectAllFields">全选</el-button>
                  <el-button text type="primary" @click="clearFields">清空</el-button>
                </div>
              </el-form-item>

              <el-form-item label="筛选条件">
                <el-button
                  text
                  type="primary"
                  @click="showFilterDialog = true"
                >
                  设置筛选条件
                </el-button>
                <div v-if="hasFilters" class="filter-tags">
                  <el-tag
                    v-for="(value, key) in exportForm.filters"
                    :key="key"
                    closable
                    @close="removeFilter(key)"
                  >
                    {{ key }}: {{ formatFilterValue(value) }}
                  </el-tag>
                </div>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="handleExport"
                  :loading="exportLoading"
                >
                  导出数据
                </el-button>
                <el-button @click="resetExport">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 筛选条件对话框 -->
    <el-dialog
      v-model="showFilterDialog"
      title="设置筛选条件"
      width="500px"
    >
      <el-form :model="tempFilters" label-width="100px">
        <el-form-item
          v-for="field in getExportFields()"
          :key="field"
          :label="field"
        >
          <el-input
            v-model="tempFilters[field]"
            :placeholder="`输入${field}的筛选值`"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showFilterDialog = false">取消</el-button>
          <el-button type="primary" @click="applyFilters">应用</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UploadFilled,
  User,
  UserFilled,
  Notebook,
  Document,
  Management,
  DataLine
} from '@element-plus/icons-vue'
import { dataImportExportApi } from '@/api/data-import-export'
import type { ImportPreviewData, ImportResult, ImportTemplate } from '@/api/data-import-export'

const router = useRouter()

// 响应式数据
const activeTab = ref('import')
const importStep = ref(0)
const selectedType = ref('')
const fileList = ref([])
const importData = ref<any[]>([])
const previewData = ref<ImportPreviewData | null>(null)
const importResult = ref<ImportResult | null>(null)
const importLoading = ref(false)
const exportLoading = ref(false)
const showFilterDialog = ref(false)
const tempFilters = ref<Record<string, any>>({})
const templates = ref<Record<string, ImportTemplate>>({})

// 导入选项
const importOptions = [
  {
    type: 'users',
    label: '用户数据',
    description: '导入系统用户信息',
    icon: User
  },
  {
    type: 'students',
    label: '学生数据',
    description: '导入学生基本信息',
    icon: UserFilled
  },
  {
    type: 'teachers',
    label: '教师数据',
    description: '导入教师基本信息',
    icon: Management
  },
  {
    type: 'courses',
    label: '课程数据',
    description: '导入课程信息',
    icon: Notebook
  },
  {
    type: 'enrollments',
    label: '选课数据',
    description: '导入学生选课记录',
    icon: Document
  },
  {
    type: 'grades',
    label: '成绩数据',
    description: '导入学生成绩信息',
    icon: DataLine
  }
]

// 导出选项
const exportOptions = [...importOptions]

// 导出表单
const exportForm = reactive({
  type: 'users',
  format: 'xlsx',
  fields: [] as string[],
  filters: {}
})

// 计算属性
const hasFilters = computed(() => Object.keys(exportForm.filters).length > 0)

// 方法
const nextStep = () => {
  if (importStep.value < 3) {
    importStep.value++
  }
}

const prevStep = () => {
  if (importStep.value > 0) {
    importStep.value--
  }
}

const handleFileChange = async (file: any) => {
  try {
    const text = await file.raw.text()
    const data = JSON.parse(text)

    // 如果是JSON文件
    if (file.raw.type === 'application/json') {
      importData.value = Array.isArray(data) ? data : [data]
    } else {
      // Excel/CSV文件需要后端处理，这里先占位
      importData.value = [{ placeholder: 'File data will be processed by backend' }]
    }

    fileList.value = [file]
  } catch (error) {
    console.error('文件读取失败:', error)
    ElMessage.error('文件格式不正确')
  }
}

const downloadTemplate = () => {
  if (!selectedType.value) return

  const template = templates.value[selectedType.value]
  if (!template) return

  // 创建模板数据
  const templateData = [template.example]

  // 下载模板文件
  const blob = new Blob([JSON.stringify(templateData, null, 2)], {
    type: 'application/json'
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${selectedType.value}_template.json`
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('模板下载成功')
}

const previewImport = async () => {
  try {
    const response = await dataImportExportApi.previewImport({
      type: selectedType.value,
      data: importData.value
    })

    if (response.success) {
      previewData.value = response.data
      nextStep()
    }
  } catch (error: any) {
    console.error('预览导入失败:', error)
    ElMessage.error(error.response?.data?.message || '预览失败')
  }
}

const executeImport = async () => {
  try {
    importLoading.value = true

    const response = await dataImportExportApi.executeImport({
      type: selectedType.value,
      data: importData.value
    })

    if (response.success) {
      importResult.value = response.data
      nextStep()
    }
  } catch (error: any) {
    console.error('执行导入失败:', error)
    ElMessage.error(error.response?.data?.message || '导入失败')
  } finally {
    importLoading.value = false
  }
}

const resetImport = () => {
  importStep.value = 0
  selectedType.value = ''
  fileList.value = []
  importData.value = []
  previewData.value = null
  importResult.value = null
}

const getExportFields = () => {
  const type = exportForm.type
  const template = templates.value[type]
  return template ? template.schema.fields : []
}

const selectAllFields = () => {
  exportForm.fields = getExportFields()
}

const clearFields = () => {
  exportForm.fields = []
}

const applyFilters = () => {
  // 过滤掉空值
  const filters = Object.fromEntries(
    Object.entries(tempFilters.value).filter(([_, value]) => value !== '')
  )
  exportForm.filters = filters
  showFilterDialog.value = false
  tempFilters.value = {}
}

const removeFilter = (key: string) => {
  delete exportForm.filters[key]
}

const formatFilterValue = (value: any) => {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return String(value)
}

const handleExport = async () => {
  try {
    exportLoading.value = true

    const response = await dataImportExportApi.exportData({
      type: exportForm.type,
      format: exportForm.format,
      fields: exportForm.fields.length ? exportForm.fields : undefined,
      filters: Object.keys(exportForm.filters).length ? exportForm.filters : undefined
    })

    // 创建下载链接
    const blob = new Blob([response.data])
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${exportForm.type}_${new Date().toISOString().split('T')[0]}.${exportForm.format}`
    link.click()
    URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exportLoading.value = false
  }
}

const resetExport = () => {
  exportForm.type = 'users'
  exportForm.format = 'xlsx'
  exportForm.fields = []
  exportForm.filters = {}
  tempFilters.value = {}
}

const handleBack = () => {
  router.back()
}

const loadTemplates = async () => {
  try {
    const response = await dataImportExportApi.getTemplates()
    if (response.success) {
      templates.value = response.data
    }
  } catch (error) {
    console.error('加载模板失败:', error)
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style lang="scss" scoped>
.data-management {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .data-container {
    margin-top: 20px;

    .data-tabs {
      .import-card,
      .export-card {
        margin-top: 20px;

        .step-content {
          margin-top: 40px;
          min-height: 400px;

          h3 {
            margin-bottom: 20px;
            color: var(--el-text-color-primary);
          }

          .type-card {
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;

            &:hover {
              transform: translateY(-2px);
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }

            &.active {
              border-color: var(--el-color-primary);
              background-color: var(--el-color-primary-light-9);
            }

            .type-icon {
              font-size: 48px;
              color: var(--el-color-primary);
              margin-bottom: 16px;
            }

            h4 {
              margin: 8px 0;
            }

            p {
              color: var(--el-text-color-secondary);
              font-size: 14px;
            }
          }

          .step-actions {
            margin-top: 40px;
            display: flex;
            justify-content: center;
            gap: 16px;
          }

          .upload-area {
            margin-bottom: 20px;
          }

          .template-hint {
            margin: 20px 0;
          }

          .preview-alert {
            margin-bottom: 20px;
          }

          .error-list {
            margin: 20px 0;

            h4 {
              margin-bottom: 10px;
            }

            .error-item {
              margin-bottom: 8px;
            }
          }

          .preview-table {
            margin: 20px 0;

            h4 {
              margin-bottom: 10px;
            }
          }

          .result-content {
            .error-summary {
              max-width: 600px;
              margin: 20px auto;

              h4 {
                margin-bottom: 10px;
              }

              .error-item {
                margin-bottom: 8px;
              }
            }

            .result-actions {
              margin-top: 20px;
              display: flex;
              justify-content: center;
              gap: 16px;
            }
          }
        }
      }
    }
  }

  .field-actions {
    margin-top: 8px;
    display: flex;
    gap: 12px;
  }

  .filter-tags {
    margin-top: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}
</style>