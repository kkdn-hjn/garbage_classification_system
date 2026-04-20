<template>
  <div class="service-config-page">
    <h1 class="page-title">服务配置</h1>

    <div class="config-card">
      <p class="card-desc">百度智能云识别服务凭证（与系统设置中的模型服务配置共用同一存储）</p>
      <div class="form-grid">
        <div class="form-item">
          <label>API 地址</label>
          <input v-model="form.model_api_url" type="text" placeholder="https://aip.baidubce.com" />
          <span class="form-hint">EasyDL 发布后「服务详情」里的完整接口地址，例如：https://aip.baidubce.com/rpc/2.0/ai_custom/v1/classification/你的服务名</span>
        </div>
        <div class="form-item">
          <label>API Key</label>
          <input v-model="form.model_api_key" type="text" autocomplete="off" placeholder="请输入 API Key" />
        </div>
        <div class="form-item">
          <label>Secret Key</label>
          <input v-model="form.model_secret_key" type="password" autocomplete="new-password" placeholder="请输入 Secret Key" />
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

/** 本地开发可在 frontend/.env.local 中配置，勿将真实密钥提交到 Git */
const envDefaults = () => ({
  model_api_url: import.meta.env.VITE_BAIDU_API_URL || 'https://aip.baidubce.com',
  model_api_key: import.meta.env.VITE_BAIDU_API_KEY || '',
  model_secret_key: import.meta.env.VITE_BAIDU_SECRET_KEY || ''
})

const form = ref({
  model_api_url: '',
  model_api_key: '',
  model_secret_key: ''
})

const saving = ref(false)
const saveMessage = ref('')
const saveSuccess = ref(false)

onMounted(() => loadConfig())

async function loadConfig() {
  saveMessage.value = ''
  try {
    const res = await api.get('/service/config')
    const d = res.data || {}
    form.value = {
      model_api_url: d.model_api_url || '',
      model_api_key: d.model_api_key || '',
      model_secret_key: d.model_secret_key || ''
    }
    const def = envDefaults()
    if (!form.value.model_api_url) form.value.model_api_url = def.model_api_url
    if (!form.value.model_api_key && def.model_api_key) form.value.model_api_key = def.model_api_key
    if (!form.value.model_secret_key && def.model_secret_key) form.value.model_secret_key = def.model_secret_key
  } catch (e) {
    saveMessage.value = e.response?.data?.detail || '加载配置失败（需要「服务管理」权限）'
    saveSuccess.value = false
  }
}

async function handleSave() {
  saving.value = true
  saveMessage.value = ''
  try {
    await api.put('/service/config', {
      model_api_url: form.value.model_api_url || null,
      model_api_key: form.value.model_api_key || null,
      model_secret_key: form.value.model_secret_key || null
    })
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
.service-config-page {
  min-height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 24px 0;
}

.config-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
  margin-bottom: 20px;
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
  max-width: 520px;
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
