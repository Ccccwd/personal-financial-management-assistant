<template>
  <div class="forgot-container">
    <div class="forgot-content">
      <div class="forgot-header">
        <div class="logo-wrapper">
          <el-icon class="logo-icon" :size="48"><Wallet /></el-icon>
        </div>
        <h1 class="app-title">个人记账系统</h1>
        <p class="app-subtitle">找回您的账户密码</p>
      </div>

      <el-card class="forgot-card" shadow="hover">
        <h2 class="card-title">忘记密码</h2>

        <!-- 步骤一：输入邮箱 -->
        <div v-if="step === 1">
          <p class="step-desc">请输入注册时使用的邮箱地址，我们将发送密码重置链接。</p>
          <el-form
            ref="emailFormRef"
            :model="emailForm"
            :rules="emailRules"
            class="forgot-form"
            size="large"
            @keyup.enter="handleSendEmail"
          >
            <el-form-item prop="email">
              <el-input
                v-model="emailForm.email"
                placeholder="请输入注册邮箱"
                :prefix-icon="Message"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                class="submit-btn"
                :loading="loading"
                @click="handleSendEmail"
              >
                发送重置链接
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤二：发送成功提示 -->
        <div v-else-if="step === 2" class="success-step">
          <el-icon class="success-icon" :size="64"><CircleCheck /></el-icon>
          <p class="success-text">重置链接已发送</p>
          <p class="success-desc">
            我们已向 <strong>{{ emailForm.email }}</strong> 发送了密码重置邮件，请查收并按照邮件中的指引操作。
          </p>
          <el-button type="primary" class="submit-btn" @click="handleResend" :loading="loading" :disabled="countdown > 0">
            {{ countdown > 0 ? `重新发送 (${countdown}s)` : '重新发送' }}
          </el-button>
        </div>

        <div class="back-prompt">
          <el-link type="primary" underline="never" @click="goToLogin">
            <el-icon><ArrowLeft /></el-icon> 返回登录
          </el-link>
        </div>
      </el-card>

      <div class="forgot-footer">
        © 2026 Personal Finance Manager. All rights reserved.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message, Wallet, CircleCheck, ArrowLeft } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { requestPasswordReset } from '@/api/auth'

const router = useRouter()
const emailFormRef = ref<FormInstance>()
const loading = ref(false)
const step = ref(1)
const countdown = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

const emailForm = reactive({
  email: ''
})

const emailRules = reactive<FormRules>({
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
})

const startCountdown = () => {
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0 && timer) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

const handleSendEmail = async () => {
  if (!emailFormRef.value) return
  await emailFormRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await requestPasswordReset(emailForm.email)
      step.value = 2
      startCountdown()
      ElMessage.success('重置链接已发送，请查收邮箱')
    } catch (error) {
      ElMessage.error('发送失败，请检查邮箱是否正确')
    } finally {
      loading.value = false
    }
  })
}

const handleResend = async () => {
  loading.value = true
  try {
    await requestPasswordReset(emailForm.email)
    startCountdown()
    ElMessage.success('重置链接已重新发送')
  } catch (error) {
    ElMessage.error('发送失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
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

.forgot-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #F9FAFB; /* --color-bg */
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-image: radial-gradient(#16A34A 1px, transparent 1px); /* Subtle pattern using primary color */
  background-size: 40px 40px;
}

.forgot-content {
  width: 100%;
  max-width: 440px;
  padding: 20px;
}

.forgot-header {
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

.forgot-card {
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

.step-desc {
  font-size: 14px;
  color: #4B5563; /* --color-text-secondary */
  margin-bottom: 24px;
  line-height: 1.6;
  text-align: center;
}

.forgot-form .el-input {
  --el-input-hover-border-color: #16A34A;
  --el-input-focus-border-color: #16A34A;
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

.success-step {
  padding: 10px 0;
  text-align: center;
}

.success-icon {
  color: #22C55E; /* --color-success */
  margin-bottom: 16px;
}

.success-text {
  font-size: 20px;
  font-weight: 600;
  color: #111827; /* --color-text-primary */
  margin: 0 0 12px;
}

.success-desc {
  font-size: 14px;
  color: #4B5563; /* --color-text-secondary */
  line-height: 1.6;
  margin-bottom: 24px;
}

.back-prompt {
  margin-top: 24px;
  text-align: center;
}

.forgot-footer {
  margin-top: 40px;
  text-align: center;
  font-size: 12px;
  color: #9CA3AF;
}
</style>
