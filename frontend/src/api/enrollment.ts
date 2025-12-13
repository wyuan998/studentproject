import request from './request'

// 选课接口类型定义
export interface Enrollment {
  id: number
  student_id: number
  student_name: string
  student_no: string
  course_id: number
  course_name: string
  course_code: string
  teacher_id: number
  teacher_name: string
  semester: string
  academic_year: string
  status: 'pending' | 'approved' | 'rejected' | 'dropped'
  enrollment_date: string
  approval_date?: string
  approver_id?: number
  approver_name?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface EnrollmentListParams {
  page?: number
  size?: number
  student_id?: number
  course_id?: number
  teacher_id?: number
  semester?: string
  academic_year?: string
  status?: string
  keyword?: string
}

export interface EnrollmentListResponse {
  items: Enrollment[]
  total: number
  page: number
  size: number
  pages: number
}

export interface EnrollmentCreateParams {
  student_id: number
  course_id: number
  notes?: string
}

export interface EnrollmentUpdateParams {
  status?: 'pending' | 'approved' | 'rejected' | 'dropped'
  notes?: string
}

// API 方法
/**
 * 获取选课列表
 */
export function getEnrollmentList(params: EnrollmentListParams) {
  return request<EnrollmentListResponse>({
    url: '/enrollments',
    method: 'get',
    params
  })
}

/**
 * 获取选课详情
 */
export function getEnrollmentDetail(id: number) {
  return request<Enrollment>({
    url: `/enrollments/${id}`,
    method: 'get'
  })
}

/**
 * 学生选课
 */
export function createEnrollment(data: EnrollmentCreateParams) {
  return request<Enrollment>({
    url: '/enrollments',
    method: 'post',
    data
  })
}

/**
 * 更新选课状态
 */
export function updateEnrollment(id: number, data: EnrollmentUpdateParams) {
  return request<Enrollment>({
    url: `/enrollments/${id}`,
    method: 'put',
    data
  })
}

/**
 * 取消选课
 */
export function cancelEnrollment(id: number) {
  return request({
    url: `/enrollments/${id}`,
    method: 'delete'
  })
}

/**
 * 批量审核选课
 */
export function batchApproveEnrollments(ids: number[], approved: boolean, notes?: string) {
  return request({
    url: '/enrollments/batch-approve',
    method: 'post',
    data: {
      ids,
      approved,
      notes
    }
  })
}

/**
 * 获取学生选课记录
 */
export function getStudentEnrollments(studentId: number, params?: { semester?: string; academic_year?: string }) {
  return request<Enrollment[]>({
    url: `/students/${studentId}/enrollments`,
    method: 'get',
    params
  })
}

/**
 * 获取课程选课学生列表
 */
export function getCourseEnrollments(courseId: number, params?: { status?: string }) {
  return request<Enrollment[]>({
    url: `/courses/${courseId}/enrollments`,
    method: 'get',
    params
  })
}

/**
 * 获取可选修课程列表
 */
export function getAvailableCourses(studentId: number, params?: { semester?: string; academic_year?: string }) {
  return request({
    url: `/students/${studentId}/available-courses`,
    method: 'get',
    params
  })
}

/**
 * 检查选课冲突
 */
export function checkEnrollmentConflict(studentId: number, courseId: number) {
  return request({
    url: '/enrollments/check-conflict',
    method: 'get',
    params: {
      student_id: studentId,
      course_id: courseId
    }
  })
}

/**
 * 导入选课记录
 */
export function importEnrollments(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/enrollments/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出选课记录
 */
export function exportEnrollments(params: EnrollmentListParams) {
  return request({
    url: '/enrollments/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}