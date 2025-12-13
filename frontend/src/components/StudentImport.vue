<template>
  <el-dialog
    v-model="visible"
    title="批量导入学生"
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
          <p>1. 请先下载模板文件，按照模板格式填写学生信息</p>
          <p>2. 支持 Excel (.xlsx, .xls) 格式文件</p>
          <p>3. 学号不能重复，必填字段：学号、姓名、性别、专业、班级</p>
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
          <el-table-column prop="student_id" label="学号" width="120" />
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column prop="gender" label="性别" width="80" />
          <el-table-column prop="major" label="专业" />
          <el-table-column prop="class_name" label="班级" width="120" />
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
import { ref } from 'vue'
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
      const students = jsonData.map((row: any) => ({
        student_id: row['学号'] || '',
        name: row['姓名'] || '',
        gender: row['性别'] || '',
        birth_date: row['出生日期'] || '',
        phone: row['电话'] || '',
        email: row['邮箱'] || '',
        major: row['专业'] || '',
        class_name: row['班级'] || '',
        status: row['状态'] || 'active',
        enrollment_date: row['入学时间'] || '',
        address: row['家庭地址'] || ''
      }))

      previewData.value = students.filter(s => s.student_id && s.name)
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
      '学号': 'S2024001',
      '姓名': '张三',
      '性别': '男',
      '出生日期': '2000-01-01',
      '电话': '13800138000',
      '邮箱': 'zhangsan@example.com',
      '专业': '计算机科学',
      '班级': '计算机科学1班',
      '状态': 'active',
      '入学时间': '2020-09-01',
      '家庭地址': '北京市海淀区'
    }
  ]

  // 创建工作簿
  const wb = XLSX.utils.book_new()
  const ws = XLSX.utils.json_to_sheet(templateData)
  XLSX.utils.book_append_sheet(wb, ws, '学生信息模板')

  // 下载文件
  XLSX.writeFile(wb, '学生信息导入模板.xlsx')
}

// 确认导入
const handleImport = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }

  if (previewData.value.length === 0) {
    ElMessage.warning('文件中没有有效的学生数据')
    return
  }

  importing.value = true

  try {
    // 模拟导入过程
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 这里应该调用API进行实际的导入
    // await api.importStudents(previewData.value)

    ElMessage.success(`成功导入 ${previewData.value.length} 名学生`)
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