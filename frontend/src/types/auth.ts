// 认证相关类型定义

export interface LoginFormData {
  username: string
  password: string
  remember?: boolean
  captcha?: string
}

export interface RegisterFormData {
  username: string
  email: string
  password: string
  confirm_password: string
  phone?: string
  real_name?: string
  student_id?: string
  captcha?: string
  captcha_id?: string
}

export interface UserInfo {
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
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user_info: UserInfo
}

export interface ChangePasswordData {
  old_password: string
  new_password: string
  confirm_password: string
}

export interface UpdateUserInfoData {
  email?: string
  phone?: string
  real_name?: string
  avatar?: string
}

export interface UserProfileData {
  first_name?: string
  last_name?: string
  phone?: string
  gender?: 'male' | 'female' | 'other'
  birthday?: string
  address?: string
  city?: string
  province?: string
  postal_code?: string
  department?: string
  major?: string
  degree?: string
  email?: string
}

export interface CaptchaResponse {
  captcha_id: string
  captcha_image: string
  expires_at: string
}

export interface TokenRefreshResponse {
  access_token: string
  refresh_token?: string
  token_type: string
  expires_in: number
}

export interface ForgotPasswordData {
  email: string
  captcha?: string
}

export interface ResetPasswordData {
  token: string
  new_password: string
  confirm_password: string
}

export interface EmailVerificationData {
  token: string
}

// API响应类型
export interface AuthResponse<T = any> {
  success: boolean
  message: string
  data?: T
  code?: number
}