// 用户相关类型定义

export interface User {
  id: number
  username: string
  email: string
  phone?: string
  real_name?: string
  avatar?: string
  status: 'active' | 'inactive' | 'locked'
  roles: string[]
  permissions: string[]
  created_at: string
  updated_at: string
  last_login_at?: string
  created_by?: number
  updated_by?: number
}

export interface Student {
  id: number
  student_id: string
  user_id: number
  real_name: string
  gender: 'male' | 'female' | 'other'
  birth_date?: string
  phone?: string
  email?: string
  address?: string
  avatar?: string
  enrollment_date: string
  graduation_date?: string
  major: string
  class_name: string
  grade: string
  status: 'active' | 'graduated' | 'suspended' | 'withdrawn'
  guardian_name?: string
  guardian_phone?: string
  guardian_email?: string
  emergency_contact?: string
  emergency_phone?: string
  notes?: string
  created_at: string
  updated_at: string
  created_by?: number
  updated_by?: number

  // 关联数据
  user?: User
  enrollments?: Enrollment[]
  grades?: Grade[]
}

export interface Teacher {
  id: number
  teacher_id: string
  user_id?: number
  real_name: string
  gender: 'male' | 'female' | 'other'
  birth_date?: string
  phone?: string
  email?: string
  address?: string
  avatar?: string
  hire_date: string
  department: string
  position?: string
  title?: 'professor' | 'associate_professor' | 'lecturer' | 'assistant'
  office_location?: string
  education?: 'bachelor' | 'master' | 'doctor' | 'postdoctor'
  graduated_from?: string
  research_area?: string
  status: 'active' | 'inactive' | 'on_leave'
  salary?: number
  bio?: string
  skills?: string[]
  emergency_contact?: string
  emergency_phone?: string
  notes?: string
  created_at: string
  updated_at: string
  created_by?: number
  updated_by?: number

  // 关联数据
  user?: User
  teaching_courses?: Course[]
  advisees?: Student[]
}

export interface Course {
  id: number
  course_code: string
  course_name: string
  description?: string
  credits: number
  hours?: number
  course_type?: 'required' | 'elective' | 'general'
  department?: string
  teacher_id?: number
  semester: string
  academic_year?: string
  schedule?: string
  classroom?: string
  max_students?: number
  enrolled_count: number
  status: 'draft' | 'published' | 'archived' | 'cancelled'
  prerequisites?: string[]
  textbooks?: string[]
  syllabus?: string
  objectives?: string
  outcomes?: string
  assessment_methods?: string[]
  start_date?: string
  end_date?: string
  created_at: string
  updated_at: string
  created_by?: number
  updated_by?: number

  // 关联数据
  teacher?: Teacher
  enrollments?: Enrollment[]
  grades?: Grade[]
}

export interface Enrollment {
  id: number
  student_id: number
  course_id: number
  enrollment_date: string
  status: 'pending' | 'approved' | 'rejected' | 'withdrawn' | 'completed'
  approved_by?: number
  approved_at?: string
  rejection_reason?: string
  grade?: string
  credits_earned?: number
  attendance_rate?: number
  final_score?: number
  gpa_points?: number
  notes?: string
  created_at: string
  updated_at: string

  // 关联数据
  student?: Student
  course?: Course
  approver?: User
}

export interface Grade {
  id: number
  enrollment_id: number
  student_id: number
  course_id: number
  assignment_type: 'exam' | 'quiz' | 'homework' | 'project' | 'participation' | 'final'
  assignment_name: string
  score: number
  max_score: number
  percentage: number
  letter_grade?: string
  gpa_points?: number
  weight?: number
  graded_by: number
  graded_at: string
  comments?: string
  extra_credit?: number
  late_penalty?: number
  submission_date?: string
  created_at: string
  updated_at: string

  // 关联数据
  enrollment?: Enrollment
  student?: Student
  course?: Course
  grader?: User
}

export interface Permission {
  id: number
  name: string
  code: string
  description?: string
  resource: string
  action: string
  category: string
  created_at: string
  updated_at: string
}

export interface Role {
  id: number
  name: string
  code: string
  description?: string
  permissions: number[]
  is_default: boolean
  created_at: string
  updated_at: string

  // 关联数据
  permission_details?: Permission[]
}

export interface CreateUserData {
  username: string
  email: string
  password: string
  phone?: string
  real_name?: string
  roles: string[]
  status?: 'active' | 'inactive'
}

export interface UpdateUserData {
  email?: string
  phone?: string
  real_name?: string
  avatar?: string
  status?: 'active' | 'inactive'
  roles?: string[]
}

export interface CreateStudentData {
  student_id: string
  user_id?: number
  real_name: string
  gender: 'male' | 'female' | 'other'
  birth_date?: string
  phone?: string
  email?: string
  address?: string
  avatar?: string
  enrollment_date: string
  graduation_date?: string
  major: string
  class_name: string
  grade: string
  guardian_name?: string
  guardian_phone?: string
  guardian_email?: string
  emergency_contact?: string
  emergency_phone?: string
  notes?: string
}

export interface UpdateStudentData {
  real_name?: string
  gender?: 'male' | 'female' | 'other'
  birth_date?: string
  phone?: string
  email?: string
  address?: string
  avatar?: string
  graduation_date?: string
  major?: string
  class_name?: string
  grade?: string
  status?: 'active' | 'graduated' | 'suspended' | 'withdrawn'
  guardian_name?: string
  guardian_phone?: string
  guardian_email?: string
  emergency_contact?: string
  emergency_phone?: string
  notes?: string
}

export interface CreateTeacherData {
  teacher_id: string
  user_id?: number
  real_name: string
  gender: 'male' | 'female' | 'other'
  birth_date?: string
  phone?: string
  email?: string
  address?: string
  avatar?: string
  hire_date: string
  department: string
  position?: string
  title?: 'professor' | 'associate_professor' | 'lecturer' | 'assistant'
  office_location?: string
  education?: 'bachelor' | 'master' | 'doctor' | 'postdoctor'
  graduated_from?: string
  research_area?: string
  status?: 'active' | 'inactive' | 'on_leave'
  salary?: number
  bio?: string
  skills?: string[]
  emergency_contact?: string
  emergency_phone?: string
  notes?: string
}

export interface UpdateTeacherData {
  real_name?: string
  gender?: 'male' | 'female' | 'other'
  birth_date?: string
  phone?: string
  email?: string
  address?: string
  avatar?: string
  department?: string
  position?: string
  title?: 'professor' | 'associate_professor' | 'lecturer' | 'assistant'
  office_location?: string
  education?: 'bachelor' | 'master' | 'doctor' | 'postdoctor'
  graduated_from?: string
  research_area?: string
  status?: 'active' | 'inactive' | 'on_leave'
  salary?: number
  bio?: string
  skills?: string[]
  emergency_contact?: string
  emergency_phone?: string
  notes?: string
}

// API响应类型
export interface UserResponse<T = any> {
  success: boolean
  message: string
  data?: T
  code?: number
}

export interface PaginatedResponse<T = any> {
  success: boolean
  message: string
  data: {
    items: T[]
    total: number
    page: number
    per_page: number
    pages: number
  }
  code?: number
}

// 查询参数
export interface UserQueryParams {
  page?: number
  per_page?: number
  search?: string
  status?: 'active' | 'inactive' | 'locked'
  role?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface StudentQueryParams {
  page?: number
  per_page?: number
  search?: string
  status?: 'active' | 'graduated' | 'suspended' | 'withdrawn'
  major?: string
  grade?: string
  class_name?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface TeacherQueryParams {
  page?: number
  per_page?: number
  search?: string
  status?: 'active' | 'inactive' | 'on_leave'
  department?: string
  title?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}