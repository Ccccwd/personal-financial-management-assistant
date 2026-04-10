<template>
  <div class="settings-container">
    <div class="page-header">
      <h2>个人设置</h2>
    </div>

    <el-row :gutter="20">
      <el-col :span="16" :xs="24">
        <!-- 基本信息 -->
        <el-card shadow="hover" class="settings-card">
          <template #header>
            <span class="card-title">基本信息</span>
          </template>
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
            size="large"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input :model-value="userStore.user?.email" disabled />
            </el-form-item>
            <el-form-item label="头像">
              <el-avatar :size="64" :src="userStore.user?.avatar || defaultAvatar" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="handleSaveProfile">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 修改密码 -->
        <el-card shadow="hover" class="settings-card" style="margin-top: 20px">
          <template #header>
            <span class="card-title">修改密码</span>
          </template>
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
            size="large"
          >
            <el-form-item label="当前密码" prop="old_password">
              <el-input
                v-model="passwordForm.old_password"
                type="password"
                show-password
                placeholder="请输入当前密码"
              />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                show-password
                placeholder="请输入新密码"
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                show-password
                placeholder="请再次输入新密码"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" :loading="changingPassword" @click="handleChangePassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="8" :xs="24">
        <!-- 账户信息 -->
        <el-card shadow="hover" class="settings-card">
          <template #header>
            <span class="card-title">账户信息</span>
          </template>
          <div class="account-info">
            <div class="info-item">
              <span class="label">用户ID</span>
              <span class="value">{{ userStore.user?.id }}</span>
            </div>
            <div class="info-item">
              <span class="label">注册时间</span>
              <span class="value">{{ formatDate(userStore.user?.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="label">账户状态</span>
              <el-tag :type="userStore.user?.is_active ? 'success' : 'danger'">
                {{ userStore.user?.is_active ? '正常' : '已禁用' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { updateCurrentUser, changePassword } from '@/api/auth'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import dayjs from 'dayjs'

const userStore = useUserStore()
const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()
const saving = ref(false)
const changingPassword = ref(false)
const defaultAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'

const profileForm = reactive({
  username: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const profileRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
})

const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = reactive<FormRules>({
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
})

const formatDate = (date?: string) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}

const handleSaveProfile = async () => {
  const valid = await profileFormRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    await updateCurrentUser({ username: profileForm.username })
    await userStore.getUserInfo()
    ElMessage.success('个人信息更新成功')
  } catch {
    ElMessage.error('更新失败，请重试')
  } finally {
    saving.value = false
  }
}

const handleChangePassword = async () => {
  const valid = await passwordFormRef.value?.validate().catch(() => false)
  if (!valid) return

  changingPassword.value = true
  try {
    await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    ElMessage.success('密码修改成功，请重新登录')
    passwordFormRef.value?.resetFields()
    userStore.logout()
  } catch {
    ElMessage.error('密码修改失败，请检查当前密码是否正确')
  } finally {
    changingPassword.value = false
  }
}

onMounted(() => {
  if (userStore.user) {
    profileForm.username = userStore.user.username
  }
})
</script>

<style scoped>
.settings-container {
  max-width: 1000px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.settings-card {
  border-radius: 8px;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
}

.account-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #909399;
  font-size: 14px;
}

.info-item .value {
  color: #303133;
  font-size: 14px;
}
</style>
