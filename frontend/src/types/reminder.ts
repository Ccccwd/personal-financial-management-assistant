import { BaseEntity } from './common'

export type ReminderType = 'daily' | 'budget' | 'recurring' | 'report'
export type ReminderFrequency = 'once' | 'daily' | 'weekly' | 'monthly' | 'yearly'

export interface Reminder extends BaseEntity {
  user_id: number
  type: ReminderType
  title: string
  content?: string
  frequency: ReminderFrequency
  trigger_time: string // HH:mm:ss for daily, or full datetime for once
  day_of_week?: number // 1-7
  day_of_month?: number // 1-31
  month_of_year?: number // 1-12
  is_enabled: boolean
  last_triggered_at?: string
  next_trigger_at?: string
}

export interface ReminderCreate {
  type: ReminderType
  title: string
  content?: string
  frequency: ReminderFrequency
  trigger_time: string
  day_of_week?: number
  day_of_month?: number
  month_of_year?: number
  is_enabled?: boolean
}

export interface ReminderUpdate extends Partial<ReminderCreate> {}
