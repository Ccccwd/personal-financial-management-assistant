/**
 * TransactionCard 组件测试
 * 测试交易卡片的渲染输出与不同交易类型的显示逻辑
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TransactionCard from '@/components/business/TransactionCard.vue'

const baseTransaction = {
  id: 1,
  type: 'expense' as const,
  amount: 100.5,
  category_name: '餐饮',
  category_color: '#FF6B6B',
  account_name: '微信',
  transaction_date: '2026-04-28T12:30:00',
  remark: '午餐',
  merchant_name: '麦当劳',
  source: 'manual' as const,
  created_at: '2026-04-28T12:30:00',
  updated_at: '2026-04-28T12:30:00'
}

describe('TransactionCard 组件', () => {
  it('1. 正确渲染支出类型交易的金额（带负号）', () => {
    const wrapper = mount(TransactionCard, {
      props: { transaction: { ...baseTransaction, type: 'expense', amount: 100.5 } }
    })
    expect(wrapper.text()).toContain('-100.50')
  })

  it('2. 正确渲染收入类型交易的金额（带正号）', () => {
    const wrapper = mount(TransactionCard, {
      props: { transaction: { ...baseTransaction, type: 'income', amount: 5000 } }
    })
    expect(wrapper.text()).toContain('+5000.00')
  })

  it('3. 转账类型交易不显示正负符号', () => {
    const wrapper = mount(TransactionCard, {
      props: { transaction: { ...baseTransaction, type: 'transfer', amount: 200 } }
    })
    const amountEl = wrapper.find('.item-amount')
    expect(amountEl.text()).toBe('200.00')
    expect(amountEl.text()).not.toContain('+')
    expect(amountEl.text()).not.toContain('-')
  })

  it('4. 显示商户名（当 merchant_name 存在时优先显示）', () => {
    const wrapper = mount(TransactionCard, {
      props: { transaction: { ...baseTransaction, merchant_name: '麦当劳' } }
    })
    expect(wrapper.find('.item-title').text()).toBe('麦当劳')
  })

  it('5. 无商户名时显示分类名', () => {
    const wrapper = mount(TransactionCard, {
      props: {
        transaction: {
          ...baseTransaction,
          merchant_name: undefined,
          category_name: '餐饮'
        }
      }
    })
    expect(wrapper.find('.item-title').text()).toBe('餐饮')
  })

  it('6. 无任何名称时显示"未分类"', () => {
    const wrapper = mount(TransactionCard, {
      props: {
        transaction: {
          ...baseTransaction,
          merchant_name: undefined,
          category_name: undefined
        }
      }
    })
    expect(wrapper.find('.item-title').text()).toBe('未分类')
  })

  it('7. 分类图标显示首字母（大写）', () => {
    const wrapper = mount(TransactionCard, {
      props: { transaction: { ...baseTransaction, category_name: '餐饮' } }
    })
    expect(wrapper.find('.icon-text').text()).toBe('餐')
  })

  it('8. 备注超过10个字符时显示省略号', () => {
    const longRemark = '这是一段超过十个字符的备注内容'
    const wrapper = mount(TransactionCard, {
      props: {
        transaction: { ...baseTransaction, remark: longRemark }
      }
    })
    const remarkEl = wrapper.find('.remark')
    expect(remarkEl.text()).toContain('...')
    expect(remarkEl.text().length).toBeLessThanOrEqual(13)
  })

  it('9. 有备注时显示分隔符', () => {
    const wrapper = mount(TransactionCard, {
      props: { transaction: { ...baseTransaction, remark: '午餐' } }
    })
    expect(wrapper.find('.divider').exists()).toBe(true)
  })

  it('10. 无备注时不显示分隔符', () => {
    const wrapper = mount(TransactionCard, {
      props: { transaction: { ...baseTransaction, remark: undefined } }
    })
    expect(wrapper.find('.divider').exists()).toBe(false)
  })

  it('11. 支出金额应用正确的CSS类名（is-expense）', () => {
    const wrapper = mount(TransactionCard, {
      props: { transaction: { ...baseTransaction, type: 'expense' } }
    })
    expect(wrapper.find('.item-amount').classes()).toContain('is-expense')
  })

  it('12. 收入金额应用正确的CSS类名（is-income）', () => {
    const wrapper = mount(TransactionCard, {
      props: { transaction: { ...baseTransaction, type: 'income' } }
    })
    expect(wrapper.find('.item-amount').classes()).toContain('is-income')
  })
})
