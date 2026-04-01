export interface APIResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface ErrorItem {
  field?: string
  message?: string
  type?: string
}

export interface ErrorResponse {
  code: number
  message: string
  data: null
  error?: ErrorItem[]
}

export interface BaseEntity {
  id: number
  created_at: string
  updated_at?: string
}
