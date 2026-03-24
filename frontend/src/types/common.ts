export interface APIResponse<T = any> {
  code: number
  message: string
  data?: T
  success: boolean
}

export interface PaginationInfo {
  page: number
  pageSize: number
  total: number
  totalPages: number
}

export interface PaginatedResponse<T = any> extends APIResponse<T[]> {
  pagination: PaginationInfo
}

export interface ErrorResponse extends APIResponse {
  success: false
  error?: {
    field?: string
    message?: string
    type?: string
  }[]
}

export interface BaseEntity {
  id: number
  created_at: string
  updated_at?: string
}
