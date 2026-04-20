<template>
  <div class="history-page">
    <h1 class="page-title">识别历史记录</h1>
    <p class="page-desc">每次调用在线识别接口后自动落库，可按时间与结果追溯。</p>

    <div class="toolbar">
      <button type="button" class="btn-refresh" :disabled="loading" @click="load">
        {{ loading ? '加载中…' : '刷新' }}
      </button>
      <span class="total-hint">共 {{ total.toLocaleString('zh-CN') }} 条</span>
      <span v-if="error" class="error-text">{{ error }}</span>
    </div>

    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>用户</th>
            <th>文件名</th>
            <th>结果</th>
            <th>来源</th>
            <th>细类</th>
            <th>大类</th>
            <th>置信度</th>
            <th>耗时</th>
            <th>错误信息</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in items" :key="row.id">
            <td class="cell-time">{{ formatTime(row.created_at) }}</td>
            <td>{{ row.username || '—' }}</td>
            <td class="cell-file" :title="row.filename">{{ shortName(row.filename) }}</td>
            <td>
              <span :class="['tag', row.success ? 'ok' : 'fail']">{{ row.success ? '成功' : '失败' }}</span>
            </td>
            <td>{{ sourceLabel(row.source) }}</td>
            <td>{{ row.class_name || '—' }}</td>
            <td>{{ row.category || '—' }}</td>
            <td>{{ formatConfidence(row.confidence) }}</td>
            <td>{{ row.latency_ms != null ? row.latency_ms + ' ms' : '—' }}</td>
            <td class="cell-err" :title="row.error_message || ''">{{ shortErr(row.error_message) }}</td>
          </tr>
          <tr v-if="!loading && items.length === 0">
            <td colspan="10" class="empty-cell">暂无记录</td>
          </tr>
        </tbody>
      </table>

      <div v-if="total > pageSize" class="pager">
        <button type="button" class="btn-page" :disabled="page <= 1 || loading" @click="goPage(page - 1)">上一页</button>
        <span class="page-info">第 {{ page }} 页</span>
        <button
          type="button"
          class="btn-page"
          :disabled="page * pageSize >= total || loading"
          @click="goPage(page + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const loading = ref(false)
const error = ref('')
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20

function formatTime(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('zh-CN')
  } catch {
    return iso
  }
}

function shortName(name) {
  if (!name) return '—'
  return name.length > 24 ? name.slice(0, 22) + '…' : name
}

function sourceLabel(s) {
  if (s === 'local') return '本地'
  if (s === 'easydl') return 'EasyDL'
  return s || '—'
}

function formatConfidence(c) {
  if (c == null || c === '') return '—'
  const s = String(c).trim()
  if (s.includes('%')) return s
  const n = parseFloat(s)
  if (!Number.isNaN(n)) {
    // EasyDL：0~1 概率，展示小数；本地模型：多为百分比数值（如 95.2）
    if (n >= 0 && n <= 1) return n.toFixed(4)
    return `${n}%`
  }
  return s
}

function shortErr(msg) {
  if (!msg) return '—'
  return msg.length > 32 ? msg.slice(0, 30) + '…' : msg
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const skip = (page.value - 1) * pageSize
    const res = await api.get('/recognize/history', { params: { skip, limit: pageSize } })
    items.value = res.data.items || []
    total.value = res.data.total ?? 0
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || '加载失败'
    items.value = []
  } finally {
    loading.value = false
  }
}

function goPage(p) {
  page.value = p
  load()
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.history-page {
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

.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
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

.total-hint {
  font-size: 13px;
  color: #8c8c8c;
}

.error-text {
  font-size: 13px;
  color: #ff4d4f;
}

.table-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  overflow: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th,
.data-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.data-table th {
  font-weight: 600;
  color: #595959;
  background: #fafafa;
}

.cell-time {
  white-space: nowrap;
}

.cell-file {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cell-err {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #cf1322;
  font-size: 12px;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.tag.ok {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.tag.fail {
  background: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.empty-cell {
  text-align: center;
  color: #8c8c8c;
  padding: 32px !important;
}

.pager {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
}

.btn-page {
  padding: 4px 12px;
  font-size: 13px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
}

.btn-page:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: #8c8c8c;
}
</style>
