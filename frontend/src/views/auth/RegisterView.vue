<template>
  <div class="register-container">
    <div class="register-content">
      <div class="register-header">
        <div class="logo-wrapper">
          <el-icon class="logo-icon" :size="48"><Wallet /></el-icon>
        </div>
        <h1 class="app-title">个人记账系统</h1>
        <p class="app-subtitle">开启您的智能财务管理之旅</p>
      </div>
      
      <el-card class="register-card" shadow="hover">
        <h2 class="card-title">用户注册</h2>
        <el-form 
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          class="register-form"
          size="large"
          @keyup.enter="handleRegister"
        >
          <el-form-item prop="username">
            <el-input 
              name="username"
              v-model="registerForm.username" 
              placeholder="请输入用户名" 
              :prefix-icon="User"
              autocomplete="off"
            />
          </el-form-item>

          <el-form-item prop="email">
            <el-input 
              name="email"
              v-model="registerForm.email" 
              placeholder="请输入邮箱" 
              :prefix-icon="Message"
              autocomplete="off"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              name="password"
              v-model="registerForm.password" 
              type="password" 
              placeholder="请输入密码" 
              :prefix-icon="Lock"
              show-password
              autocomplete="new-password"
            />
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input 
              name="confirmPassword"
              v-model="registerForm.confirmPassword" 
              type="password" 
              placeholder="请再次输入密码" 
              :prefix-icon="Lock"
              show-password
              autocomplete="new-password"
            />
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              class="submit-btn" 
              :loading="loading" 
              @click="handleRegister"
            >
              注册
            </el-button>
          </el-form-item>
          
          <div class="login-prompt">
            已有账号？
            <el-link type="primary" @click="goToLogin">立即登录</el-link>
          </div>
        </el-form>
      </el-card>

      <div class="register-footer">
        © 2026 Personal Finance Manager. All rights reserved.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Message, Wallet } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { register as registerApi } from '@/api/auth'

const router = useRouter()
const registerFormRef = ref<FormInstance>()
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePass2 = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const registerRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确格式的邮箱', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validatePass2, trigger: 'blur' }
  ]
})

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await registerApi({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password
        })
        
        ElMessage.success('注册成功，请登录')
        router.push('/login')
      } catch (error: any) {
        console.error('Register error:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #F9FAFB;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-image: radial-gradient(#16A34A 1px, transparent 1px);
  background-size: 40px 40px;
}

.register-content {
  width: 100%;
  max-width: 440px;
  padding: 20px;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-wrapper {
  display: inline-flex;
  padding: 12px;
  background-color: #DCFCE7;
  border-radius: 16px;
  margin-bottom: 16px;
}

.logo-icon {
  color: #16A34A;
}

.app-title {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 800;
  color: #111827;
  letter-spacing: -0.5px;
}

.app-subtitle {
  margin: 0;
  font-size: 14px;
  color: #6B7280;
}

.register-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  overflow: visible;
}

:deep(.el-card__body) {
  padding: 32px;
}

.card-title {
  margin: 0 0 24px;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  text-align: center;
}

.register-form .el-input {
  --el-input-hover-border-color: #16A34A;
  --el-input-focus-border-color: #16A34A;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  font-weight: 600;
  font-size: 16px;
  background-color: #16A34A;
  border-color: #16A34A;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.submit-btn:hover, .submit-btn:focus {
  background-color: #15803D;
  border-color: #15803D;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.3);
}

.submit-btn:active {
  transform: translateY(0);
}

.el-link.el-link--primary {
  --el-link-text-color: #16A34A;
  --el-link-hover-text-color: #15803D;
  font-weight: 500;
}

.login-prompt {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #4B5563;
}

.register-footer {
  margin-top: 40px;
  text-align: center;
  font-size: 12px;
  color: #9CA3AF;
}
</style>
