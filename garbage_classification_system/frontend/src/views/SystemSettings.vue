<template>
  <div class="settings-page">
    <h1 class="page-title">系统设置</h1>

    <div class="settings-card">
      <h2 class="card-title">模型服务配置</h2>
      <p class="card-desc">配置百度智能云垃圾分类识别 API 服务</p>
      <div class="form-grid">
        <div class="form-item">
          <label>API 地址</label>
          <input
            v-model="form.model_api_url"
            type="text"
            placeholder="例如：https://aip.baidubce.com"
          />
          <span class="form-hint">百度智能云识别服务 API 地址</span>
        </div>
        <div class="form-item">
          <label>API Key</label>
          <input
            v-model="form.model_api_key"
            type="text"
            placeholder="请输入 API Key"
          />
          <span class="form-hint">在百度智能云控制台获取</span>
        </div>
        <div class="form-item">
          <label>Secret Key</label>
          <input
            v-model="form.model_secret_key"
            type="password"
            placeholder="请输入 Secret Key"
          />
          <span class="form-hint">与 API Key 配对使用</span>
        </div>
      </div>
    </div>

    <div class="settings-card">
      <h2 class="card-title">安全与日志设置</h2>
      <p class="card-desc">操作日志与安全相关配置</p>
      <div class="form-grid">
        <div class="form-item">
          <label>操作日志保存时长（天）</label>
          <input
            v-model.number="form.log_retention_days"
            type="number"
            min="1"
            max="3650"
            placeholder="例如：90"
          />
          <span class="form-hint">超过该天数的操作日志将被自动清理，建议 30～365 天</span>
        </div>
      </div>
    </div>

    <div class="actions">
      <button class="btn-save" :disabled="saving" @click="handleSave">
        {{ saving ? '保存中...' : '保存配置' }}
      </button>
      <span v-if="saveMessage" :class="['save-message', saveSuccess ? 'success' : 'error']">
        {{ saveMessage }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const form = ref({
  model_api_url: '',
  model_api_key: '',
  model_secret_key: '',
  log_retention_days: 90
})

const saving = ref(false)
const saveMessage = ref('')
const saveSuccess = ref(false)

onMounted(() => loadSettings())

async function loadSettings() {
  try {
    const res = await api.get('/admin/settings')
    form.value = {
      model_api_url: res.data.model_api_url || '',
      model_api_key: res.data.model_api_key || '',
      model_secret_key: res.data.model_secret_key || '',
      log_retention_days: res.data.log_retention_days ?? 90
    }
  } catch (e) {
    console.error('加载设置失败:', e)
    saveMessage.value = '加载设置失败'
    saveSuccess.value = false
  }
}

async function handleSave() {
  saving.value = true
  saveMessage.value = ''
  try {
    const payload = {
      model_api_url: form.value.model_api_url || null,
      model_api_key: form.value.model_api_key || null,
      model_secret_key: form.value.model_secret_key || null,
      log_retention_days: form.value.log_retention_days
    }
    if (payload.log_retention_days < 1) payload.log_retention_days = 1
    if (payload.log_retention_days > 3650) payload.log_retention_days = 3650

    await api.put('/admin/settings', payload)
    saveMessage.value = '保存成功'
    saveSuccess.value = true
  } catch (e) {
    saveMessage.value = e.response?.data?.detail || '保存失败'
    saveSuccess.value = false
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings-page {
  min-height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 24px 0;
}

.settings-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
}

.card-desc {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0 0 20px 0;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item label {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.form-item input {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  max-width: 480px;
}

.form-item input:focus {
  outline: none;
  border-color: #1890ff;
}

.form-hint {
  font-size: 12px;
  color: #8c8c8c;
}

.actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-save {
  padding: 10px 24px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-save:hover:not(:disabled) {
  background: #40a9ff;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-message {
  font-size: 14px;
}

.save-message.success {
  color: #52c41a;
}

.save-message.error {
  color: #ff4d4f;
}
</style>
