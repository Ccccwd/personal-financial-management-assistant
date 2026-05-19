import request from '@/api/request'
import {
  ImportPreviewResponse,
  ImportLog,
  ImportLogsPayload,
  ImportRequest,
  ImportBase64Request,
  ImportResult,
  ValidateBillResult,
} from '@/types/index'

/**
 * 预览账单文件
 * @param file 文件对象（CSV / XLSX）
 */
export function previewBill(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<ImportPreviewResponse>('/wechat/preview', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/**
 * 导入账单（文件上传）
 * @param data 导入参数（file 必填，account_id / category_id 可选）
 */
export function importBill(data: ImportRequest) {
  const formData = new FormData()
  formData.append('file', data.file)
  if (data.account_id !== undefined) {
    formData.append('account_id', data.account_id.toString())
  }
  if (data.category_id !== undefined) {
    formData.append('category_id', data.category_id.toString())
  }
  return request.post<ImportResult>('/wechat/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    // 账单导入可能包含大量数据，超时时间适当放宽
    timeout: 120_000,
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
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/**
 * 获取导入日志列表
 * @param params 分页参数
 */
export function getImportLogs(params?: { page?: number; page_size?: number }) {
  return request.get<ImportLogsPayload>('/wechat/import-logs', { params })
}

/**
 * 获取导入日志详情
 * @param id 日志 ID
 */
export function getImportLog(id: number) {
  return request.get<ImportLog>(`/wechat/import-logs/${id}`)
}

/**
 * 获取导入日志错误详情
 * @param id 日志 ID
 */
export function getImportLogErrors(id: number) {
  return request.get(`/wechat/import-logs/${id}/errors`)
}
