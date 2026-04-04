<template>
  <div class="statistics-page">
    <div class="page-header">
      <h1 class="page-title">数据集统计</h1>
      <button class="btn-refresh" @click="load">刷新</button>
    </div>

    <div v-if="loading" class="loading-wrap">加载中...</div>
    <template v-else>
      <div class="summary-cards">
        <div class="card">
          <div class="card-value">{{ stats.total }}</div>
          <div class="card-label">图片总数</div>
        </div>
        <div class="card">
          <div class="card-value">{{ stats.category_count }}</div>
          <div class="card-label">分类数量</div>
        </div>
        <div class="card">
          <div class="card-value">{{ maxCategory }}</div>
          <div class="card-label">最多分类</div>
        </div>
        <div class="card">
          <div class="card-value">{{ minCategory }}</div>
          <div class="card-label">最少分类</div>
        </div>
      </div>

      <div class="chart-card">
        <h3 class="section-title">各类别图片数量</h3>
        <div class="bar-chart">
          <div
            v-for="item in stats.items"
            :key="item.name"
            class="bar-row"
          >
            <span class="bar-label">{{ item.name }}</span>
            <div class="bar-wrap">
              <div
                class="bar-fill"
                :style="{ width: barWidth(item.count) + '%' }"
              />
              <span class="bar-value">{{ item.count }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="table-card">
        <h3 class="section-title">明细表</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>分类</th>
              <th>数量</th>
              <th>占比</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in stats.items" :key="item.name">
              <td>{{ item.name }}</td>
              <td>{{ item.count }}</td>
              <td>{{ percent(item.count) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const stats = ref({
  total: 0,
  category_count: 0,
  items: [],
  max_count: 0
})
const loading = ref(false)

const maxCategory = computed(() => {
  const items = stats.value.items
  if (!items.length) return '-'
  const max = Math.max(...items.map((x) => x.count))
  const found = items.find((x) => x.count === max)
  return found ? `${found.name} (${max})` : '-'
})

const minCategory = computed(() => {
  const items = stats.value.items
  if (!items.length) return '-'
  const min = Math.min(...items.map((x) => x.count))
  const found = items.find((x) => x.count === min)
  return found ? `${found.name} (${min})` : '-'
})

function barWidth(count) {
  const max = stats.value.max_count
  if (!max || max === 0) return 0
  return Math.min(100, (count / max) * 100)
}

function percent(count) {
  const total = stats.value.total
  if (!total) return '0%'
  return ((count / total) * 100).toFixed(1) + '%'
}

async function load() {
  loading.value = true
  try {
    const res = await api.get('/data/statistics')
    stats.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.statistics-page {
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.btn-refresh {
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-refresh:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.loading-wrap {
  text-align: center;
  padding: 48px;
  color: #8c8c8c;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 20px;
  border: 1px solid #f0f0f0;
}

.card-value {
  font-size: 28px;
  font-weight: 600;
  color: #1890ff;
  line-height: 1.2;
}

.card-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 8px;
}

.chart-card,
.table-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 20px 0;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-label {
  width: 80px;
  font-size: 14px;
  color: #262626;
  flex-shrink: 0;
}

.bar-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.bar-fill {
  height: 24px;
  background: linear-gradient(90deg, #1890ff, #69c0ff);
  border-radius: 4px;
  min-width: 4px;
  transition: width 0.3s;
}

.bar-value {
  font-size: 14px;
  color: #595959;
  min-width: 36px;
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

.data-table tr:hover {
  background: #fafafa;
}
</style>
