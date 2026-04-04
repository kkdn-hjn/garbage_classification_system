<template>
  <div class="operation-records">
    <h1 class="page-title">操作记录</h1>

    <!-- 筛选卡片 -->
    <div class="filter-card">
      <div class="filter-form">
        <div class="filter-item">
          <label>操作人</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="请输入操作人"
            class="filter-input"
          />
        </div>
        <div class="filter-item">
          <label>操作类型</label>
          <select v-model="filters.log_type" class="filter-select">
            <option value="">请选择操作类型</option>
            <option value="认证">认证</option>
            <option value="用户管理">用户管理</option>
            <option value="系统">系统</option>
          </select>
        </div>
        <div class="filter-item">
          <label>操作时间</label>
          <div class="date-range">
            <input
              v-model="filters.dateStart"
              type="datetime-local"
              class="filter-input date-input"
              placeholder="开始时间"
            />
            <span class="date-sep">至</span>
            <input
              v-model="filters.dateEnd"
              type="datetime-local"
              class="filter-input date-input"
              placeholder="结束时间"
            />
          </div>
        </div>
        <div class="filter-actions">
          <button class="btn-query" @click="handleQuery">查询</button>
          <button class="btn-reset" @click="handleReset">重置</button>
        </div>
      </div>
    </div>

    <!-- 表格卡片 -->
    <div class="table-card">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>操作人</th>
              <th>操作类型</th>
              <th>操作模块</th>
              <th>操作内容</th>
              <th>IP地址</th>
              <th>操作时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="logsLoading">
              <td colspan="7" class="loading-cell">加载中...</td>
            </tr>
            <tr v-else-if="logs.length === 0">
              <td colspan="7" class="empty-cell">暂无数据</td>
            </tr>
            <tr v-else v-for="(log, idx) in logs" :key="log.id" class="data-row">
              <td>{{ (currentLogPage - 1) * logPageSize + idx + 1 }}</td>
              <td>{{ log.username || '-' }}</td>
              <td>
                <span class="type-badge" :class="getBadgeClass(log.action)">
                  {{ getTypeLabel(log.action) }}
                </span>
              </td>
              <td>{{ log.log_type || '-' }}</td>
              <td>{{ log.description || '-' }}</td>
              <td>{{ log.ip_address || '-' }}</td>
              <td>{{ formatTime(log.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination">
        <button
          class="page-btn"
          @click="changeLogPage(currentLogPage - 1)"
          :disabled="currentLogPage === 1 || logsLoading"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ currentLogPage }} 页，共 {{ totalLogPages }} 页（共 {{ totalLogs }} 条）
        </span>
        <button
          class="page-btn"
          @click="changeLogPage(currentLogPage + 1)"
          :disabled="currentLogPage >= totalLogPages || logsLoading"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'

const logs = ref([])
const logsLoading = ref(false)
const totalLogs = ref(0)
const currentLogPage = ref(1)
const logPageSize = 20

const filters = ref({
  search: '',
  log_type: '',
  dateStart: '',
  dateEnd: ''
})

const totalLogPages = computed(() => Math.ceil(totalLogs.value / logPageSize))

onMounted(() => loadLogs())

async function loadLogs() {
  logsLoading.value = true
  try {
    const skip = (currentLogPage.value - 1) * logPageSize
    const params = { skip, limit: logPageSize }
    if (filters.value.log_type) params.log_type = filters.value.log_type
    if (filters.value.search) params.search = filters.value.search
    const response = await api.get('/admin/logs', { params })
    logs.value = response.data.logs
    totalLogs.value = response.data.total
  } catch (error) {
    console.error('加载日志失败:', error)
  } finally {
    logsLoading.value = false
  }
}

function handleQuery() {
  currentLogPage.value = 1
  loadLogs()
}

function handleReset() {
  filters.value = { search: '', log_type: '', dateStart: '', dateEnd: '' }
  currentLogPage.value = 1
  loadLogs()
}

function changeLogPage(page) {
  if (page >= 1 && page <= totalLogPages.value) {
    currentLogPage.value = page
    loadLogs()
  }
}

function formatTime(timeString) {
  if (!timeString) return '-'
  const d = new Date(timeString)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function getTypeLabel(action) {
  if (!action) return '-'
  if (action.includes('登录')) return '登录'
  if (action.includes('注册')) return '注册'
  if (action.includes('编辑') || action.includes('更新')) return '编辑'
  if (action.includes('删除')) return '删除'
  if (action.includes('创建')) return '创建'
  return action.slice(0, 8)
}

function getBadgeClass(action) {
  if (!action) return 'default'
  if (action.includes('登录')) return 'login'
  if (action.includes('注册')) return 'register'
  if (action.includes('编辑') || action.includes('更新')) return 'edit'
  if (action.includes('删除')) return 'delete'
  return 'default'
}
</script>

<style scoped>
.operation-records {
  min-height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 24px 0;
}

.filter-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 20px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item label {
  font-size: 14px;
  color: #595959;
}

.filter-input,
.filter-select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  min-width: 160px;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #1890ff;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input {
  min-width: 180px;
}

.date-sep {
  font-size: 14px;
  color: #8c8c8c;
}

.filter-actions {
  display: flex;
  gap: 12px;
}

.btn-query {
  padding: 8px 20px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-query:hover {
  background: #40a9ff;
}

.btn-reset {
  padding: 8px 20px;
  background: #fff;
  color: #595959;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-reset:hover {
  color: #1890ff;
  border-color: #1890ff;
}

.table-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
}

.table-wrap {
  overflow-x: auto;
  margin-bottom: 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.data-table td {
  padding: 12px 16px;
  font-size: 14px;
  color: #595959;
  border-bottom: 1px solid #f5f5f5;
}

.data-row:hover {
  background: #fafafa;
}

.loading-cell,
.empty-cell {
  text-align: center;
  color: #8c8c8c;
  padding: 48px 16px !important;
}

.type-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.type-badge.login {
  background: #f6ffed;
  color: #52c41a;
}

.type-badge.register {
  background: #e6f7ff;
  color: #1890ff;
}

.type-badge.edit {
  background: #fff7e6;
  color: #fa8c16;
}

.type-badge.delete {
  background: #fff2f0;
  color: #ff4d4f;
}

.type-badge.default {
  background: #f5f5f5;
  color: #595959;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.page-btn {
  padding: 6px 14px;
  border: 1px solid #d9d9d9;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.page-btn:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #8c8c8c;
}
</style>
