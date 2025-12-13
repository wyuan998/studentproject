import request from './request'

// 学生接口类型定义
export interface Student {
  id: number
  student_id: string
  name: string
  gender: '男' | '女'
  birth_date: string
  phone: string
  email: string
  address: string
  class_id: string
  class_name: string
  major: string
  enrollment_date: string
  graduation_date?: string
  status: 'active' | 'graduated' | 'suspended' | 'dropped'
  guardian_name?: string
  guardian_phone?: string
  guardian_relationship?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface StudentListParams {
  page?: number
  size?: number
  keyword?: string
  class_id?: string
  status?: string
  major?: string
}

export interface StudentListResponse {
  items: Student[]
  total: number
  page: number
  size: number
  pages: number
}

export interface StudentCreateParams {
  student_id: string
  name: string
  gender: '男' | '女'
  birth_date: string
  phone: string
  email: string
  address: string
  class_id: string
  major: string
  enrollment_date: string
  guardian_name?: string
  guardian_phone?: string
  guardian_relationship?: string
  notes?: string
}

export interface StudentUpdateParams extends Partial<StudentCreateParams> {
  id?: number
  graduation_date?: string
  status?: 'active' | 'graduated' | 'suspended' | 'dropped'
}

// API 方法
/**
 * 获取学生列表
 */
export function getStudentList(params: StudentListParams) {
  return request<StudentListResponse>({
    url: '/students',
    method: 'get',
    params
  })
}

/**
 * 获取学生详情
 */
export function getStudentDetail(id: number) {
  return request<Student>({
    url: `/students/${id}`,
    method: 'get'
  })
}

/**
 * 创建学生
 */
export function createStudent(data: StudentCreateParams) {
  return request<Student>({
    url: '/students',
    method: 'post',
    data
  })
}

/**
 * 更新学生信息
 */
export function updateStudent(id: number, data: StudentUpdateParams) {
  return request<Student>({
    url: `/students/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除学生
 */
export function deleteStudent(id: number) {
  return request({
    url: `/students/${id}`,
    method: 'delete'
  })
}

/**
 * 批量删除学生
 */
export function batchDeleteStudents(ids: number[]) {
  return request({
    url: '/students/batch',
    method: 'delete',
    data: { ids }
  })
}

/**
 * 导入学生
 */
export function importStudents(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/students/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出学生
 */
export function exportStudents(params: StudentListParams) {
  return request({
    url: '/students/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 获取学生选课记录
 */
export function getStudentEnrollments(studentId: number) {
  return request({
    url: `/students/${studentId}/enrollments`,
    method: 'get'
  })
}

/**
 * 获取学生成绩
 */
export function getStudentGrades(studentId: number, params?: { semester?: string }) {
  return request({
    url: `/students/${studentId}/grades`,
    method: 'get',
    params
  })
}