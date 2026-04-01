import { BaseEntity } from './common'

export type ImportStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface WechatBillItem {
  transaction_date: string
  merchant_name: string
  product_name: string
  income_expense: string
  amount: number
  payment_method: string
  wechat_transaction_id: string
}

export interface ImportPreviewSummary {
  total_records: number
  income_count: number
  expense_count: number
  total_income: number
  total_expense: number
  start_date: string
  end_date: string
  potential_duplicates: number
}

export interface ImportPreviewResponse {
  valid: boolean
  detected_format: string
  filename: string
  file_size: number
  summary: ImportPreviewSummary
  preview_data: WechatBillItem[]
}

export interface ImportLog extends BaseEntity {
  source: string
  success_count: number
  duplicate_count: number
  fail_count: number
  ai_classified_count: number
  total_count: number
  import_time: string
}

export interface ImportRequest {
  file?: File
  skip_duplicates?: boolean
  ai_classify?: boolean
  default_account_id?: number
}

export interface ImportBase64Request {
  file_content: string
  filename: string
  skip_duplicates?: boolean
  ai_classify?: boolean
  default_account_id?: number | null
}

export interface ImportResult {
  import_log_id: number
  success_count: number
  fail_count: number
  duplicate_count: number
  ai_classified_count: number
  total_count: number
}

export interface ValidateBillResult {
  valid: boolean
  detected_format: string
  message: string
}

export interface ImportLogsPayload {
  logs: ImportLog[]
  total: number
}
