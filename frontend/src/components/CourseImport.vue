<template>
  <el-dialog
    v-model="visible"
    title="批量导入课程"
    width="600px"
    @close="handleClose"
  >
    <div class="import-container">
      <!-- 下载模板 -->
      <el-alert
        title="导入说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #default>
          <p>1. 请先下载模板文件，按照模板格式填写课程信息</p>
          <p>2. 支持 Excel (.xlsx, .xls) 格式文件</p>
          <p>3. 课程代码不能重复，必填字段：课程代码、课程名称、学分、教师、院系、学期</p>
        </template>
      </el-alert>

      <div class="template-download">
        <el-button type="primary" @click="downloadTemplate">
          <el-icon><Download /></el-icon>
          下载模板文件
        </el-button>
      </div>

      <!-- 文件上传 -->
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        drag
        class="upload-area"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xlsx/xls 文件，且不超过 10MB
          </div>
        </template>
      </el-upload>

      <!-- 数据预览 -->
      <div v-if="previewData.length" class="preview-section">
        <h4>数据预览 (前5条)</h4>
        <el-table :data="previewData.slice(0, 5)" border size="small">
          <el-table-column prop="course_code" label="课程代码" width="120" />
          <el-table-column prop="course_name" label="课程名称" width="150" />
          <el-table-column prop="credits" label="学分" width="80" />
          <el-table-column prop="teacher_name" label="授课教师" width="100" />
          <el-table-column prop="semester" label="学期" />
        </el-table>
        <p style="margin-top: 10px; color: #409eff;">
          共 {{ previewData.length }} 条数据
        </p>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          @click="handleImport"
          :loading="importing"
          :disabled="!uploadFile"
        >
          {{ importing ? '导入中...' : '确认导入' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, toRefs } from 'vue'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'

const emit = defineEmits(['success', 'error'])

// 组件属性
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

// 响应式数据
const visible = ref(props.modelValue)
const uploading = ref(false)
const importing = ref(false)
const uploadFile = ref(null)
const uploadRef = ref(null)
const previewData = ref([])

// 监听 modelValue 变化
const { modelValue } = toRefs(props)
watch(modelValue, (val) => {
  visible.value = val
})

// 监听 visible 变化
watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    resetData()
  }
})

// 文件选择处理
const handleFileChange = (file) => {
  uploadFile.value = file.raw
  parseFile(file.raw)
}

// 文件移除处理
const handleFileRemove = () => {
  uploadFile.value = null
  previewData.value = []
}

// 解析文件
const parseFile = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      const sheetName = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[sheetName]
      const jsonData = XLSX.utils.sheet_to_json(worksheet)

      // 转换数据格式
      const courseData = jsonData.map((row: any) => ({
        course_code: row['课程代码'] || '',
        course_name: row['课程名称'] || '',
        credits: row['学分'] || 3,
        hours: row['学时'] || 48,
        course_type: row['课程类型'] || '',
        teacher_name: row['授课教师'] || '',
        teacher_id: row['教师工号'] || '',
        department: row['院系'] || '',
        semester: row['学期'] || '',
        max_students: row['最大人数'] || 50,
        current_students: row['当前人数'] || 0,
        status: row['状态'] || 'active',
        schedule: row['上课时间'] || '',
        location: row['上课地点'] || '',
        description: row['课程描述'] || ''
      }))

      previewData.value = courseData.filter(c => c.course_code && c.course_name)
    } catch (error) {
      console.error('文件解析失败:', error)
      ElMessage.error('文件解析失败，请检查文件格式')
    }
  }
  reader.readAsArrayBuffer(file)
}

// 下载模板
const downloadTemplate = () => {
  // 创建模板数据
  const templateData = [
    {
      '课程代码': 'CS101',
      '课程名称': '计算机科学导论',
      '学分': 3,
      '学时': 48,
      '课程类型': 'required',
      '授课教师': '张教授',
      '教师工号': 'T0001',
      '院系': '计算机科学系',
      '学期': '2025-春季',
      '最大人数': 50,
      '当前人数': 0,
      '状态': 'active',
      '上课时间': '周一 14:00-16:00',
      '上课地点': '教学楼A201',
      '课程描述': '计算机科学基础课程，涵盖基本概念和编程入门。'
    }
  ]

  // 创建工作簿
  const wb = XLSX.utils.book_new()
  const ws = XLSX.utils.json_to_sheet(templateData)
  XLSX.utils.book_append_sheet(wb, ws, '课程信息模板')

  // 下载文件
  XLSX.writeFile(wb, '课程信息导入模板.xlsx')
}

// 确认导入
const handleImport = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }

  if (previewData.value.length === 0) {
    ElMessage.warning('文件中没有有效的课程数据')
    return
  }

  importing.value = true

  try {
    // 模拟导入过程
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 这里应该调用API进行实际的导入
    // await api.importCourses(previewData.value)

    ElMessage.success(`成功导入 ${previewData.value.length} 门课程`)
    emit('success', previewData.value)
    visible.value = false
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败，请稍后重试')
    emit('error', error)
  } finally {
    importing.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}

// 重置数据
const resetData = () => {
  uploadFile.value = null
  previewData.value = []
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}
</script>

<style scoped>
.import-container {
  padding: 10px 0;
}

.template-download {
  text-align: center;
  margin-bottom: 20px;
}

.upload-area {
  width: 100%;
  margin: 20px 0;
}

.preview-section {
  margin-top: 20px;
}

.preview-section h4 {
  margin-bottom: 10px;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>