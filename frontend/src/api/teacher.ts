import request from './request'

// 教师接口类型定义
export interface Teacher {
  id: number
  teacher_id: string
  name: string
  gender: '男' | '女'
  birth_date: string
  phone: string
  email: string
  address: string
  department: string
  title: string
  specialization: string
  education: string
  hire_date: string
  status: 'active' | 'inactive' | 'retired'
  office?: string
  office_hours?: string
  bio?: string
  created_at: string
  updated_at: string
}

export interface TeacherListParams {
  page?: number
  size?: number
  keyword?: string
  department?: string
  title?: string
  status?: string
}

export interface TeacherListResponse {
  items: Teacher[]
  total: number
  page: number
  size: number
  pages: number
}

export interface TeacherCreateParams {
  teacher_id: string
  name: string
  gender: '男' | '女'
  birth_date: string
  phone: string
  email: string
  address: string
  department: string
  title: string
  specialization: string
  education: string
  hire_date: string
  office?: string
  office_hours?: string
  bio?: string
}

export interface TeacherUpdateParams extends Partial<TeacherCreateParams> {
  id?: number
  status?: 'active' | 'inactive' | 'retired'
}

// API 方法
/**
 * 获取教师列表
 */
export function getTeacherList(params: TeacherListParams) {
  return request<TeacherListResponse>({
    url: '/teachers',
    method: 'get',
    params
  })
}

/**
 * 获取教师详情
 */
export function getTeacherDetail(id: number) {
  return request<Teacher>({
    url: `/teachers/${id}`,
    method: 'get'
  })
}

/**
 * 创建教师
 */
export function createTeacher(data: TeacherCreateParams) {
  return request<Teacher>({
    url: '/teachers',
    method: 'post',
    data
  })
}

/**
 * 更新教师信息
 */
export function updateTeacher(id: number, data: TeacherUpdateParams) {
  return request<Teacher>({
    url: `/teachers/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除教师
 */
export function deleteTeacher(id: number) {
  return request({
    url: `/teachers/${id}`,
    method: 'delete'
  })
}

/**
 * 批量删除教师
 */
export function batchDeleteTeachers(ids: number[]) {
  return request({
    url: '/teachers/batch',
    method: 'delete',
    data: { ids }
  })
}

/**
 * 获取教师课程列表
 */
export function getTeacherCourseList(teacherId: number, params?: { semester?: string; academic_year?: string }) {
  return request({
    url: `/teachers/${teacherId}/courses`,
    method: 'get',
    params
  })
}

/**
 * 获取教师统计数据
 */
export function getTeacherStatistics(teacherId: number) {
  return request({
    url: `/teachers/${teacherId}/statistics`,
    method: 'get'
  })
}

/**
 * 导入教师
 */
export function importTeachers(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/teachers/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出教师
 */
export function exportTeachers(params: TeacherListParams) {
  return request({
    url: '/teachers/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}