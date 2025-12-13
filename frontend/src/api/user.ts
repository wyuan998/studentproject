import { request } from './request'
import type {
  User,
  Student,
  Teacher,
  Course,
  Enrollment,
  Grade,
  Permission,
  Role,
  CreateUserData,
  UpdateUserData,
  CreateStudentData,
  UpdateStudentData,
  CreateTeacherData,
  UpdateTeacherData,
  UserQueryParams,
  StudentQueryParams,
  TeacherQueryParams,
  UserResponse,
  PaginatedResponse
} from '@/types/user'

// 用户API
export const userApi = {
  // 获取用户列表
  getUsers: (params?: UserQueryParams) =>
    request.get<PaginatedResponse<User>>('/users', { params }),

  // 获取用户详情
  getUser: (id: number) =>
    request.get<UserResponse<User>>(`/users/${id}`),

  // 创建用户
  createUser: (data: CreateUserData) =>
    request.post<UserResponse<User>>('/users', data),

  // 更新用户
  updateUser: (id: number, data: UpdateUserData) =>
    request.put<UserResponse<User>>(`/users/${id}`, data),

  // 删除用户
  deleteUser: (id: number) =>
    request.delete(`/users/${id}`),

  // 批量删除用户
  batchDeleteUsers: (ids: number[]) =>
    request.post('/users/batch-delete', { ids }),

  // 更改用户状态
  updateUserStatus: (id: number, status: 'active' | 'inactive' | 'locked') =>
    request.patch(`/users/${id}/status`, { status }),

  // 重置用户密码
  resetUserPassword: (id: number, newPassword: string) =>
    request.post(`/users/${id}/reset-password`, { new_password: newPassword }),

  // 获取用户权限
  getUserPermissions: (userId?: number) =>
    request.get<UserResponse<{ permissions: string[]; roles: string[] }>>(
      userId ? `/users/${userId}/permissions` : '/users/permissions'
    ),

  // 更新用户权限
  updateUserPermissions: (id: number, roles: string[]) =>
    request.put(`/users/${id}/permissions`, { roles }),

  // 导出用户数据
  exportUsers: (params?: UserQueryParams) =>
    request.get('/users/export', { params, responseType: 'blob' }),

  // 导入用户数据
  importUsers: (formData: FormData) =>
    request.upload('/users/import', formData),

  // 获取用户统计
  getUserStats: () =>
    request.get<UserResponse<any>>('/users/stats')
}

// 学生API
export const studentApi = {
  // 获取学生列表
  getStudents: (params?: StudentQueryParams) =>
    request.get<PaginatedResponse<Student>>('/students', { params }),

  // 获取学生详情
  getStudent: (id: number) =>
    request.get<UserResponse<Student>>(`/students/${id}`),

  // 创建学生
  createStudent: (data: CreateStudentData) =>
    request.post<UserResponse<Student>>('/students', data),

  // 更新学生
  updateStudent: (id: number, data: UpdateStudentData) =>
    request.put<UserResponse<Student>>(`/students/${id}`, data),

  // 删除学生
  deleteStudent: (id: number) =>
    request.delete(`/students/${id}`),

  // 批量删除学生
  batchDeleteStudents: (ids: number[]) =>
    request.post('/students/batch-delete', { ids }),

  // 更改学生状态
  updateStudentStatus: (id: number, status: 'active' | 'graduated' | 'suspended' | 'withdrawn') =>
    request.patch(`/students/${id}/status`, { status }),

  // 获取学生选课记录
  getStudentEnrollments: (studentId: number, params?: { page?: number; per_page?: number }) =>
    request.get<PaginatedResponse<Enrollment>>(`/students/${studentId}/enrollments`, { params }),

  // 获取学生成绩
  getStudentGrades: (studentId: number, params?: { page?: number; per_page?: number; course_id?: number }) =>
    request.get<PaginatedResponse<Grade>>(`/students/${studentId}/grades`, { params }),

  // 获取学生GPA
  getStudentGPA: (studentId: number) =>
    request.get<UserResponse<{ gpa: number; credits: number; rank?: number }>>(`/students/${studentId}/gpa`),

  // 导出学生数据
  exportStudents: (params?: StudentQueryParams) =>
    request.get('/students/export', { params, responseType: 'blob' }),

  // 导入学生数据
  importStudents: (formData: FormData) =>
    request.upload('/students/import', formData),

  // 获取学生统计
  getStudentStats: () =>
    request.get<UserResponse<any>>('/students/stats'),

  // 搜索学生
  searchStudents: (query: string) =>
    request.get<UserResponse<Student[]>>('/students/search', { params: { q: query } })
}

// 教师API
export const teacherApi = {
  // 获取教师列表
  getTeachers: (params?: TeacherQueryParams) =>
    request.get<PaginatedResponse<Teacher>>('/teachers', { params }),

  // 获取教师详情
  getTeacher: (id: number) =>
    request.get<UserResponse<Teacher>>(`/teachers/${id}`),

  // 创建教师
  createTeacher: (data: CreateTeacherData) =>
    request.post<UserResponse<Teacher>>('/teachers', data),

  // 更新教师
  updateTeacher: (id: number, data: UpdateTeacherData) =>
    request.put<UserResponse<Teacher>>(`/teachers/${id}`, data),

  // 删除教师
  deleteTeacher: (id: number) =>
    request.delete(`/teachers/${id}`),

  // 批量删除教师
  batchDeleteTeachers: (ids: number[]) =>
    request.post('/teachers/batch-delete', { ids }),

  // 更改教师状态
  updateTeacherStatus: (id: number, status: 'active' | 'inactive' | 'retired') =>
    request.patch(`/teachers/${id}/status`, { status }),

  // 获取教师授课记录
  getTeacherCourses: (teacherId: number, params?: { page?: number; per_page?: number; semester?: string }) =>
    request.get<PaginatedResponse<Course>>(`/teachers/${teacherId}/courses`, { params }),

  // 获取教师指导学生
  getTeacherAdvisees: (teacherId: number, params?: { page?: number; per_page?: number }) =>
    request.get<PaginatedResponse<Student>>(`/teachers/${teacherId}/advisees`, { params }),

  // 获取教师工作量
  getTeacherWorkload: (teacherId: number, semester?: string) =>
    request.get<UserResponse<any>>(`/teachers/${teacherId}/workload`, { params: { semester } }),

  // 导出教师数据
  exportTeachers: (params?: TeacherQueryParams) =>
    request.get('/teachers/export', { params, responseType: 'blob' }),

  // 导入教师数据
  importTeachers: (formData: FormData) =>
    request.upload('/teachers/import', formData),

  // 获取教师统计
  getTeacherStats: () =>
    request.get<UserResponse<any>>('/teachers/stats'),

  // 搜索教师
  searchTeachers: (query: string) =>
    request.get<UserResponse<Teacher[]>>('/teachers/search', { params: { q: query } })
}

// 权限API
export const permissionApi = {
  // 获取权限列表
  getPermissions: () =>
    request.get<UserResponse<{ permissions: Permission[]; roles: Role[] }>>('/permissions'),

  // 获取角色列表
  getRoles: () =>
    request.get<UserResponse<Role[]>>('/roles'),

  // 创建角色
  createRole: (data: { name: string; code: string; description?: string; permissions: number[] }) =>
    request.post<UserResponse<Role>>('/roles', data),

  // 更新角色
  updateRole: (id: number, data: Partial<{ name: string; description?: string; permissions: number[] }>) =>
    request.put<UserResponse<Role>>(`/roles/${id}`, data),

  // 删除角色
  deleteRole: (id: number) =>
    request.delete(`/roles/${id}`),

  // 获取角色详情
  getRole: (id: number) =>
    request.get<UserResponse<Role>>(`/roles/${id}`),

  // 分配角色权限
  assignRolePermissions: (roleId: number, permissionIds: number[]) =>
    request.put(`/roles/${roleId}/permissions`, { permission_ids: permissionIds })
}