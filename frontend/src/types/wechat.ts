import { BaseEntity } from './common'

export type ImportStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface WechatBillItem {
  transaction_time: string
  transaction_type: string
  counterparty: string // 交易对方
  product_name: string
  payment_type: string // 收/支
  amount: number
  payment_method: string
  status: string
  transaction_id: string
  merchant_id: string
  remark: string
  // After preview/parsing
  suggested_category_id?: number
  suggested_account_id?: number
  is_duplicate?: boolean
}

export interface ImportPreviewResponse {
  total_count: number
  valid_count: number
  duplicate_count: number
  items: WechatBillItem[]
}

export interface ImportLog extends BaseEntity {
  user_id: number
  filename: string
  status: ImportStatus
  total_rows: number
  success_count: number
  fail_count: number
  error_message?: string
  import_time: string
}

export interface ImportRequest {
  file?: File
  skip_duplicates?: boolean
  ai_classify?: boolean
  default_account_id?: number
}
