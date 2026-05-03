import request from '@/api/request'
import {
  Reminder,
  ReminderCreate,
  ReminderListPayload,
  ReminderStatistics,
  ReminderUpdate,
} from '@/types/index'

/**
 * 获取提醒列表
 * @param params 查询参数
 */
export function getReminders(params?: {
  reminder_type?: string
  is_enabled?: boolean
}) {
  return request.get<ReminderListPayload>('/reminders', { params })
}

/**
 * 获取提醒详情
 * @param id 提醒ID
 */
export function getReminder(id: number) {
  return request.get<Reminder>(`/reminders/${id}`)
}

/**
 * 创建提醒
 * @param data 提醒数据
 */
export function createReminder(data: ReminderCreate) {
  return request.post<Reminder>('/reminders', data)
}

/**
 * 更新提醒
 * @param id 提醒ID
 * @param data 提醒数据
 */
export function updateReminder(id: number, data: ReminderUpdate) {
  return request.put<Reminder>(`/reminders/${id}`, data)
}

/**
 * 删除提醒
 * @param id 提醒ID
 */
export function deleteReminder(id: number) {
  return request.delete(`/reminders/${id}`)
}

/**
 * 切换提醒启用状态
 * @param id 提醒ID
 */
export function toggleReminder(id: number) {
  return request.patch<{ success: boolean; is_enabled: boolean }>(`/reminders/${id}/toggle`)
}

/**
 * 检查今日提醒
 */
export function checkTodayReminders() {
  return request.get<Reminder[]>('/reminders/check-today')
}

/**
 * 获取提醒统计
 */
export function getReminderStatistics() {
  return request.get<ReminderStatistics>('/reminders/statistics')
}
