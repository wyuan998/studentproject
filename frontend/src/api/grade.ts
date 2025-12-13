import request from './request'

// 成绩接口类型定义
export interface Grade {
  id: number
  student_id: number
  student_name: string
  student_no: string
  course_id: number
  course_name: string
  course_code: string
  teacher_id: number
  teacher_name: string
  enrollment_id: number
  semester: string
  academic_year: string
  grade_type: 'exam' | 'assignment' | 'quiz' | 'project' | 'final'
  grade_name: string
  score: number
  max_score: number
  percentage: number
  grade_letter?: string
  grade_point?: number
  weight: number
  status: 'draft' | 'published' | 'final'
  graded_date?: string
  published_date?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface GradeListParams {
  page?: number
  size?: number
  student_id?: number
  course_id?: number
  teacher_id?: number
  enrollment_id?: number
  semester?: string
  academic_year?: string
  grade_type?: string
  status?: string
  keyword?: string
}

export interface GradeListResponse {
  items: Grade[]
  total: number
  page: number
  size: number
  pages: number
}

export interface GradeCreateParams {
  student_id: number
  course_id: number
  grade_type: 'exam' | 'assignment' | 'quiz' | 'project' | 'final'
  grade_name: string
  score: number
  max_score: number
  weight: number
  notes?: string
}

export interface GradeUpdateParams {
  score?: number
  max_score?: number
  notes?: string
  status?: 'draft' | 'published' | 'final'
}

export interface GradeStatistics {
  total_students: number
  average_score: number
  highest_score: number
  lowest_score: number
  pass_rate: number
  grade_distribution: {
    A: number
    B: number
    C: number
    D: number
    F: number
  }
}

// API 方法
/**
 * 获取成绩列表
 */
export function getGradeList(params: GradeListParams) {
  return request<GradeListResponse>({
    url: '/grades',
    method: 'get',
    params
  })
}

/**
 * 获取成绩详情
 */
export function getGradeDetail(id: number) {
  return request<Grade>({
    url: `/grades/${id}`,
    method: 'get'
  })
}

/**
 * 录入成绩
 */
export function createGrade(data: GradeCreateParams) {
  return request<Grade>({
    url: '/grades',
    method: 'post',
    data
  })
}

/**
 * 更新成绩
 */
export function updateGrade(id: number, data: GradeUpdateParams) {
  return request<Grade>({
    url: `/grades/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除成绩
 */
export function deleteGrade(id: number) {
  return request({
    url: `/grades/${id}`,
    method: 'delete'
  })
}

/**
 * 批量录入成绩
 */
export function batchCreateGrades(data: GradeCreateParams[]) {
  return request({
    url: '/grades/batch',
    method: 'post',
    data
  })
}

/**
 * 发布成绩
 */
export function publishGrades(gradeIds: number[]) {
  return request({
    url: '/grades/publish',
    method: 'post',
    data: { grade_ids: gradeIds }
  })
}

/**
 * 获取学生成绩
 */
export function getStudentGrades(studentId: number, params?: { semester?: string; academic_year?: string }) {
  return request<Grade[]>({
    url: `/students/${studentId}/grades`,
    method: 'get',
    params
  })
}

/**
 * 获取课程成绩
 */
export function getCourseGrades(courseId: number, params?: { grade_type?: string }) {
  return request<Grade[]>({
    url: `/courses/${courseId}/grades`,
    method: 'get',
    params
  })
}

/**
 * 获取课程成绩统计
 */
export function getCourseGradeStatistics(courseId: number) {
  return request<GradeStatistics>({
    url: `/courses/${courseId}/grade-statistics`,
    method: 'get'
  })
}

/**
 * 获取学生成绩统计
 */
export function getStudentGradeStatistics(studentId: number, params?: { semester?: string; academic_year?: string }) {
  return request({
    url: `/students/${studentId}/grade-statistics`,
    method: 'get',
    params
  })
}

/**
 * 导入成绩
 */
export function importGrades(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/grades/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出成绩
 */
export function exportGrades(params: GradeListParams) {
  return request({
    url: '/grades/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 导出成绩单
 */
export function exportTranscript(studentId: number, params?: { semester?: string; academic_year?: string }) {
  return request({
    url: `/students/${studentId}/transcript`,
    method: 'get',
    params,
    responseType: 'blob'
  })
}