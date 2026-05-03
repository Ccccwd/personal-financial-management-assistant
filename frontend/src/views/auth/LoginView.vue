<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <div class="logo-wrapper">
          <el-icon class="logo-icon" :size="48"><Wallet /></el-icon>
        </div>
        <h1 class="app-title">个人记账系统</h1>
        <p class="app-subtitle">智能财务助手，轻松管理您的每一笔收支</p>
      </div>
      
      <el-card class="login-card" shadow="hover">
        <h2 class="card-title">欢迎登录</h2>
        <el-form 
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          size="large"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input 
              name="username"
              v-model="loginForm.username" 
              placeholder="请输入用户名" 
              :prefix-icon="User"
              autocomplete="off"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              name="password"
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码" 
              :prefix-icon="Lock"
              show-password
              autocomplete="new-password"
            />
          </el-form-item>
          
          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <el-link type="primary" underline="never" @click="router.push('/forgot-password')">忘记密码？</el-link>
          </div>

          <el-form-item>
            <el-button 
              type="primary" 
              class="submit-btn" 
              :loading="loading" 
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
          
          <div class="register-prompt">
            还没有账号？
            <el-link type="primary" @click="goToRegister">立即注册</el-link>
          </div>
        </el-form>
      </el-card>

      <div class="login-footer">
        © 2026 Personal Finance Manager. All rights reserved.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { User, Lock, Wallet } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref<FormInstance>()
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' }
  ]
})

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const success = await userStore.login({
          username: loginForm.username,
          password: loginForm.password
        })
        
        if (success) {
          ElMessage.success('登录成功')
          router.push('/')
        } else {
          // ElMessage.error('登录失败，请检查用户名或密码')
        }
      } catch (error: any) {
        // request.ts 拦截器已经处理了大部分错误提示
        console.error('Login error:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
/* Design Spec Colors */
:root {
  --color-primary: #16A34A;
  --color-primary-hover: #15803D;
  --color-bg: #F9FAFB;
  --color-text-primary: #111827;
  --color-text-secondary: #4B5563;
}

.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #F9FAFB; /* --color-bg */
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-image: radial-gradient(#16A34A 1px, transparent 1px); /* Subtle pattern using primary color */
  background-size: 40px 40px;
}

.login-content {
  width: 100%;
  max-width: 440px;
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-wrapper {
  display: inline-flex;
  padding: 12px;
  background-color: #DCFCE7; /* Light green background for logo */
  border-radius: 16px;
  margin-bottom: 16px;
}

.logo-icon {
  color: #16A34A; /* --color-primary */
}

.app-title {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 800;
  color: #111827; /* --color-text-primary */
  letter-spacing: -0.5px;
}

.app-subtitle {
  margin: 0;
  font-size: 14px;
  color: #6B7280; /* lighter secondary text */
}

.login-card {
  border-radius: 16px; /* Smooth corners */
  border: none;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); /* Soft shadow */
  overflow: visible;
}

/* Override Element Plus Card Body Padding */
:deep(.el-card__body) {
  padding: 32px;
}

.card-title {
  margin: 0 0 24px;
  font-size: 20px;
  font-weight: 600;
  color: #111827; /* --color-text-primary */
  text-align: center;
}

.login-form .el-input {
  --el-input-hover-border-color: #16A34A;
  --el-input-focus-border-color: #16A34A;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

/* Primary Button Styling */
.submit-btn {
  width: 100%;
  padding: 12px;
  font-weight: 600;
  font-size: 16px;
  background-color: #16A34A; /* --color-primary */
  border-color: #16A34A;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.submit-btn:hover, .submit-btn:focus {
  background-color: #15803D; /* --color-primary-hover */
  border-color: #15803D;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.3);
}

.submit-btn:active {
  transform: translateY(0);
}

/* Link Styling */
.el-link.el-link--primary {
  --el-link-text-color: #16A34A;
  --el-link-hover-text-color: #15803D;
  font-weight: 500;
}

.el-checkbox {
  --el-checkbox-checked-bg-color: #16A34A;
  --el-checkbox-checked-input-border-color: #16A34A;
  --el-checkbox-input-border-color-hover: #16A34A;
}

.register-prompt {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #4B5563;
}

.login-footer {
  margin-top: 40px;
  text-align: center;
  font-size: 12px;
  color: #9CA3AF;
}
</style>
