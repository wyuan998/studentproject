import * as XLSX from 'xlsx'
import { ElMessage } from 'element-plus'

// 导出Excel文件
export const exportToExcel = (data: any[], filename: string, headers?: any[]) => {
  try {
    // 如果提供了表头，使用表头数据
    let exportData = data
    if (headers && headers.length > 0) {
      exportData = data.map(item => {
        const row: any = {}
        headers.forEach(header => {
          row[header.label] = item[header.prop]
        })
        return row
      })
    }

    // 创建工作簿
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(exportData)

    // 设置列宽
    const colWidths = headers ? headers.map(() => ({ wch: 15 })) : []
    ws['!cols'] = colWidths

    XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')

    // 下载文件
    XLSX.writeFile(wb, `${filename}.xlsx`)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 导出学生数据
export const exportStudents = (students: any[]) => {
  const headers = [
    { prop: 'student_id', label: '学号' },
    { prop: 'name', label: '姓名' },
    { prop: 'gender', label: '性别' },
    { prop: 'birth_date', label: '出生日期' },
    { prop: 'phone', label: '电话' },
    { prop: 'email', label: '邮箱' },
    { prop: 'major', label: '专业' },
    { prop: 'class_name', label: '班级' },
    { prop: 'status', label: '状态' },
    { prop: 'enrollment_date', label: '入学时间' },
    { prop: 'address', label: '家庭地址' }
  ]

  exportToExcel(students, '学生信息', headers)
}

// 导出教师数据
export const exportTeachers = (teachers: any[]) => {
  const headers = [
    { prop: 'teacher_id', label: '教师工号' },
    { prop: 'name', label: '姓名' },
    { prop: 'gender', label: '性别' },
    { prop: 'phone', label: '电话' },
    { prop: 'email', label: '邮箱' },
    { prop: 'department', label: '院系' },
    { prop: 'title', label: '职称' },
    { prop: 'status', label: '状态' }
  ]

  exportToExcel(teachers, '教师信息', headers)
}

// 导出课程数据
export const exportCourses = (courses: any[]) => {
  const headers = [
    { prop: 'course_code', label: '课程代码' },
    { prop: 'course_name', label: '课程名称' },
    { prop: 'credits', label: '学分' },
    { prop: 'hours', label: '学时' },
    { prop: 'teacher_name', label: '授课教师' },
    { prop: 'semester', label: '学期' },
    { prop: 'max_students', label: '最大人数' },
    { prop: 'current_students', label: '当前人数' }
  ]

  exportToExcel(courses, '课程信息', headers)
}