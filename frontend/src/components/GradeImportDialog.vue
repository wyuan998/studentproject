<template>
  <el-dialog
    v-model="visible"
    title="导入Excel成绩"
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
          <p>1. 请先下载模板文件，按照模板格式填写成绩信息</p>
          <p>2. 支持 Excel (.xlsx, .xls) 格式文件</p>
          <p>3. 学号必须与学生信息匹配，分数不能为空</p>
          <p>4. 同一学生同一考试只能有一条记录</p>
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
          <el-table-column prop="student_name" label="姓名" width="100" />
          <el-table-column prop="score" label="分数" width="80" />
          <el-table-column prop="comments" label="评语" />
        </el-table>
        <p style="margin-top: 10px; color: #409eff;">
          共 {{ previewData.length }} 条数据，有效数据 {{ validCount }} 条
        </p>

        <!-- 错误信息 -->
        <div v-if="errorMessages.length" class="error-section">
          <h5>错误信息</h5>
          <el-alert
            v-for="(error, index) in errorMessages.slice(0, 5)"
            :key="index"
            :title="error"
            type="error"
            :closable="false"
            style="margin-bottom: 5px"
          />
          <p v-if="errorMessages.length > 5" style="color: #f56c6c;">
            还有 {{ errorMessages.length - 5 }} 条错误信息...
          </p>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          @click="handleImport"
          :loading="importing"
          :disabled="!uploadFile || validCount === 0"
        >
          {{ importing ? '导入中...' : '确认导入' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, toRefs, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, UploadFilled } from '@element-plus/icons-vue'
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
const importing = ref(false)
const uploadFile = ref(null)
const uploadRef = ref(null)
const previewData = ref([])
const errorMessages = ref([])

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

// 有效数据计数
const validCount = computed(() => {
  return previewData.value.filter(item =>
    item.student_id &&
    item.score !== null &&
    item.score !== undefined &&
    !isNaN(item.score)
  ).length
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
  errorMessages.value = []
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
      const grades = []
      const errors = []

      jsonData.forEach((row: any, index) => {
        const rowNum = index + 2 // Excel行号（从2开始，因为第一行是标题）

        // 验证必填字段
        if (!row['学号'] && !row['student_id']) {
          errors.push(`第${rowNum}行：学号不能为空`)
          return
        }

        if (row['分数'] === null || row['分数'] === undefined || row['score'] === null || row['score'] === undefined) {
          errors.push(`第${rowNum}行：分数不能为空`)
          return
        }

        const score = parseFloat(row['分数'] || row['score'] || 0)
        if (isNaN(score) || score < 0) {
          errors.push(`第${rowNum}行：分数格式不正确或为负数`)
          return
        }

        grades.push({
          student_id: row['学号'] || row['student_id'] || '',
          student_name: row['姓名'] || row['student_name'] || '',
          score: score,
          comments: row['评语'] || row['comments'] || '',
          row_num: rowNum
        })
      })

      previewData.value = grades
      errorMessages.value = errors

      if (errors.length > 0) {
        ElMessage.warning(`发现 ${errors.length} 个错误，请检查文件格式`)
      } else {
        ElMessage.success(`文件解析成功，共 ${grades.length} 条数据`)
      }
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
      '学号': 'S2021001',
      '姓名': '张三',
      '分数': 85,
      '评语': '表现良好'
    },
    {
      '学号': 'S2021002',
      '姓名': '李四',
      '分数': 92,
      '评语': '优秀'
    },
    {
      '学号': 'S2021003',
      '姓名': '王五',
      '分数': 78,
      '评语': '继续努力'
    }
  ]

  // 创建工作簿
  const wb = XLSX.utils.book_new()
  const ws = XLSX.utils.json_to_sheet(templateData)
  XLSX.utils.book_append_sheet(wb, ws, '成绩导入模板')

  // 下载文件
  XLSX.writeFile(wb, '成绩导入模板.xlsx')
}

// 确认导入
const handleImport = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }

  if (validCount.value === 0) {
    ElMessage.warning('文件中没有有效的成绩数据')
    return
  }

  importing.value = true

  try {
    // 模拟导入过程
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 过滤有效数据
    const validData = previewData.value.filter(item =>
      item.student_id &&
      item.score !== null &&
      item.score !== undefined &&
      !isNaN(item.score)
    )

    // 这里应该调用API进行实际的导入
    // await api.importGrades(validData)

    ElMessage.success(`成功导入 ${validData.length} 条成绩记录`)
    emit('success', validData)
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
  errorMessages.value = []
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

.error-section {
  margin-top: 15px;
}

.error-section h5 {
  margin-bottom: 10px;
  color: #f56c6c;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>