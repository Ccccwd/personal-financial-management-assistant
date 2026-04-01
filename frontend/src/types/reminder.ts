import { BaseEntity } from './common'

export type ReminderType = 'daily' | 'budget' | 'recurring' | 'report'

export interface Reminder extends BaseEntity {
  type: ReminderType
  title: string
  content?: string
  remind_time: string
  remind_day?: number | null
  category_id?: number | null
  amount?: number | null
  is_enabled: boolean
  last_reminded_at?: string
}

export interface ReminderCreate {
  type: ReminderType
  title: string
  content?: string
  remind_time: string
  remind_day?: number | null
  category_id?: number | null
  amount?: number | null
  is_enabled?: boolean
}

export interface ReminderUpdate extends Partial<ReminderCreate> {}

export interface ReminderListPayload {
  reminders: Reminder[]
  total: number
}

export interface ReminderStatistics {
  [key: string]: unknown
}
