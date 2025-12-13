<template>
  <div class="message-templates">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">消息模板</span>
      </template>
    </el-page-header>

    <!-- 操作栏 -->
    <div class="action-container">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建模板
      </el-button>
      <el-button @click="handleImport" :loading="importLoading">
        <el-icon><Upload /></el-icon>
        导入模板
      </el-button>
      <el-button @click="handleExport" :loading="exportLoading">
        <el-icon><Download /></el-icon>
        导出模板
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-container">
      <el-form :model="filterForm" :inline="true" size="default">
        <el-form-item label="模板类型">
          <el-select v-model="filterForm.type" placeholder="全部类型" clearable style="width: 150px">
            <el-option label="系统通知" value="system" />
            <el-option label="选课通知" value="enrollment" />
            <el-option label="成绩通知" value="grade" />
            <el-option label="活动通知" value="activity" />
            <el-option label="紧急通知" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 100px">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索模板名称"
            style="width: 200px"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 模板列表 -->
    <el-card>
      <el-table
        v-loading="loading"
        :data="filteredTemplates"
        stripe
        style="width: 100%"
      >
        <el-table-column label="模板名称" prop="name" min-width="200" />
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)">
              {{ getTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标题" prop="title" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="'active'"
              :inactive-value="'disabled'"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="created_at" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="使用次数" prop="usage_count" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              size="small"
              type="success"
              @click="handleUseTemplate(row)"
            >
              使用
            </el-button>
            <el-button
              size="small"
              type="info"
              @click="handlePreview(row)"
            >
              预览
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>

    <!-- 创建/编辑模板对话框 -->
    <el-dialog
      v-model="templateDialogVisible"
      :title="isEdit ? '编辑模板' : '新建模板'"
      width="800px"
    >
      <el-form
        ref="formRef"
        :model="templateForm"
        :rules="templateRules"
        label-width="100px"
        size="default"
      >
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="模板类型" prop="type">
          <el-select v-model="templateForm.type" placeholder="请选择模板类型" style="width: 100%">
            <el-option label="系统通知" value="system" />
            <el-option label="选课通知" value="enrollment" />
            <el-option label="成绩通知" value="grade" />
            <el-option label="活动通知" value="activity" />
            <el-option label="紧急通知" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="消息标题" prop="title">
          <el-input v-model="templateForm.title" placeholder="请输入消息标题" />
        </el-form-item>
        <el-form-item label="消息内容" prop="content">
          <el-input
            v-model="templateForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入消息内容，可以使用变量如：{name}, {course}, {grade}等"
          />
          <div class="template-variables">
            <el-tag
              v-for="variable in getVariablesByType(templateForm.type)"
              :key="variable"
              @click="insertVariable(variable)"
              style="margin-right: 8px; margin-bottom: 8px; cursor: pointer;"
            >
              {{ variable }}
            </el-tag>
          </div>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="templateForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模板描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="templateForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="templateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveTemplate" :loading="saveLoading">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 预览模板对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="模板预览"
      width="600px"
    >
      <div v-if="currentTemplate" class="template-preview">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="模板名称">{{ currentTemplate.name }}</el-descriptions-item>
          <el-descriptions-item label="模板类型">
            <el-tag :type="getTypeColor(currentTemplate.type)">
              {{ getTypeText(currentTemplate.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="标题">{{ currentTemplate.title }}</el-descriptions-item>
          <el-descriptions-item label="内容">{{ currentTemplate.content }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ currentTemplate.description || '无' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentTemplate.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="使用次数">{{ currentTemplate.usage_count }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleUseTemplate(currentTemplate!)">
          使用此模板
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Upload, Download, Search } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const importLoading = ref(false)
const exportLoading = ref(false)
const saveLoading = ref(false)
const templateDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const isEdit = ref(false)
const currentTemplate = ref<any>(null)

interface Template {
  id: number
  name: string
  type: string
  title: string
  content: string
  description: string
  status: 'active' | 'disabled'
  created_at: string
  usage_count: number
}

const filterForm = reactive({
  type: '',
  status: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const templateForm = reactive({
  name: '',
  type: 'system',
  title: '',
  content: '',
  description: '',
  status: 'active'
})

const templateRules: FormRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择模板类型', trigger: 'change' }
  ],
  title: [
    { required: true, message: '请输入消息标题', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入消息内容', trigger: 'blur' }
  ]
}

const templates = ref<Template[]>([])

const filteredTemplates = computed(() => {
  return templates.value.filter(template => {
    const matchType = !filterForm.type || template.type === filterForm.type
    const matchStatus = !filterForm.status || template.status === filterForm.status
    const matchKeyword = !filterForm.keyword ||
      template.name.includes(filterForm.keyword) ||
      template.title.includes(filterForm.keyword)

    return matchType && matchStatus && matchKeyword
  })
})

const loadTemplates = async () => {
  try {
    loading.value = true

    // Mock API call - 替换为实际的API调用
    const mockTemplates: Template[] = [
      {
        id: 1,
        name: '选课开始通知',
        type: 'enrollment',
        title: '{semester}学期选课开始通知',
        content: '亲爱的{name}同学，{semester}学期选课将于{start_time}正式开始，请及时登录系统选课。',
        description: '每学期选课开始时发送给学生',
        status: 'active',
        created_at: '2024-02-20T10:30:00Z',
        usage_count: 156
      },
      {
        id: 2,
        name: '成绩发布通知',
        type: 'grade',
        title: '您的《{course}》课程成绩已发布',
        content: '亲爱的{name}同学，您的《{course}》课程成绩为{grade}分，如有疑问请联系任课教师{teacher}。',
        description: '成绩发布时发送给学生',
        status: 'active',
        created_at: '2024-02-18T14:20:00Z',
        usage_count: 89
      },
      {
        id: 3,
        name: '系统维护通知',
        type: 'system',
        title: '系统维护通知',
        content: '系统将于{maintenance_time}进行维护升级，预计持续{duration}小时，期间系统将无法访问。',
        description: '系统维护时发送给所有用户',
        status: 'active',
        created_at: '2024-02-15T09:15:00Z',
        usage_count: 23
      }
    ]

    templates.value = mockTemplates
    pagination.total = mockTemplates.length
  } catch (error) {
    ElMessage.error('获取模板列表失败')
  } finally {
    loading.value = false
  }
}

const getVariablesByType = (type: string) => {
  const variableMap: Record<string, string[]> = {
    system: ['{maintenance_time}', '{duration}', '{contact}'],
    enrollment: ['{name}', '{semester}', '{start_time}', '{end_time}', '{contact}'],
    grade: ['{name}', '{course}', '{grade}', '{teacher}', '{contact}'],
    activity: ['{name}', '{activity_name}', '{time}', '{location}', '{contact}'],
    urgent: ['{name}', '{content}', '{action_required}', '{contact}']
  }
  return variableMap[type] || []
}

const insertVariable = (variable: string) => {
  templateForm.content += variable
}

const getTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    system: 'primary',
    enrollment: 'success',
    grade: 'warning',
    activity: 'info',
    urgent: 'danger'
  }
  return colorMap[type] || 'info'
}

const getTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    system: '系统通知',
    enrollment: '选课通知',
    grade: '成绩通知',
    activity: '活动通知',
    urgent: '紧急通知'
  }
  return textMap[type] || type
}

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString()
}

const handleSearch = () => {
  // 触发重新计算过滤后的模板
  pagination.page = 1
}

const handleReset = () => {
  filterForm.type = ''
  filterForm.status = ''
  filterForm.keyword = ''
  pagination.page = 1
}

const handleCreate = () => {
  isEdit.value = false
  Object.assign(templateForm, {
    name: '',
    type: 'system',
    title: '',
    content: '',
    description: '',
    status: 'active'
  })
  templateDialogVisible.value = true
}

const handleEdit = (template: Template) => {
  isEdit.value = true
  Object.assign(templateForm, template)
  templateDialogVisible.value = true
}

const handleSaveTemplate = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    saveLoading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success(isEdit.value ? '模板更新成功' : '模板创建成功')
    templateDialogVisible.value = false
    loadTemplates()
  } catch (error) {
    if (error !== 'validation failed') {
      ElMessage.error('保存失败')
    }
  } finally {
    saveLoading.value = false
  }
}

const handlePreview = (template: Template) => {
  currentTemplate.value = template
  previewDialogVisible.value = true
}

const handleUseTemplate = (template: Template) => {
  previewDialogVisible.value = false
  router.push({
    path: '/messages/create',
    query: {
      templateId: template.id
    }
  })
}

const handleStatusChange = async (template: Template) => {
  try {
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 500))

    ElMessage.success(`模板已${template.status === 'active' ? '启用' : '禁用'}`)
  } catch (error) {
    ElMessage.error('状态更新失败')
  }
}

const handleDelete = async (template: Template) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板 "${template.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    const index = templates.value.findIndex(t => t.id === template.id)
    if (index > -1) {
      templates.value.splice(index, 1)
      pagination.total--
    }

    ElMessage.success('模板删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleImport = async () => {
  try {
    importLoading.value = true
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success('模板导入成功')
    loadTemplates()
  } catch (error) {
    ElMessage.error('模板导入失败')
  } finally {
    importLoading.value = false
  }
}

const handleExport = async () => {
  try {
    exportLoading.value = true
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success('模板导出成功')
  } catch (error) {
    ElMessage.error('模板导出失败')
  } finally {
    exportLoading.value = false
  }
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadTemplates()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadTemplates()
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadTemplates()
})
</script>

<style lang="scss" scoped>
.message-templates {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .action-container {
    margin: 20px 0;
    display: flex;
    gap: 12px;
  }

  .filter-container {
    margin: 20px 0;
    padding: 20px;
    background-color: var(--el-bg-color-page);
    border-radius: 8px;
  }

  .template-variables {
    margin-top: 8px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .template-preview {
    // 预览样式
  }
}
</style>