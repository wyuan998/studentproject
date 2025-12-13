import request from './request'

// 课程接口类型定义
export interface Course {
  id: number
  course_code: string
  name: string
  description: string
  credits: number
  hours: number
  teacher_id: number
  teacher_name: string
  semester: string
  academic_year: string
  max_students: number
  current_students: number
  status: 'draft' | 'published' | 'ongoing' | 'completed' | 'cancelled'
  schedule?: string
  classroom?: string
  prerequisites?: string[]
  created_at: string
  updated_at: string
}

export interface CourseListParams {
  page?: number
  size?: number
  keyword?: string
  teacher_id?: number
  semester?: string
  academic_year?: string
  status?: string
}

export interface CourseListResponse {
  items: Course[]
  total: number
  page: number
  size: number
  pages: number
}

export interface CourseCreateParams {
  course_code: string
  name: string
  description: string
  credits: number
  hours: number
  teacher_id: number
  semester: string
  academic_year: string
  max_students: number
  schedule?: string
  classroom?: string
  prerequisites?: string[]
}

export interface CourseUpdateParams extends Partial<CourseCreateParams> {
  id?: number
  status?: 'draft' | 'published' | 'ongoing' | 'completed' | 'cancelled'
}

// API 方法
/**
 * 获取课程列表
 */
export function getCourseList(params: CourseListParams) {
  return request<CourseListResponse>({
    url: '/courses',
    method: 'get',
    params
  })
}

/**
 * 获取课程详情
 */
export function getCourseDetail(id: number) {
  return request<Course>({
    url: `/courses/${id}`,
    method: 'get'
  })
}

/**
 * 创建课程
 */
export function createCourse(data: CourseCreateParams) {
  return request<Course>({
    url: '/courses',
    method: 'post',
    data
  })
}

/**
 * 更新课程信息
 */
export function updateCourse(id: number, data: CourseUpdateParams) {
  return request<Course>({
    url: `/courses/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除课程
 */
export function deleteCourse(id: number) {
  return request({
    url: `/courses/${id}`,
    method: 'delete'
  })
}

/**
 * 获取课程学生列表
 */
export function getCourseStudents(courseId: number) {
  return request({
    url: `/courses/${courseId}/students`,
    method: 'get'
  })
}

/**
 * 获取教师课程列表
 */
export function getTeacherCourses(teacherId: number) {
  return request<Course[]>({
    url: `/teachers/${teacherId}/courses`,
    method: 'get'
  })
}

/**
 * 导入课程
 */
export function importCourses(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/courses/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出课程
 */
export function exportCourses(params: CourseListParams) {
  return request({
    url: '/courses/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}