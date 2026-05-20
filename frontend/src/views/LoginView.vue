<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <el-icon :size="48" color="#0A6ED1"><Setting /></el-icon>
        </div>
        <h1 class="login-title">품질관리시스템</h1>
        <p class="login-subtitle">QMS - IATF 16949</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="사용자 ID" prop="user_id">
          <el-input
            v-model="form.user_id"
            placeholder="사용자 ID를 입력하세요"
            prefix-icon="User"
            size="large"
            :disabled="loading"
          />
        </el-form-item>

        <el-form-item label="비밀번호" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="비밀번호를 입력하세요"
            prefix-icon="Lock"
            size="large"
            show-password
            :disabled="loading"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-alert
          v-if="errorMsg"
          :title="errorMsg"
          type="error"
          show-icon
          :closable="true"
          style="margin-bottom: 16px;"
          @close="errorMsg = ''"
        />

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%;"
            :loading="loading"
            @click="handleLogin"
          >
            로그인
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <span>MES 품질관리시스템 v1.0</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Setting } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  user_id: '',
  password: ''
})

const rules: FormRules = {
  user_id: [
    { required: true, message: '사용자 ID를 입력하세요', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '비밀번호를 입력하세요', trigger: 'blur' },
    { min: 4, message: '비밀번호는 4자 이상이어야 합니다', trigger: 'blur' }
  ]
}

async function handleLogin() {
  if (!formRef.value) return
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
  } catch {
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    await authStore.login(form.user_id, form.password)
  } catch (error: any) {
    errorMsg.value = error.message || '로그인에 실패했습니다. 다시 시도해 주세요.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--qms-primary-dark) 0%, var(--qms-primary) 100%);
}

.login-card {
  width: 420px;
  padding: 40px;
  background: var(--qms-bg-white);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-logo {
  margin-bottom: 16px;
}

.login-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--qms-text-primary);
  margin: 0 0 4px 0;
}

.login-subtitle {
  font-size: 14px;
  color: var(--qms-text-secondary);
  margin: 0;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--qms-border);
  font-size: 12px;
  color: var(--qms-text-secondary);
}
</style>
