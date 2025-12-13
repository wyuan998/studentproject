import request from './request'

// 报表接口类型定义
export interface ReportParams {
  start_date?: string
  end_date?: string
  semester?: string
  academic_year?: string
  department?: string
  class_id?: string
  format?: 'json' | 'excel' | 'pdf'
}

export interface StudentReport {
  total_count: number
  active_count: number
  graduated_count: number
  suspended_count: number
  dropped_count: number
  gender_distribution: {
    male: number
    female: number
  }
  class_distribution: Record<string, number>
  major_distribution: Record<string, number>
  enrollment_trend: Array<{
    date: string
    count: number
  }>
}

export interface TeacherReport {
  total_count: number
  active_count: number
  department_distribution: Record<string, number>
  title_distribution: Record<string, number>
  average_courses: number
  average_students: number
}

export interface CourseReport {
  total_count: number
  active_count: number
  completed_count: number
  average_enrollment: number
  popular_courses: Array<{
    course_name: string
    enrollment_count: number
  }>
  completion_rate: number
}

export interface GradeReport {
  total_grades: number
  average_score: number
  pass_rate: number
  grade_distribution: {
    A: number
    B: number
    C: number
    D: number
    F: number
  }
  course_performance: Array<{
    course_name: string
    average_score: number
    pass_rate: number
  }>
}

export interface EnrollmentReport {
  total_enrollments: number
  pending_count: number
  approved_count: number
  rejected_count: number
  enrollment_trend: Array<{
    date: string
    count: number
  }>
  popular_courses: Array<{
    course_name: string
    enrollment_count: number
  }>
  department_stats: Record<string, {
    enrollments: number
    approval_rate: number
  }>
}

export interface SystemReport {
  user_stats: {
    total_users: number
    active_users: number
    new_users_today: number
    new_users_this_month: number
  }
  activity_stats: {
    total_actions: number
    actions_today: number
    most_active_users: Array<{
      user_name: string
      action_count: number
    }>
  }
  performance_stats: {
    average_response_time: number
    error_rate: number
    uptime: number
  }
}

// API 方法
/**
 * 获取学生报表
 */
export function getStudentReport(params: ReportParams) {
  return request<StudentReport>({
    url: '/reports/students',
    method: 'get',
    params
  })
}

/**
 * 获取教师报表
 */
export function getTeacherReport(params: ReportParams) {
  return request<TeacherReport>({
    url: '/reports/teachers',
    method: 'get',
    params
  })
}

/**
 * 获取课程报表
 */
export function getCourseReport(params: ReportParams) {
  return request<CourseReport>({
    url: '/reports/courses',
    method: 'get',
    params
  })
}

/**
 * 获取成绩报表
 */
export function getGradeReport(params: ReportParams) {
  return request<GradeReport>({
    url: '/reports/grades',
    method: 'get',
    params
  })
}

/**
 * 获取选课报表
 */
export function getEnrollmentReport(params: ReportParams) {
  return request<EnrollmentReport>({
    url: '/reports/enrollments',
    method: 'get',
    params
  })
}

/**
 * 获取系统报表
 */
export function getSystemReport(params: ReportParams) {
  return request<SystemReport>({
    url: '/reports/system',
    method: 'get',
    params
  })
}

/**
 * 导出学生报表
 */
export function exportStudentReport(params: ReportParams) {
  return request({
    url: '/reports/students/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 导出教师报表
 */
export function exportTeacherReport(params: ReportParams) {
  return request({
    url: '/reports/teachers/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 导出课程报表
 */
export function exportCourseReport(params: ReportParams) {
  return request({
    url: '/reports/courses/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 导出成绩报表
 */
export function exportGradeReport(params: ReportParams) {
  return request({
    url: '/reports/grades/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 导出选课报表
 */
export function exportEnrollmentReport(params: ReportParams) {
  return request({
    url: '/reports/enrollments/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 导出综合报表
 */
export function exportComprehensiveReport(params: ReportParams & {
  include_students?: boolean
  include_teachers?: boolean
  include_courses?: boolean
  include_grades?: boolean
  include_enrollments?: boolean
}) {
  return request({
    url: '/reports/comprehensive/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 获取仪表板数据
 */
export function getDashboardData() {
  return request({
    url: '/reports/dashboard',
    method: 'get'
  })
}

/**
 * 获取实时统计数据
 */
export function getRealTimeStats() {
  return request({
    url: '/reports/realtime-stats',
    method: 'get'
  })
}

/**
 * 获取趋势数据
 */
export function getTrendData(params: {
  metric: string
  period: 'day' | 'week' | 'month' | 'year'
  start_date?: string
  end_date?: string
}) {
  return request({
    url: '/reports/trends',
    method: 'get',
    params
  })
}

/**
 * 获取对比数据
 */
export function getComparisonData(params: {
  metric: string
  compare_type: 'period' | 'department' | 'class'
  periods?: string[]
  departments?: string[]
  classes?: string[]
}) {
  return request({
    url: '/reports/comparison',
    method: 'get',
    params
  })
}

/**
 * 生成自定义报表
 */
export function generateCustomReport(data: {
  name: string
  description: string
  data_sources: string[]
  filters: Record<string, any>
  aggregations: Array<{
    field: string
    operation: string
    alias?: string
  }>
  group_by?: string[]
  order_by?: Array<{
    field: string
    direction: 'asc' | 'desc'
  }>
}) {
  return request({
    url: '/reports/custom',
    method: 'post',
    data
  })
}