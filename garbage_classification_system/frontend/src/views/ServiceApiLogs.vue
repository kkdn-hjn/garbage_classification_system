<template>
  <div class="api-logs-page">
    <h1 class="page-title">API 调用记录</h1>
    <p class="page-desc">统计范围：在线识别接口 <code>/api/recognize/predict</code>（按自然日汇总）。</p>

    <div class="toolbar">
      <button type="button" class="btn-refresh" :disabled="loading" @click="fetchStats">
        {{ loading ? '加载中…' : '刷新' }}
      </button>
      <span v-if="error" class="error-text">{{ error }}</span>
    </div>

    <div class="metrics-card">
      <h2 class="section-title">调用概览</h2>
      <div class="metrics-grid">
        <div class="metric-item">
          <span class="metric-label">今日调用量</span>
          <span class="metric-value">{{ fmtCount(stats.today_calls) }} 次</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">成功率</span>
          <span class="metric-value">{{ stats.today_calls ? stats.today_success_rate.toFixed(1) + '%' : '—' }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">平均耗时</span>
          <span class="metric-value">{{ stats.today_calls ? stats.today_avg_latency_ms + 'ms' : '—' }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">今日失败数</span>
          <span class="metric-value">{{ fmtCount(stats.today_failures) }} 次</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">累计调用量</span>
          <span class="metric-value">{{ fmtCount(stats.total_calls) }} 次</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const loading = ref(false)
const error = ref('')
const stats = ref({
  today_calls: 0,
  today_success_rate: 0,
  today_avg_latency_ms: 0,
  today_failures: 0,
  total_calls: 0
})

function fmtCount(n) {
  if (n == null) return '—'
  return Number(n).toLocaleString('zh-CN')
}

async function fetchStats() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('/recognize/stats')
    stats.value = res.data
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.api-logs-page {
  min-height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
}

.page-desc {
  font-size: 13px;
  color: #8c8c8c;
  margin: 0 0 20px 0;
}

.page-desc code {
  font-size: 12px;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
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

.error-text {
  font-size: 13px;
  color: #ff4d4f;
}

.metrics-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 16px 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
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
