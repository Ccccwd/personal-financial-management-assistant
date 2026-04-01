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
          <p class="step-desc">请输入您注册时使用的邮箱地址，我们将发送密码重置链接。</p>
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
          <el-button type="primary" @click="handleResend" :loading="loading" :disabled="countdown > 0">
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
.forgot-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.forgot-content {
  width: 100%;
  max-width: 460px;
  text-align: center;
}

.forgot-header {
  margin-bottom: 30px;
  color: #fff;
}

.logo-wrapper {
  margin-bottom: 16px;
}

.logo-icon {
  color: #fff;
}

.app-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px;
}

.app-subtitle {
  font-size: 14px;
  opacity: 0.85;
  margin: 0;
}

.forgot-card {
  border-radius: 12px;
  padding: 10px 20px;
}

.card-title {
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 20px;
  color: #303133;
}

.step-desc {
  font-size: 14px;
  color: #606266;
  margin-bottom: 24px;
  line-height: 1.6;
}

.forgot-form .submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 8px;
}

.success-step {
  padding: 20px 0;
}

.success-icon {
  color: #67c23a;
}

.success-text {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 16px 0 8px;
}

.success-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 24px;
}

.back-prompt {
  margin-top: 24px;
  text-align: center;
}

.forgot-footer {
  margin-top: 30px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}
</style>
