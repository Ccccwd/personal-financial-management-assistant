<template>
  <div class="category-manage-page">
    <div class="page-header">
      <el-button link :icon="ArrowLeft" class="back-btn" @click="router.back()">返回</el-button>
      <h1 class="page-title">分类管理</h1>
      <div class="header-placeholder" />
    </div>

    <el-tabs v-model="activeTab" class="type-tabs">
      <el-tab-pane label="支出分类" name="expense" />
      <el-tab-pane label="收入分类" name="income" />
    </el-tabs>

    <div class="category-list">
      <div
        v-for="cat in currentList"
        :key="cat.id"
        class="category-item"
      >
        <div class="cat-left">
          <span class="cat-icon" :style="{ backgroundColor: cat.color + '22' }">{{ cat.icon || '📝' }}</span>
          <span class="cat-name">{{ cat.name }}</span>
          <el-tag v-if="cat.is_system" size="small" type="info" class="sys-tag">系统</el-tag>
        </div>
        <div class="cat-actions">
          <el-button link :icon="Edit" @click="openEdit(cat)" />
          <el-button
            link
            :icon="Delete"
            :disabled="cat.is_system"
            class="del-btn"
            @click="handleDelete(cat)"
          />
        </div>
      </div>

      <el-empty v-if="currentList.length === 0" description="暂无分类" />
    </div>

    <div class="add-btn-wrapper">
      <el-button type="primary" :icon="Plus" @click="openAdd">新增分类</el-button>
    </div>

    <!-- 新增 / 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑分类' : '新增分类'"
      width="360px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="72px" size="large">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" maxlength="10" show-word-limit />
        </el-form-item>

        <el-form-item label="图标" prop="icon">
          <el-input v-model="form.icon" placeholder="输入 Emoji，如 🍔" maxlength="4" />
        </el-form-item>

        <el-form-item label="颜色" prop="color">
          <div class="color-row">
            <el-color-picker v-model="form.color" />
            <div class="color-presets">
              <span
                v-for="c in COLOR_PRESETS"
                :key="c"
                class="color-dot"
                :style="{ backgroundColor: c }"
                :class="{ active: form.color === c }"
                @click="form.color = c"
              />
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useCategoryStore } from '@/stores/category'
import type { Category, CategoryType } from '@/types/category'

const router = useRouter()
const categoryStore = useCategoryStore()

const activeTab = ref<CategoryType>('expense')
const currentList = computed(() => categoryStore.getByType(activeTab.value))

const COLOR_PRESETS = [
  '#EF4444', '#F97316', '#F59E0B', '#84CC16',
  '#10B981', '#06B6D4', '#3B82F6', '#8B5CF6',
  '#EC4899', '#6B7280',
]

// ─── 对话框 ─────────────────────────────────────────────────────────────────
const dialogVisible = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const form = ref({ name: '', icon: '', color: '#3B82F6' })

const rules: FormRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 10, message: '名称长度 1~10 个字符', trigger: 'blur' },
  ],
}

function openAdd() {
  editingId.value = null
  form.value = { name: '', icon: '📝', color: '#3B82F6' }
  dialogVisible.value = true
}

function openEdit(cat: Category) {
  editingId.value = cat.id
  form.value = { name: cat.name, icon: cat.icon ?? '', color: cat.color ?? '#3B82F6' }
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (editingId.value !== null) {
      await categoryStore.editCategory(editingId.value, {
        name: form.value.name,
        icon: form.value.icon || undefined,
        color: form.value.color || undefined,
      })
      ElMessage.success('分类已更新')
    } else {
      await categoryStore.addCategory({
        name: form.value.name,
        type: activeTab.value,
        icon: form.value.icon || undefined,
        color: form.value.color || undefined,
      })
      ElMessage.success('分类已添加')
    }
    dialogVisible.value = false
  } catch {
    // 错误已由请求拦截器统一提示
  } finally {
    submitting.value = false
  }
}

async function handleDelete(cat: Category) {
  if (cat.is_system) return
  await ElMessageBox.confirm(`确认删除分类「${cat.name}」？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await categoryStore.removeCategory(cat.id)
  ElMessage.success('已删除')
}
</script>

<style scoped>
.category-manage-page {
  max-width: 600px;
  margin: 0 auto;
  padding: 0 0 80px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0 8px;
}

.page-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}

.back-btn {
  font-size: 14px;
}

.header-placeholder {
  width: 60px;
}

.type-tabs {
  margin-bottom: 12px;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 12px 16px;
}

.cat-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cat-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.cat-name {
  font-size: 15px;
  font-weight: 500;
  color: #111827;
}

.sys-tag {
  margin-left: 4px;
}

.cat-actions {
  display: flex;
  gap: 4px;
}

.del-btn {
  color: #ef4444 !important;
}

.del-btn:disabled {
  color: #d1d5db !important;
}

.add-btn-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.color-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.color-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.15s;
}

.color-dot.active,
.color-dot:hover {
  border-color: #374151;
}
</style>
