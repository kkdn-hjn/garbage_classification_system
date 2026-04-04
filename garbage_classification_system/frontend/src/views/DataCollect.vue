<template>
  <div class="collect-page">
    <h1 class="page-title">数据采集</h1>
    <p class="page-desc">从百度图片按分类采集垃圾图片，自动保存到数据库和 laji3 目录</p>

    <div class="collect-card">
      <div class="form-row">
        <div class="form-group">
          <label>选择分类</label>
          <select v-model="form.category" class="form-select">
            <option value="">请选择</option>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>采集数量</label>
          <input v-model.number="form.count" type="number" min="1" max="50" class="form-input" />
          <span class="form-hint">1-50 张</span>
        </div>
        <div class="form-group form-actions">
          <button class="btn-collect" @click="startCollect" :disabled="collecting || !form.category">
            {{ collecting ? '采集中...' : '开始采集' }}
          </button>
        </div>
      </div>

      <div v-if="result" class="result-box" :class="result.success > 0 ? 'success' : 'warn'">
        <p>{{ result.message }}</p>
        <p>成功 {{ result.success }} 张，失败 {{ result.failed }} 张</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const categories = ref([])
const collecting = ref(false)
const result = ref(null)

const form = ref({
  category: '',
  count: 20
})

onMounted(async () => {
  try {
    const res = await api.get('/data/images/categories')
    categories.value = res.data.categories || []
    if (categories.value.length && !form.value.category) {
      form.value.category = categories.value[0]
    }
  } catch (e) {
    console.error(e)
  }
})

async function startCollect() {
  if (!form.value.category) return
  collecting.value = true
  result.value = null
  try {
    const res = await api.post('/data/collect', {
      category: form.value.category,
      count: Math.max(1, Math.min(50, form.value.count || 20))
    })
    result.value = res.data
  } catch (e) {
    result.value = {
      message: e.response?.data?.detail || '采集失败',
      success: 0,
      failed: 0
    }
  } finally {
    collecting.value = false
  }
}
</script>

<style scoped>
.collect-page {
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
}

.collect-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
  max-width: 560px;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 20px;
}

.form-group {
  flex-shrink: 0;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #262626;
  margin-bottom: 8px;
}

.form-select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  min-width: 140px;
}

.form-input {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  width: 80px;
}

.form-hint {
  display: block;
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

.form-actions {
  margin-left: 8px;
}

.btn-collect {
  padding: 8px 24px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-collect:hover:not(:disabled) {
  background: #40a9ff;
}

.btn-collect:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result-box {
  margin-top: 24px;
  padding: 16px;
  border-radius: 4px;
  font-size: 14px;
}

.result-box.success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #389e0d;
}

.result-box.warn {
  background: #fff7e6;
  border: 1px solid #ffd591;
  color: #d46b08;
}

.result-box p {
  margin: 0 0 4px 0;
}

.result-box p:last-child {
  margin-bottom: 0;
}
</style>
