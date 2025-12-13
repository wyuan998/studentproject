import request from './request'

// API 分组导出
export const gradeApi = {
  getGrades,
  getGrade,
  createGrade,
  updateGrade,
  deleteGrade,
  publishGrade,
  lockGrade,
  bulkCreateGrades,
  getStudentGradeSummary,
  getCourseGradeStatistics,
  getGradeStatistics,
  importGrades,
  exportGrades
}

// 成绩接口类型定义
export interface Grade {
  id: string
  student_id: string
  student_name?: string
  student_id?: string
  course_id: string
  course_name?: string
  course_code?: string
  teacher_id?: string
  teacher_name?: string
  exam_type: 'quiz' | 'assignment' | 'midterm' | 'final' | 'project' | 'presentation' | 'participation' | 'lab' | 'attendance' | 'other'
  exam_name: string
  score: number
  max_score: number
  weight: number
  semester: string
  percentage?: number
  letter_grade?: string
  grade_point?: number
  is_published: boolean
  is_locked: boolean
  published_at?: string
  graded_by?: string
  graded_at?: string
  comments?: string
  improvement_suggestions?: string
  class_average?: number
  class_max?: number
  class_min?: number
  percentile?: number
  created_at: string
  updated_at: string
}

export interface GradeListParams {
  page?: number
  per_page?: number
  keyword?: string
  student_id?: string
  course_id?: string
  teacher_id?: string
  exam_type?: string
  semester?: string
  score_min?: number
  score_max?: number
  is_published?: boolean
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface GradeListResponse {
  grades: Grade[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface GradeCreateParams {
  student_id: string
  course_id: string
  exam_type: 'quiz' | 'assignment' | 'midterm' | 'final' | 'project' | 'presentation' | 'participation' | 'lab' | 'attendance' | 'other'
  exam_name: string
  score: number
  max_score?: number
  weight?: number
  semester: string
  comments?: string
  improvement_suggestions?: string
}

export interface GradeUpdateParams {
  score?: number
  max_score?: number
  weight?: number
  comments?: string
  improvement_suggestions?: string
  is_published?: boolean
  is_locked?: boolean
}

export interface BulkGradeParams {
  course_id: string
  exam_type: 'quiz' | 'assignment' | 'midterm' | 'final' | 'project' | 'presentation' | 'participation' | 'lab' | 'attendance' | 'other'
  exam_name: string
  max_score: number
  weight?: number
  semester: string
  grades: Array<{
    student_id: string
    score: number
    comments?: string
  }>
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
export function getGrades(params: GradeListParams) {
  return request<GradeListResponse>({
    url: '/grades',
    method: 'get',
    params
  })
}

/**
 * 获取成绩详情
 */
export function getGrade(id: string) {
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
export function updateGrade(id: string, data: GradeUpdateParams) {
  return request<Grade>({
    url: `/grades/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除成绩
 */
export function deleteGrade(id: string) {
  return request({
    url: `/grades/${id}`,
    method: 'delete'
  })
}

/**
 * 发布成绩
 */
export function publishGrade(id: string) {
  return request({
    url: `/grades/${id}/publish`,
    method: 'post'
  })
}

/**
 * 锁定成绩
 */
export function lockGrade(id: string) {
  return request({
    url: `/grades/${id}/lock`,
    method: 'post'
  })
}

/**
 * 批量录入成绩
 */
export function bulkCreateGrades(data: BulkGradeParams) {
  return request({
    url: '/grades/bulk',
    method: 'post',
    data
  })
}

/**
 * 获取学生成绩汇总
 */
export function getStudentGradeSummary(studentId: string) {
  return request({
    url: `/grades/student/${studentId}/summary`,
    method: 'get'
  })
}

/**
 * 获取课程成绩统计
 */
export function getCourseGradeStatistics(courseId: string) {
  return request({
    url: `/grades/course/${courseId}/statistics`,
    method: 'get'
  })
}

/**
 * 获取成绩统计信息
 */
export function getGradeStatistics() {
  return request({
    url: '/grades/statistics',
    method: 'get'
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
export function exportGrades(params?: {
  course_id?: string
  semester?: string
  exam_type?: string
  format?: string
}) {
  return request({
    url: '/grades/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}