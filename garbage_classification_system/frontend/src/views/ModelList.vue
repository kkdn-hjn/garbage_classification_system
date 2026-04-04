<template>
  <div class="model-list-page">
    <div class="page-header">
      <h1 class="page-title">模型列表</h1>
      <button class="btn-refresh" @click="load">刷新</button>
    </div>

    <p class="page-desc">展示 backend/ml_models 及根目录下的 .h5 模型文件。将模型放入 ml_models 目录即可在此查看。</p>

    <div class="model-dir-hint" v-if="modelDir">模型目录：{{ modelDir }}</div>

    <div class="table-card">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>模型名称</th>
              <th>路径</th>
              <th>大小</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="4" class="loading-cell">加载中...</td>
            </tr>
            <tr v-else-if="models.length === 0">
              <td colspan="4" class="empty-cell">暂无模型，请将 .h5 文件放入 ml_models 目录</td>
            </tr>
            <tr v-else v-for="(m, idx) in models" :key="m.name" class="data-row">
              <td>{{ idx + 1 }}</td>
              <td><strong>{{ m.name }}</strong></td>
              <td class="path-cell">{{ m.path }}</td>
              <td>{{ m.size_mb }} MB</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const models = ref([])
const modelDir = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await api.get('/model/list')
    models.value = res.data.models || []
    modelDir.value = res.data.model_dir || ''
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.model-list-page {
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
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

.page-desc {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0 0 12px 0;
}

.model-dir-hint {
  font-size: 13px;
  color: #595959;
  margin-bottom: 20px;
}

.table-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
}

.table-wrap {
  overflow-x: auto;
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

.path-cell {
  font-family: monospace;
  font-size: 13px;
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
</style>
