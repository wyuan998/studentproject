<template>
  <div class="config-management">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">系统配置管理</span>
      </template>
    </el-page-header>

    <div class="config-container">
      <!-- 搜索和操作栏 -->
      <el-card class="search-card">
        <el-form :model="searchForm" inline>
          <el-form-item label="关键词">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索配置名称、键或描述"
              style="width: 200px"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="分类">
            <el-select
              v-model="searchForm.category"
              placeholder="选择配置分类"
              style="width: 150px"
              clearable
            >
              <el-option
                v-for="category in categories"
                :key="category.category"
                :label="category.category"
                :value="category.category"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="类型">
            <el-select
              v-model="searchForm.config_type"
              placeholder="选择配置类型"
              style="width: 150px"
              clearable
            >
              <el-option label="系统配置" value="system" />
              <el-option label="学术配置" value="academic" />
              <el-option label="通知配置" value="notification" />
              <el-option label="安全配置" value="security" />
              <el-option label="邮件配置" value="email" />
              <el-option label="备份配置" value="backup" />
              <el-option label="界面配置" value="ui" />
              <el-option label="集成配置" value="integration" />
              <el-option label="功能开关" value="feature" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>

        <div class="actions">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新增配置
          </el-button>
          <el-button @click="handleExport">
            <el-icon><Download /></el-icon>
            导出配置
          </el-button>
          <el-button @click="handleClearCache">
            <el-icon><Refresh /></el-icon>
            清除缓存
          </el-button>
        </div>
      </el-card>

      <!-- 配置列表 -->
      <el-card class="table-card">
        <el-table
          :data="configs"
          v-loading="loading"
          stripe
          style="width: 100%"
        >
          <el-table-column prop="key" label="配置键" width="180" />
          <el-table-column prop="name" label="配置名称" width="200" />
          <el-table-column prop="category" label="分类" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ row.category }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="display_type" label="值类型" width="100" />
          <el-table-column prop="display_value" label="当前值" width="200" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-switch
                v-model="row.is_active"
                @change="handleToggleStatus(row)"
                :disabled="!row.is_editable"
              />
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.updated_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click="handleEdit(row)"
                :disabled="!row.is_editable"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                @click="handleDelete(row)"
                :disabled="!row.is_editable"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.per_page"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSearch"
            @current-change="handleSearch"
          />
        </div>
      </el-card>
    </div>

    <!-- 创建/编辑配置对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingConfig ? '编辑配置' : '新增配置'"
      width="600px"
      @closed="resetForm"
    >
      <el-form
        ref="configFormRef"
        :model="configForm"
        :rules="configRules"
        label-width="100px"
      >
        <el-form-item label="配置键" prop="key">
          <el-input
            v-model="configForm.key"
            placeholder="配置键，如：system.name"
            :disabled="!!editingConfig"
          />
        </el-form-item>
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="configForm.name" placeholder="配置显示名称" />
        </el-form-item>
        <el-form-item label="配置分类" prop="category">
          <el-input v-model="configForm.category" placeholder="如：basic, security, email" />
        </el-form-item>
        <el-form-item label="配置类型" prop="config_type">
          <el-select v-model="configForm.config_type" style="width: 100%">
            <el-option label="系统配置" value="system" />
            <el-option label="学术配置" value="academic" />
            <el-option label="通知配置" value="notification" />
            <el-option label="安全配置" value="security" />
            <el-option label="邮件配置" value="email" />
            <el-option label="备份配置" value="backup" />
            <el-option label="界面配置" value="ui" />
            <el-option label="集成配置" value="integration" />
            <el-option label="功能开关" value="feature" />
          </el-select>
        </el-form-item>
        <el-form-item label="值类型" prop="value_type">
          <el-select v-model="configForm.value_type" style="width: 100%">
            <el-option label="字符串" value="string" />
            <el-option label="整数" value="integer" />
            <el-option label="浮点数" value="float" />
            <el-option label="布尔值" value="boolean" />
            <el-option label="JSON对象" value="json" />
            <el-option label="数组" value="array" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置值" prop="value">
          <el-input
            v-if="configForm.value_type === 'string'"
            v-model="configForm.value"
            type="textarea"
            :rows="3"
            placeholder="请输入字符串值"
          />
          <el-input-number
            v-else-if="configForm.value_type === 'integer'"
            v-model="configForm.value"
            style="width: 100%"
          />
          <el-input-number
            v-else-if="configForm.value_type === 'float'"
            v-model="configForm.value"
            :step="0.1"
            style="width: 100%"
          />
          <el-switch
            v-else-if="configForm.value_type === 'boolean'"
            v-model="configForm.value"
          />
          <el-input
            v-else-if="configForm.value_type === 'json' || configForm.value_type === 'array'"
            v-model="configForm.value_text"
            type="textarea"
            :rows="5"
            placeholder="请输入JSON格式的值"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="configForm.description"
            type="textarea"
            :rows="2"
            placeholder="配置项描述"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="是否启用">
              <el-switch v-model="configForm.is_active" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="是否必填">
              <el-switch v-model="configForm.is_required" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="是否公开">
              <el-switch v-model="configForm.is_public" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="是否可编辑">
              <el-switch v-model="configForm.is_editable" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="需要重启">
              <el-switch v-model="configForm.requires_restart" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="排序序号">
              <el-input-number v-model="configForm.sort_order" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" :loading="saveLoading" @click="handleSave">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Download, Refresh } from '@element-plus/icons-vue'
import { systemConfigApi } from '@/api/system-config'
import type { SystemConfigItem, SystemConfigCreateData, SystemConfigUpdateData } from '@/api/system-config'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const saveLoading = ref(false)
const showCreateDialog = ref(false)
const editingConfig = ref<SystemConfigItem | null>(null)
const configFormRef = ref<FormInstance>()

const configs = ref<SystemConfigItem[]>([])
const categories = ref<{ category: string; config_count: number }[]>([])

const searchForm = reactive({
  keyword: '',
  category: '',
  config_type: '',
  is_active: undefined as boolean | undefined
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const configForm = reactive({
  key: '',
  name: '',
  description: '',
  category: '',
  config_type: 'system',
  value_type: 'string',
  value: null as any,
  value_text: '',
  is_active: true,
  is_required: false,
  is_public: false,
  is_editable: true,
  requires_restart: false,
  sort_order: 0
})

const configRules: FormRules = {
  key: [
    { required: true, message: '请输入配置键', trigger: 'blur' },
    { pattern: /^[a-zA-Z][a-zA-Z0-9_.-]*$/, message: '配置键格式不正确', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请输入配置分类', trigger: 'blur' }
  ],
  config_type: [
    { required: true, message: '请选择配置类型', trigger: 'change' }
  ],
  value_type: [
    { required: true, message: '请选择值类型', trigger: 'change' }
  ],
  value: [
    { required: true, message: '请输入配置值', trigger: 'blur' }
  ]
}

// 方法
const loadConfigs = async () => {
  try {
    loading.value = true
    const response = await systemConfigApi.getConfigList({
      ...searchForm,
      page: pagination.page,
      per_page: pagination.per_page
    })

    if (response.success) {
      configs.value = response.data.configs
      pagination.total = response.data.pagination.total
    }
  } catch (error: any) {
    console.error('加载配置列表失败:', error)
    ElMessage.error(error.response?.data?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const response = await systemConfigApi.getConfigCategories()
    if (response.success) {
      categories.value = response.data
    }
  } catch (error) {
    console.error('加载分类列表失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadConfigs()
}

const handleReset = () => {
  Object.assign(searchForm, {
    keyword: '',
    category: '',
    config_type: '',
    is_active: undefined
  })
  handleSearch()
}

const handleEdit = (config: SystemConfigItem) => {
  editingConfig.value = config
  Object.assign(configForm, {
    key: config.key,
    name: config.name,
    description: config.description,
    category: config.category,
    config_type: config.config_type,
    value_type: config.value_type,
    value: config.value,
    value_text: typeof config.value === 'object' ? JSON.stringify(config.value, null, 2) : '',
    is_active: config.is_active,
    is_required: config.is_required,
    is_public: config.is_public,
    is_editable: config.is_editable,
    requires_restart: config.requires_restart,
    sort_order: config.sort_order
  })
  showCreateDialog.value = true
}

const handleDelete = async (config: SystemConfigItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除配置项 "${config.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await systemConfigApi.deleteConfig(config.key)
    if (response.success) {
      ElMessage.success('删除成功')
      loadConfigs()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除配置失败:', error)
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}

const handleToggleStatus = async (config: SystemConfigItem) => {
  try {
    const response = await systemConfigApi.updateConfig(config.key, {
      is_active: config.is_active
    })
    if (response.success) {
      ElMessage.success(config.is_active ? '已启用' : '已禁用')
    }
  } catch (error: any) {
    console.error('更新状态失败:', error)
    ElMessage.error(error.response?.data?.message || '更新失败')
    // 恢复状态
    config.is_active = !config.is_active
  }
}

const handleSave = async () => {
  if (!configFormRef.value) return

  try {
    await configFormRef.value.validate()

    saveLoading.value = true

    // 处理复杂类型的值
    let value = configForm.value
    if (configForm.value_type === 'json' || configForm.value_type === 'array') {
      try {
        value = JSON.parse(configForm.value_text)
      } catch (e) {
        ElMessage.error('JSON格式不正确')
        return
      }
    }

    const configData = {
      ...configForm,
      value
    }

    if (editingConfig.value) {
      // 更新配置
      const response = await systemConfigApi.updateConfig(editingConfig.value.key, configData)
      if (response.success) {
        ElMessage.success('更新成功')
        showCreateDialog.value = false
        loadConfigs()
      }
    } else {
      // 创建配置
      const response = await systemConfigApi.createConfig(configData)
      if (response.success) {
        ElMessage.success('创建成功')
        showCreateDialog.value = false
        loadConfigs()
        loadCategories()
      }
    }
  } catch (error: any) {
    console.error('保存配置失败:', error)
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    saveLoading.value = false
  }
}

const handleExport = async () => {
  try {
    const response = await systemConfigApi.exportConfigs({
      category: searchForm.category,
      format: 'json'
    })
    if (response.success) {
      // 下载JSON文件
      const dataStr = JSON.stringify(response.data, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `system-configs-${new Date().toISOString().split('T')[0]}.json`
      link.click()
      URL.revokeObjectURL(url)

      ElMessage.success('导出成功')
    }
  } catch (error: any) {
    console.error('导出配置失败:', error)
    ElMessage.error(error.response?.data?.message || '导出失败')
  }
}

const handleClearCache = async () => {
  try {
    const response = await systemConfigApi.clearConfigCache()
    if (response.success) {
      ElMessage.success('缓存清除成功')
    }
  } catch (error: any) {
    console.error('清除缓存失败:', error)
    ElMessage.error(error.response?.data?.message || '清除失败')
  }
}

const resetForm = () => {
  if (configFormRef.value) {
    configFormRef.value.resetFields()
  }

  editingConfig.value = null
  Object.assign(configForm, {
    key: '',
    name: '',
    description: '',
    category: '',
    config_type: 'system',
    value_type: 'string',
    value: null,
    value_text: '',
    is_active: true,
    is_required: false,
    is_public: false,
    is_editable: true,
    requires_restart: false,
    sort_order: 0
  })
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadConfigs()
  loadCategories()
})
</script>

<style lang="scss" scoped>
.config-management {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .config-container {
    margin-top: 20px;

    .search-card {
      .actions {
        margin-top: 16px;
        display: flex;
        gap: 12px;
      }
    }

    .table-card {
      margin-top: 20px;

      .pagination {
        margin-top: 20px;
        display: flex;
        justify-content: flex-end;
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>