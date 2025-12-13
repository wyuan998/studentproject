import { request } from './request'
import type {
  LoginFormData,
  RegisterFormData,
  UserInfo,
  LoginResponse,
  ChangePasswordData,
  UpdateUserInfoData,
  ForgotPasswordData,
  ResetPasswordData,
  EmailVerificationData,
  CaptchaResponse,
  AuthResponse
} from '@/types/auth'

export const authApi = {
  // 登录
  login: (data: LoginFormData) =>
    request.post<LoginResponse>('/auth/login', data),

  // 注册
  register: (data: RegisterFormData) =>
    request.post<any>('/auth/register', data),

  // 登出
  logout: () =>
    request.post('/auth/logout'),

  // 刷新Token
  refreshToken: (refreshToken: string) =>
    request.post('/auth/refresh', { refresh_token: refreshToken }),

  // 获取用户信息
  getUserInfo: () =>
    request.get<UserInfo>('/auth/me'),

  // 修改密码
  changePassword: (data: ChangePasswordData) =>
    request.post('/auth/change-password', data),

  // 更新用户信息
  updateUserInfo: (data: UpdateUserInfoData) =>
    request.put('/auth/profile', data),

  // 忘记密码
  forgotPassword: (data: ForgotPasswordData) =>
    request.post('/auth/forgot-password', data),

  // 重置密码
  resetPassword: (data: ResetPasswordData) =>
    request.post('/auth/reset-password', data),

  // 验证邮箱
  verifyEmail: (data: EmailVerificationData) =>
    request.post('/auth/verify-email', data),

  // 重新发送验证邮件
  resendVerificationEmail: (email: string) =>
    request.post('/auth/resend-verification', { email }),

  // 获取验证码
  getCaptcha: () =>
    request.get<CaptchaResponse>('/auth/captcha'),

  // 验证验证码
  verifyCaptcha: (captchaId: string, captchaCode: string) =>
    request.post('/auth/verify-captcha', {
      captcha_id: captchaId,
      captcha_code: captchaCode
    }),

  // 检查用户名是否可用
  checkUsername: (username: string) =>
    request.get(`/auth/check-username?username=${username}`),

  // 检查邮箱是否可用
  checkEmail: (email: string) =>
    request.get(`/auth/check-email?email=${email}`),

  // 获取当前用户权限
  getUserPermissions: () =>
    request.get('/auth/permissions'),

  // 启用两步验证
  enable2FA: () =>
    request.post('/auth/2fa/enable'),

  // 禁用两步验证
  disable2FA: (code: string) =>
    request.post('/auth/2fa/disable', { code }),

  // 获取两步验证二维码
  get2FAQrCode: () =>
    request.get('/auth/2fa/qrcode'),

  // 验证两步验证
  verify2FA: (code: string) =>
    request.post('/auth/2fa/verify', { code }),

  // 获取登录历史
  getLoginHistory: (params?: { page?: number; per_page?: number }) =>
    request.get('/auth/login-history', { params }),

  // 撤销所有登录会话
  revokeAllSessions: () =>
    request.post('/auth/revoke-all-sessions'),

  // 撤销指定会话
  revokeSession: (sessionId: string) =>
    request.post(`/auth/revoke-session/${sessionId}`),

  // 获取活跃会话
  getActiveSessions: () =>
    request.get('/auth/active-sessions')
}