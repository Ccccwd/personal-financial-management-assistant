import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { TokenManager } from '@/utils/auth'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/home/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'transactions',
        name: 'Transactions',
        component: () => import('@/views/transaction/TransactionList.vue'),
        meta: { title: '交易记录' }
      },
      {
        path: 'transactions/add',
        name: 'TransactionAdd',
        component: () => import('@/views/transaction/TransactionAdd.vue'),
        meta: { title: '新增交易' }
      },
      {
        path: 'accounts',
        name: 'Accounts',
        component: () => import('@/views/account/AccountList.vue'),
        meta: { title: '账户管理' }
      },
      {
        path: 'budgets',
        name: 'Budgets',
        component: () => import('@/views/budget/BudgetList.vue'),
        meta: { title: '预算管理' }
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/statistics/Statistics.vue'),
        meta: { title: '统计分析' }
      },
      {
        path: 'import',
        name: 'Import',
        component: () => import('@/views/import/ImportData.vue'),
        meta: { title: '数据导入' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/Profile.vue'),
        meta: { title: '个人设置' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { guest: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/auth/ForgotPassword.vue'),
    meta: { guest: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Route Guard
router.beforeEach((to, from, next) => {
  const token = TokenManager.getAccessToken()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isGuestRoute = to.matched.some(record => record.meta.guest)

  if (requiresAuth && !token) {
    next('/login')
  } else if (isGuestRoute && token) {
    next('/')
  } else {
    next()
  }
})

export default router
