import request from '@/api/request'
import {
  ImportPreviewResponse,
  ImportLog,
  ImportLogsPayload,
  ImportRequest,
  ImportBase64Request,
  ImportResult,
  ValidateBillResult
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

  return request.post<ImportResult>('/wechat/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导入账单（Base64 编码）
 * @param data 导入数据
 */
export function importBillBase64(data: ImportBase64Request) {
  return request.post<ImportResult>('/wechat/import-base64', data)
}

/**
 * 验证文件格式
 * @param file 文件对象
 */
export function validateBillFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request.post<ValidateBillResult>('/wechat/validate', formData, {
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
  return request.get<ImportLogsPayload>('/wechat/import-logs', { params })
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
