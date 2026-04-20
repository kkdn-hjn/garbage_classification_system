<template>
  <div class="service-status-page">
    <h1 class="page-title">识别服务状态</h1>

    <div class="status-card">
      <div class="status-row">
        <span :class="['status-dot', online ? 'ok' : 'bad']" />
        <span class="status-text">{{ online ? 'API 在线 · 服务正常' : 'API 离线 · 服务异常' }}</span>
      </div>
      <p v-if="statusMessage && !online" class="status-msg">{{ statusMessage }}</p>
      <div class="status-footer">
        <p class="status-meta">最近检测：{{ lastCheckText }}</p>
        <button type="button" class="btn-refresh" :disabled="loading" @click="fetchStatus">
          {{ loading ? '检测中…' : '重新检测' }}
        </button>
      </div>
    </div>

    <div class="metrics-card">
      <h2 class="section-title">服务可用性指标</h2>
      <div class="metrics-grid">
        <div class="metric-item">
          <span class="metric-label">近 24 小时可用率</span>
          <span class="metric-value">{{ availability24 }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">近 7 天可用率</span>
          <span class="metric-value">{{ availability7d }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">当前接口响应延迟</span>
          <span class="metric-value">{{ latencyText }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const LOG_KEY = 'garbage_service_health_v1'

const online = ref(false)
const latencyMs = ref(null)
const statusMessage = ref('')
const lastCheck = ref(null)
const loading = ref(false)

const lastCheckText = computed(() => {
  if (!lastCheck.value) return '—'
  return new Date(lastCheck.value).toLocaleString()
})

const latencyText = computed(() => {
  if (latencyMs.value == null) return '—'
  return `${latencyMs.value} ms`
})

function loadLog() {
  try {
    const raw = localStorage.getItem(LOG_KEY)
    if (!raw) return []
    const arr = JSON.parse(raw)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

function saveLogEntry(entry) {
  const now = Date.now()
  const arr = loadLog().filter((e) => now - e.t < 8 * 24 * 60 * 60 * 1000)
  arr.push(entry)
  localStorage.setItem(LOG_KEY, JSON.stringify(arr.slice(-2000)))
}

function pctOk(windowMs) {
  const now = Date.now()
  const arr = loadLog().filter((e) => now - e.t <= windowMs)
  if (!arr.length) return null
  const ok = arr.filter((e) => e.ok).length
  return ((ok / arr.length) * 100).toFixed(2)
}

const availability24 = computed(() => {
  const p = pctOk(24 * 60 * 60 * 1000)
  return p == null ? '—' : `${p}%`
})

const availability7d = computed(() => {
  const p = pctOk(7 * 24 * 60 * 60 * 1000)
  return p == null ? '—' : `${p}%`
})

async function fetchStatus() {
  loading.value = true
  try {
    const res = await api.get('/service/status')
    online.value = !!res.data.online
    latencyMs.value = res.data.latency_ms ?? null
    statusMessage.value = res.data.message || ''
    lastCheck.value = Date.now()
    saveLogEntry({ t: lastCheck.value, ok: online.value })
  } catch (e) {
    online.value = false
    latencyMs.value = null
    statusMessage.value = e.response?.data?.detail || e.message || '请求失败'
    lastCheck.value = Date.now()
    saveLogEntry({ t: lastCheck.value, ok: false })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStatus()
})
</script>

<style scoped>
.service-status-page {
  min-height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 24px 0;
}

.status-card,
.metrics-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
  margin-bottom: 20px;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.ok {
  background: #52c41a;
  box-shadow: 0 0 0 3px rgba(82, 196, 26, 0.2);
}

.status-dot.bad {
  background: #ff4d4f;
  box-shadow: 0 0 0 3px rgba(255, 77, 79, 0.2);
}

.status-text {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.status-msg {
  margin: 12px 0 0 0;
  font-size: 13px;
  color: #ff4d4f;
}

.status-footer {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.status-meta {
  margin: 0;
  font-size: 12px;
  color: #8c8c8c;
}

.btn-refresh {
  padding: 6px 14px;
  font-size: 13px;
  color: #1890ff;
  background: #fff;
  border: 1px solid #1890ff;
  border-radius: 4px;
  cursor: pointer;
}

.btn-refresh:hover:not(:disabled) {
  background: #e6f7ff;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 16px 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.metric-label {
  font-size: 13px;
  color: #8c8c8c;
}

.metric-value {
  font-size: 22px;
  font-weight: 600;
  color: #1890ff;
}
</style>
