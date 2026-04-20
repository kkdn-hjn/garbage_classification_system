<template>
  <div class="recognize-page">
    <h1 class="page-title">在线图片识别</h1>

    <div class="card">
      <div class="upload-row">
        <label class="file-label">
          <input type="file" accept="image/*" class="file-input" @change="onFile" />
          <span class="btn-choose">选择图片</span>
        </label>
        <span v-if="fileName" class="file-name">{{ fileName }}</span>
      </div>
      <div class="row-top">
        <label>云端 TopN（仅在使用 EasyDL 时生效）</label>
        <input v-model.number="topNum" type="number" min="1" max="20" class="input-num" />
      </div>
      <button type="button" class="btn-submit" :disabled="!file || loading" @click="submit">
        {{ loading ? '识别中…' : '开始识别' }}
      </button>
    </div>

    <div v-if="error" class="result-card error">
      <p class="result-title">失败</p>
      <pre class="result-pre">{{ error }}</pre>
    </div>

    <div v-if="result && result.ok" class="result-card ok">
      <p class="result-title">
        识别结果
        <span :class="['badge', result.source === 'easydl' ? 'badge-cloud' : 'badge-local']">
          {{ result.source === 'easydl' ? '云端 EasyDL' : '本地模型' }}
        </span>
        <span v-if="result.latency_ms != null" class="latency">延迟 {{ result.latency_ms }} ms</span>
      </p>

      <template v-if="result.source === 'easydl' && result.result">
        <pre class="result-pre">{{ formatJson(result.result) }}</pre>
      </template>
      <template v-else-if="result.result">
        <ul class="result-list">
          <li><strong>细类</strong>：{{ result.result.class_name }}</li>
          <li><strong>置信度</strong>：{{ result.result.confidence }}%</li>
          <li><strong>大类</strong>：{{ result.result.category }}</li>
          <li v-if="result.result.model_path" class="hint"><strong>模型</strong>：{{ result.result.model_path }}</li>
        </ul>
      </template>

      <p v-if="result.source === 'easydl' && result.local_error" class="fallback-hint">
        说明：本地模型未使用或失败，已改用云端。本地侧信息：{{ result.local_error }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'

const file = ref(null)
const fileName = ref('')
const topNum = ref(2)
const loading = ref(false)
const error = ref('')
const result = ref(null)

function onFile(e) {
  const f = e.target.files?.[0]
  file.value = f || null
  fileName.value = f?.name || ''
  error.value = ''
  result.value = null
}

function formatJson(obj) {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

async function submit() {
  if (!file.value) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    const res = await api.post(`/recognize/predict?top_num=${topNum.value}`, fd)
    if (!res.data.ok) {
      const parts = [res.data.error, res.data.local_error].filter(Boolean)
      error.value = parts.join('；') || '识别失败'
      result.value = null
    } else {
      result.value = res.data
    }
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || '请求失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.recognize-page {
  min-height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
}

.page-desc {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.page-desc code {
  font-size: 13px;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
  margin-bottom: 20px;
}

.upload-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.file-input {
  display: none;
}

.file-label {
  cursor: pointer;
}

.btn-choose {
  display: inline-block;
  padding: 8px 16px;
  background: #fafafa;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.file-name {
  font-size: 14px;
  color: #595959;
}

.row-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.row-top label {
  font-size: 14px;
  color: #595959;
}

.input-num {
  width: 80px;
  padding: 6px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.btn-submit {
  padding: 10px 24px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background: #40a9ff;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 20px 24px;
}

.result-card.error {
  border-left: 3px solid #ff4d4f;
}

.result-card.ok {
  border-left: 3px solid #52c41a;
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.badge {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
}

.badge-cloud {
  background: #e6f7ff;
  color: #1890ff;
}

.badge-local {
  background: #f6ffed;
  color: #52c41a;
}

.latency {
  font-size: 13px;
  font-weight: 400;
  color: #8c8c8c;
}

.result-pre {
  margin: 0;
  padding: 12px;
  background: #fafafa;
  border-radius: 4px;
  font-size: 13px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.result-list {
  margin: 0;
  padding-left: 20px;
  font-size: 14px;
  line-height: 1.8;
}

.result-list .hint {
  font-size: 12px;
  color: #8c8c8c;
}

.fallback-hint {
  margin: 16px 0 0 0;
  font-size: 13px;
  color: #8c8c8c;
}
</style>
