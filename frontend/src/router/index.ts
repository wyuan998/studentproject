import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import nprogress from 'nprogress'
import 'nprogress/nprogress.css'

// 进度条配置
nprogress.configure({ showSpinner: false })

// 扩展路由元数据类型
declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    icon?: string
    hidden?: boolean
    roles?: string[]
    requiresAuth?: boolean
    keepAlive?: boolean
    showLayout?: boolean
    affix?: boolean
    noCache?: boolean
    activeMenu?: string
    breadcrumbs?: Array<{ title: string; path?: string }>
  }
}

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
      showLayout: false
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: {
      title: '注册',
      requiresAuth: false,
      showLayout: false
    }
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '页面不存在',
      requiresAuth: false,
      showLayout: false
    }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: {
      title: '无权限访问',
      requiresAuth: false,
      showLayout: false
    }
  },
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          title: '仪表板',
          icon: 'Dashboard',
          affix: true,
          breadcrumbs: []
        }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/user/Profile.vue'),
        meta: {
          title: '个人资料',
          icon: 'User',
          breadcrumbs: []
        }
      },
      // 学生模块
      {
        path: '/students',
        name: 'Students',
        redirect: '/students/list',
        meta: {
          title: '学生管理',
          icon: 'User'
        },
        children: [
          {
            path: '/students/list',
            name: 'StudentList',
            component: () => import('@/views/student/StudentList.vue'),
            meta: {
              title: '学生列表',
              icon: 'List',
              keepAlive: true,
              breadcrumbs: [{ title: '学生管理' }, { title: '学生列表' }]
            }
          },
          {
            path: '/students/detail/:id',
            name: 'StudentDetail',
            component: () => import('@/views/student/StudentDetail.vue'),
            meta: {
              title: '学生详情',
              icon: 'UserFilled',
              breadcrumbs: [{ title: '学生管理' }, { title: '学生详情' }]
            }
          },
          {
            path: '/students/create',
            name: 'StudentCreate',
            component: () => import('@/views/student/StudentCreate.vue'),
            meta: {
              title: '添加学生',
              icon: 'Plus',
              breadcrumbs: [{ title: '学生管理' }, { title: '添加学生' }]
            }
          },
          {
            path: '/students/edit/:id',
            name: 'StudentEdit',
            component: () => import('@/views/student/StudentCreate.vue'),
            meta: {
              title: '编辑学生',
              icon: 'Edit',
              breadcrumbs: [{ title: '学生管理' }, { title: '编辑学生' }],
              hidden: true
            }
          }
        ]
      },
      // 教师模块
      {
        path: '/teachers',
        name: 'Teachers',
        redirect: '/teachers/list',
        meta: {
          title: '教师管理',
          icon: 'Avatar'
        },
        children: [
          {
            path: '/teachers/list',
            name: 'TeacherList',
            component: () => import('@/views/teacher/TeacherList.vue'),
            meta: {
              title: '教师列表',
              icon: 'List',
              keepAlive: true,
              breadcrumbs: [{ title: '教师管理' }, { title: '教师列表' }]
            }
          },
          {
            path: '/teachers/detail/:id',
            name: 'TeacherDetail',
            component: () => import('@/views/teacher/TeacherDetail.vue'),
            meta: {
              title: '教师详情',
              icon: 'Avatar',
              breadcrumbs: [{ title: '教师管理' }, { title: '教师详情' }]
            }
          },
          {
            path: '/teachers/create',
            name: 'TeacherCreate',
            component: () => import('@/views/teacher/TeacherCreate.vue'),
            meta: {
              title: '添加教师',
              icon: 'Plus',
              breadcrumbs: [{ title: '教师管理' }, { title: '添加教师' }]
            }
          },
          {
            path: '/teachers/courses/:id',
            name: 'TeacherCourses',
            component: () => import('@/views/teacher/TeacherCourses.vue'),
            meta: {
              title: '教师课程',
              icon: 'Reading',
              breadcrumbs: [{ title: '教师管理' }, { title: '教师课程' }],
              hidden: true
            }
          }
        ]
      },
      // 课程模块
      {
        path: '/courses',
        name: 'Courses',
        redirect: '/courses/list',
        meta: {
          title: '课程管理',
          icon: 'Reading'
        },
        children: [
          {
            path: '/courses/list',
            name: 'CourseList',
            component: () => import('@/views/course/CourseList.vue'),
            meta: {
              title: '课程列表',
              icon: 'List',
              keepAlive: true,
              breadcrumbs: [{ title: '课程管理' }, { title: '课程列表' }]
            }
          },
          {
            path: '/courses/detail/:id',
            name: 'CourseDetail',
            component: () => import('@/views/course/CourseDetail.vue'),
            meta: {
              title: '课程详情',
              icon: 'Document',
              breadcrumbs: [{ title: '课程管理' }, { title: '课程详情' }]
            }
          },
          {
            path: '/courses/create',
            name: 'CourseCreate',
            component: () => import('@/views/course/CourseCreate.vue'),
            meta: {
              title: '创建课程',
              icon: 'Plus',
              breadcrumbs: [{ title: '课程管理' }, { title: '创建课程' }]
            }
          }
        ]
      },
      // 选课模块
      {
        path: '/enrollments',
        name: 'Enrollments',
        redirect: '/enrollments/list',
        meta: {
          title: '选课管理',
          icon: 'Tickets'
        },
        children: [
          {
            path: '/enrollments/list',
            name: 'EnrollmentList',
            component: () => import('@/views/enrollment/EnrollmentList.vue'),
            meta: {
              title: '选课列表',
              icon: 'List',
              keepAlive: true,
              breadcrumbs: [{ title: '选课管理' }, { title: '选课列表' }]
            }
          },
          {
            path: '/enrollments/approval',
            name: 'EnrollmentApproval',
            component: () => import('@/views/enrollment/EnrollmentApproval.vue'),
            meta: {
              title: '选课审核',
              icon: 'Check',
              roles: ['admin', 'teacher'],
              breadcrumbs: [{ title: '选课管理' }, { title: '选课审核' }]
            }
          },
          {
            path: '/enrollments/create',
            name: 'EnrollmentCreate',
            component: () => import('@/views/enrollment/EnrollmentCreate.vue'),
            meta: {
              title: '学生选课',
              icon: 'Plus',
              breadcrumbs: [{ title: '选课管理' }, { title: '学生选课' }]
            }
          }
        ]
      },
      // 成绩模块
      {
        path: '/grades',
        name: 'Grades',
        redirect: '/grades/list',
        meta: {
          title: '成绩管理',
          icon: 'DocumentChecked'
        },
        children: [
          {
            path: '/grades/list',
            name: 'GradeList',
            component: () => import('@/views/GradeManagement.vue'),
            meta: {
              title: '成绩列表',
              icon: 'List',
              keepAlive: true,
              breadcrumbs: [{ title: '成绩管理' }, { title: '成绩列表' }]
            }
          },
          {
            path: '/grades/entry',
            name: 'GradeEntry',
            component: () => import('@/views/grade/GradeEntry.vue'),
            meta: {
              title: '成绩录入',
              icon: 'EditPen',
              roles: ['admin', 'teacher'],
              breadcrumbs: [{ title: '成绩管理' }, { title: '成绩录入' }]
            }
          },
          {
            path: '/grades/statistics',
            name: 'GradeStatistics',
            component: () => import('@/views/grade/GradeStatistics.vue'),
            meta: {
              title: '成绩统计',
              icon: 'PieChart',
              roles: ['admin', 'teacher'],
              breadcrumbs: [{ title: '成绩管理' }, { title: '成绩统计' }]
            }
          }
        ]
      },
      // 报表模块
      {
        path: '/reports',
        name: 'Reports',
        redirect: '/reports/dashboard',
        meta: {
          title: '报表统计',
          icon: 'DataAnalysis',
          roles: ['admin']
        },
        children: [
          {
            path: '/reports/dashboard',
            name: 'ReportsDashboard',
            component: () => import('@/views/reports/Dashboard.vue'),
            meta: {
              title: '报表中心',
              icon: 'DataBoard',
              roles: ['admin'],
              breadcrumbs: [{ title: '报表统计' }, { title: '报表中心' }]
            }
          },
          {
            path: '/reports/student',
            name: 'StudentReports',
            component: () => import('@/views/reports/StudentReports.vue'),
            meta: {
              title: '学生报表',
              icon: 'Avatar',
              roles: ['admin'],
              breadcrumbs: [{ title: '报表统计' }, { title: '学生报表' }]
            }
          },
          {
            path: '/reports/teacher',
            name: 'TeacherReports',
            component: () => import('@/views/reports/TeacherReports.vue'),
            meta: {
              title: '教师报表',
              icon: 'Avatar',
              roles: ['admin'],
              breadcrumbs: [{ title: '报表统计' }, { title: '教师报表' }]
            }
          },
          {
            path: '/reports/grade',
            name: 'GradeReports',
            component: () => import('@/views/reports/GradeReports.vue'),
            meta: {
              title: '成绩报表',
              icon: 'DocumentChecked',
              roles: ['admin'],
              breadcrumbs: [{ title: '报表统计' }, { title: '成绩报表' }]
            }
          },
          {
            path: '/reports/enrollment',
            name: 'EnrollmentReports',
            component: () => import('@/views/reports/EnrollmentReports.vue'),
            meta: {
              title: '选课报表',
              icon: 'Tickets',
              roles: ['admin'],
              breadcrumbs: [{ title: '报表统计' }, { title: '选课报表' }]
            }
          }
        ]
      },
      // 消息模块
      {
        path: '/messages',
        name: 'Messages',
        redirect: '/messages/list',
        meta: {
          title: '消息通知',
          icon: 'Bell'
        },
        children: [
          {
            path: '/messages/list',
            name: 'MessageList',
            component: () => import('@/views/message/MessageList.vue'),
            meta: {
              title: '消息列表',
              icon: 'List',
              breadcrumbs: [{ title: '消息通知' }, { title: '消息列表' }]
            }
          },
          {
            path: '/messages/create',
            name: 'MessageCreate',
            component: () => import('@/views/message/MessageCreate.vue'),
            meta: {
              title: '发送消息',
              icon: 'Plus',
              breadcrumbs: [{ title: '消息通知' }, { title: '发送消息' }]
            }
          },
          {
            path: '/templates',
            name: 'MessageTemplates',
            component: () => import('@/views/message/MessageTemplates.vue'),
            meta: {
              title: '消息模板',
              icon: 'Document',
              roles: ['admin'],
              breadcrumbs: [{ title: '消息通知' }, { title: '消息模板' }]
            }
          }
        ]
      },
      // 系统管理模块
      {
        path: '/admin',
        name: 'Admin',
        redirect: '/admin/dashboard',
        meta: {
          title: '系统管理',
          icon: 'Setting',
          roles: ['admin']
        },
        children: [
          {
            path: '/admin/dashboard',
            name: 'AdminDashboard',
            component: () => import('@/views/admin/Dashboard.vue'),
            meta: {
              title: '系统控制台',
              icon: 'Monitor',
              roles: ['admin'],
              breadcrumbs: [{ title: '系统管理' }, { title: '控制台' }]
            }
          },
          {
            path: '/admin/users',
            name: 'AdminUsers',
            component: () => import('@/views/admin/UserManagement.vue'),
            meta: {
              title: '用户管理',
              icon: 'User',
              roles: ['admin'],
              breadcrumbs: [{ title: '系统管理' }, { title: '用户管理' }]
            }
          },
          {
            path: '/admin/permissions',
            name: 'AdminPermissions',
            component: () => import('@/views/admin/PermissionManagement.vue'),
            meta: {
              title: '权限管理',
              icon: 'Key',
              roles: ['admin'],
              breadcrumbs: [{ title: '系统管理' }, { title: '权限管理' }]
            }
          },
          {
            path: '/admin/logs',
            name: 'AdminLogs',
            component: () => import('@/views/admin/SystemLogs.vue'),
            meta: {
              title: '系统日志',
              icon: 'Document',
              roles: ['admin'],
              breadcrumbs: [{ title: '系统管理' }, { title: '系统日志' }]
            }
          },
          {
            path: '/admin/settings',
            name: 'AdminSettings',
            component: () => import('@/views/admin/SystemSettings.vue'),
            meta: {
              title: '系统设置',
              icon: 'Setting',
              roles: ['admin'],
              breadcrumbs: [{ title: '系统管理' }, { title: '系统设置' }]
            }
          },
          {
            path: '/admin/backup',
            name: 'AdminBackup',
            component: () => import('@/views/admin/DataBackup.vue'),
            meta: {
              title: '数据备份',
              icon: 'Download',
              roles: ['admin'],
              breadcrumbs: [{ title: '系统管理' }, { title: '数据备份' }]
            }
          }
        ]
      }
    ]
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return {
        el: document.querySelector(to.hash) as HTMLElement
      }
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 开始进度条
  nprogress.start()

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 学生信息管理系统`
  }

  next()
})

router.afterEach(() => {
  // 结束进度条
  nprogress.done()
})

// 错误处理
router.onError((error) => {
  console.error('Router Error:', error)
  nprogress.done()
})

export default router