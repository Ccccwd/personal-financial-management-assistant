/** 微信账单导入相关类型定义（与后端 wechat_bill.py 保持一致） */

export type ImportStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'partial'

/** 预览列表中的单条账单项（对应后端 _parse_transaction_row 返回结构） */
export interface WechatBillItem {
  transaction_time: string       // ISO 格式日期时间，如 "2026-03-31T18:30:00"
  transaction_type: 'income' | 'expense'
  counterparty: string           // 交易对方
  description: string            // 商品说明
  payment_method: string         // 支付方式
  amount: number                 // 正数金额
  transaction_id: string
  merchant_order_id?: string
  remark?: string
  is_potential_duplicate: boolean
}

/** 预览接口响应（对应后端 ImportPreview schema，exclude all_transactions） */
export interface ImportPreviewResponse {
  filename: string
  total_records: number
  preview_data: WechatBillItem[]
  detected_format: string
  potential_duplicates: number
  income_count: number
  expense_count: number
  date_range: { start_date: string; end_date: string } | null
}

/** 导入接口响应（对应后端 import_transactions 返回值） */
export interface ImportResult {
  import_log_id: number
  success_count: number
  failed_count: number
  skipped_count: number
  total: number
}

/** 导入日志列表单条记录（对应后端 get_import_logs 返回项） */
export interface ImportLog {
  id: number
  source: string
  file_name: string | null
  status: ImportStatus
  total_records: number
  success_records: number
  failed_records: number
  skipped_records: number
  import_summary: string | null
  created_at: string
}

/** 导入日志列表响应 */
export interface ImportLogsPayload {
  logs: ImportLog[]
  total: number
  page: number
  page_size: number
}

/** 文件验证响应（对应后端 ValidateResponse schema） */
export interface ValidateBillResult {
  is_valid: boolean
  message: string
  file_info?: {
    total_records: number
    file_size: number
  } | null
}

/** 发起导入请求的参数 */
export interface ImportRequest {
  file: File
  account_id?: number
  category_id?: number
}

/** Base64 导入请求体 */
export interface ImportBase64Request {
  content: string               // base64 编码后的文件内容
  filename: string
  account_id?: number | null
  category_id?: number | null
}
