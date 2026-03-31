import request from '@/utils/request'
import {
  ImportPreviewResponse,
  ImportLog,
  ImportRequest,
  PaginatedResponse,
  APIResponse
} from '@/types/index'

/**
 * 预览账单文件
 * @param file 文件对象
 * @param limit 预览条数
 */
export function previewBill(file: File, limit: number = 10) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('limit', limit.toString())

  return request.post<ImportPreviewResponse>('/wechat/preview', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导入账单（文件上传）
 * @param data 导入参数
 */
export function importBill(data: ImportRequest) {
  const formData = new FormData()
  if (data.file) {
    formData.append('file', data.file)
  }
  if (data.skip_duplicates !== undefined) {
    formData.append('skip_duplicates', data.skip_duplicates.toString())
  }
  if (data.ai_classify !== undefined) {
    formData.append('ai_classify', data.ai_classify.toString())
  }
  if (data.default_account_id !== undefined) {
    formData.append('default_account_id', data.default_account_id.toString())
  }

  return request.post<{
    import_log_id: number
    total_count: number
    success_count: number
    fail_count: number
    ai_classified_count: number
  }>('/wechat/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导入账单（Base64 编码）
 * @param data 导入数据
 */
export function importBillBase64(data: {
  file_content: string
  skip_duplicates?: boolean
  ai_classify?: boolean
  default_account_id?: number
}) {
  return request.post<{
    import_log_id: number
    total_count: number
    success_count: number
    fail_count: number
    ai_classified_count: number
  }>('/wechat/import-base64', data)
}

/**
 * 验证文件格式
 * @param file 文件对象
 */
export function validateBillFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request.post<{
    is_valid: boolean
    message: string
    file_type?: string
  }>('/wechat/validate', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取导入日志列表
 * @param params 查询参数
 */
export function getImportLogs(params?: {
  page?: number
  page_size?: number
}) {
  return request.get<PaginatedResponse<ImportLog>>('/wechat/import-logs', { params })
}

/**
 * 获取导入日志详情
 * @param id 日志ID
 */
export function getImportLog(id: number) {
  return request.get<ImportLog>(`/wechat/import-logs/${id}`)
}

/**
 * 下载错误详情
 * @param id 日志ID
 */
export function downloadImportErrors(id: number) {
  return request.get(`/wechat/import-logs/${id}/errors`, {
    responseType: 'blob'
  })
}
