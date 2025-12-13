<template>
  <div class="message-create">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">发送消息</span>
      </template>
    </el-page-header>

    <div class="form-container">
      <el-card>
        <template #header>
          <span class="card-title">新建消息</span>
        </template>

        <el-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          label-width="120px"
          size="large"
        >
          <el-form-item label="消息类型" prop="type">
            <el-select v-model="formData.type" placeholder="请选择消息类型" style="width: 100%">
              <el-option label="系统通知" value="system" />
              <el-option label="选课通知" value="enrollment" />
              <el-option label="成绩通知" value="grade" />
              <el-option label="活动通知" value="activity" />
              <el-option label="紧急通知" value="urgent" />
            </el-select>
          </el-form-item>

          <el-form-item label="接收对象" prop="receiver_type">
            <el-radio-group v-model="formData.receiver_type" @change="handleReceiverTypeChange">
              <el-radio label="all">全体用户</el-radio>
              <el-radio label="students">全体学生</el-radio>
              <el-radio label="teachers">全体教师</el-radio>
              <el-radio label="class">指定班级</el-radio>
              <el-radio label="major">指定专业</el-radio>
              <el-radio label="individual">指定个人</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 指定班级选择 -->
          <el-form-item v-if="formData.receiver_type === 'class'" label="选择班级" prop="class_ids">
            <el-select
              v-model="formData.class_ids"
              placeholder="请选择班级"
              multiple
              style="width: 100%"
            >
              <el-option
                v-for="cls in classes"
                :key="cls.value"
                :label="cls.label"
                :value="cls.value"
              />
            </el-select>
          </el-form-item>

          <!-- 指定专业选择 -->
          <el-form-item v-if="formData.receiver_type === 'major'" label="选择专业" prop="major_ids">
            <el-select
              v-model="formData.major_ids"
              placeholder="请选择专业"
              multiple
              style="width: 100%"
            >
              <el-option
                v-for="major in majors"
                :key="major.value"
                :label="major.label"
                :value="major.value"
              />
            </el-select>
          </el-form-item>

          <!-- 指定个人选择 -->
          <el-form-item v-if="formData.receiver_type === 'individual'" label="接收人" prop="receiver_ids">
            <el-select
              v-model="formData.receiver_ids"
              placeholder="请选择接收人"
              multiple
              filterable
              remote
              :remote-method="searchUsers"
              style="width: 100%"
            >
              <el-option
                v-for="user in userOptions"
                :key="user.value"
                :label="user.label"
                :value="user.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="消息标题" prop="title">
            <el-input
              v-model="formData.title"
              placeholder="请输入消息标题"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="消息内容" prop="content">
            <el-input
              v-model="formData.content"
              type="textarea"
              :rows="8"
              placeholder="请输入消息内容"
              maxlength="1000"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="发送时间">
            <el-radio-group v-model="formData.send_type">
              <el-radio label="immediate">立即发送</el-radio>
              <el-radio label="scheduled">定时发送</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item v-if="formData.send_type === 'scheduled'" label="发送时间" prop="send_time">
            <el-date-picker
              v-model="formData.send_time"
              type="datetime"
              placeholder="选择发送时间"
              style="width: 100%"
              :disabled-date="disabledDate"
            />
          </el-form-item>

          <el-form-item label="优先级">
            <el-select v-model="formData.priority" placeholder="请选择优先级" style="width: 200px">
              <el-option label="普通" value="normal" />
              <el-option label="重要" value="important" />
              <el-option label="紧急" value="urgent" />
            </el-select>
          </el-form-item>

          <el-form-item label="附件">
            <el-upload
              class="upload-demo"
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :file-list="formData.attachments"
              multiple
            >
              <el-button type="primary">选择文件</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持上传doc, docx, pdf, xls, xlsx, png, jpg等格式，单个文件不超过10MB
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="loading">
              <el-icon><Message /></el-icon>
              发送消息
            </el-button>
            <el-button @click="handlePreview">
              <el-icon><View /></el-icon>
              预览
            </el-button>
            <el-button @click="handleSaveDraft" :loading="draftLoading">
              <el-icon><Document /></el-icon>
              保存草稿
            </el-button>
            <el-button @click="handleBack">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 消息预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="消息预览"
      width="600px"
    >
      <div class="message-preview">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="消息类型">
            <el-tag :type="getTypeColor(formData.type)">
              {{ getTypeText(formData.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="接收对象">{{ getReceiverText() }}</el-descriptions-item>
          <el-descriptions-item label="标题">{{ formData.title }}</el-descriptions-item>
          <el-descriptions-item label="内容">{{ formData.content }}</el-descriptions-item>
          <el-descriptions-item label="发送时间">
            {{ formData.send_type === 'immediate' ? '立即发送' : formatDateTime(formData.send_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityColor(formData.priority)">
              {{ getPriorityText(formData.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="附件">
            <span v-if="formData.attachments.length === 0">无附件</span>
            <div v-else>
              <el-tag
                v-for="(file, index) in formData.attachments"
                :key="index"
                style="margin-right: 8px; margin-bottom: 8px;"
              >
                {{ file.name }}
              </el-tag>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleSendFromPreview">确认发送</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Message, View, Document } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const draftLoading = ref(false)
const previewDialogVisible = ref(false)

interface Option {
  value: number
  label: string
}

const formData = reactive({
  type: 'system',
  receiver_type: 'all',
  class_ids: [] as number[],
  major_ids: [] as number[],
  receiver_ids: [] as number[],
  title: '',
  content: '',
  send_type: 'immediate',
  send_time: '',
  priority: 'normal',
  attachments: [] as any[]
})

const rules: FormRules = {
  type: [
    { required: true, message: '请选择消息类型', trigger: 'change' }
  ],
  receiver_type: [
    { required: true, message: '请选择接收对象', trigger: 'change' }
  ],
  class_ids: [
    { required: true, message: '请选择班级', trigger: 'change' }
  ],
  major_ids: [
    { required: true, message: '请选择专业', trigger: 'change' }
  ],
  receiver_ids: [
    { required: true, message: '请选择接收人', trigger: 'change' }
  ],
  title: [
    { required: true, message: '请输入消息标题', trigger: 'blur' },
    { min: 5, max: 100, message: '标题长度在5-100个字符之间', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入消息内容', trigger: 'blur' },
    { min: 10, max: 1000, message: '内容长度在10-1000个字符之间', trigger: 'blur' }
  ],
  send_time: [
    { required: true, message: '请选择发送时间', trigger: 'change' }
  ]
}

const classes = ref<Option[]>([])
const majors = ref<Option[]>([])
const userOptions = ref<Option[]>([])

const loadClasses = async () => {
  try {
    const mockClasses: Option[] = [
      { value: 1, label: '计算机科学1班' },
      { value: 2, label: '计算机科学2班' },
      { value: 3, label: '软件工程1班' },
      { value: 4, label: '软件工程2班' },
      { value: 5, label: '数据科学1班' }
    ]
    classes.value = mockClasses
  } catch (error) {
    ElMessage.error('获取班级列表失败')
  }
}

const loadMajors = async () => {
  try {
    const mockMajors: Option[] = [
      { value: 1, label: '计算机科学' },
      { value: 2, label: '软件工程' },
      { value: 3, label: '数据科学' },
      { value: 4, label: '人工智能' }
    ]
    majors.value = mockMajors
  } catch (error) {
    ElMessage.error('获取专业列表失败')
  }
}

const searchUsers = async (query: string) => {
  if (!query) {
    userOptions.value = []
    return
  }

  try {
    // Mock API call - 替换为实际的API调用
    const mockUsers: Option[] = [
      { value: 1, label: '张三 (S2021001)' },
      { value: 2, label: '李四 (S2021002)' },
      { value: 3, label: '王五 (S2021003)' },
      { value: 4, label: '李老师 (T001)' },
      { value: 5, label: '王老师 (T002)' }
    ]

    userOptions.value = mockUsers.filter(user =>
      user.label.toLowerCase().includes(query.toLowerCase())
    )
  } catch (error) {
    ElMessage.error('搜索用户失败')
  }
}

const handleReceiverTypeChange = (value: string) => {
  // 清空之前的选择
  formData.class_ids = []
  formData.major_ids = []
  formData.receiver_ids = []
  userOptions.value = []
}

const disabledDate = (time: Date) => {
  return time.getTime() < Date.now() - 24 * 60 * 60 * 1000
}

const handleFileChange = (file: any, fileList: any[]) => {
  formData.attachments = fileList
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

const getReceiverText = () => {
  const typeMap: Record<string, string> = {
    all: '全体用户',
    students: '全体学生',
    teachers: '全体教师',
    class: `指定班级 (${formData.class_ids.length}个)`,
    major: `指定专业 (${formData.major_ids.length}个)`,
    individual: `指定个人 (${formData.receiver_ids.length}人)`
  }
  return typeMap[formData.receiver_type] || '未指定'
}

const getPriorityColor = (priority: string) => {
  const colorMap: Record<string, string> = {
    normal: 'info',
    important: 'warning',
    urgent: 'danger'
  }
  return colorMap[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const textMap: Record<string, string> = {
    normal: '普通',
    important: '重要',
    urgent: '紧急'
  }
  return textMap[priority] || '普通'
}

const formatDateTime = (dateTime: string | Date) => {
  return new Date(dateTime).toLocaleString()
}

const handlePreview = () => {
  // 基本验证
  if (!formData.title || !formData.content) {
    ElMessage.warning('请填写消息标题和内容')
    return
  }

  previewDialogVisible.value = true
}

const handleSendFromPreview = () => {
  previewDialogVisible.value = false
  handleSubmit()
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // 根据接收对象类型验证相应字段
    if (formData.receiver_type === 'class' && formData.class_ids.length === 0) {
      ElMessage.error('请选择至少一个班级')
      return
    }
    if (formData.receiver_type === 'major' && formData.major_ids.length === 0) {
      ElMessage.error('请选择至少一个专业')
      return
    }
    if (formData.receiver_type === 'individual' && formData.receiver_ids.length === 0) {
      ElMessage.error('请选择至少一个接收人')
      return
    }
    if (formData.send_type === 'scheduled' && !formData.send_time) {
      ElMessage.error('请选择发送时间')
      return
    }

    loading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1500))

    ElMessage.success('消息发送成功')
    router.push('/messages')
  } catch (error) {
    if (error !== 'validation failed') {
      ElMessage.error('消息发送失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSaveDraft = async () => {
  if (!formData.title || !formData.content) {
    ElMessage.warning('请填写消息标题和内容')
    return
  }

  try {
    draftLoading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('草稿保存成功')
  } catch (error) {
    ElMessage.error('草稿保存失败')
  } finally {
    draftLoading.value = false
  }
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadClasses()
  loadMajors()
})
</script>

<style lang="scss" scoped>
.message-create {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .form-container {
    margin-top: 20px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
    }
  }

  .message-preview {
    .el-tag {
      margin-right: 8px;
      margin-bottom: 8px;
    }
  }
}
</style>