<template>
  <div class="categories-page">
    <div class="page-header">
      <h1 class="page-title">垃圾类别管理</h1>
      <button class="btn-primary" @click="openAdd">添加分类</button>
    </div>

    <div class="table-card">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>分类名称</th>
              <th>类型</th>
              <th>描述</th>
              <th>图片数量</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7" class="loading-cell">加载中...</td>
            </tr>
            <tr v-else-if="categories.length === 0">
              <td colspan="7" class="empty-cell">暂无分类，请添加</td>
            </tr>
            <tr v-else v-for="(cat, idx) in categories" :key="cat.id" class="data-row">
              <td>{{ idx + 1 }}</td>
              <td><strong>{{ cat.name }}</strong></td>
              <td><span class="type-badge">{{ cat.type || '-' }}</span></td>
              <td class="desc-cell">{{ cat.description || '-' }}</td>
              <td>{{ cat.image_count }}</td>
              <td>{{ formatDate(cat.created_at) }}</td>
              <td>
                <button class="btn-edit" @click="openEdit(cat)">编辑</button>
                <button
                  class="btn-delete"
                  @click="confirmDelete(cat)"
                  :disabled="cat.image_count > 0"
                  :title="cat.image_count > 0 ? '有关联图片时不可删除' : '删除'"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p class="table-hint">共 {{ categories.length }} 个分类。删除前需先迁移或删除该分类下的图片。</p>
    </div>

    <!-- 添加/编辑弹窗 -->
    <div v-if="showForm" class="modal-overlay" @click="closeForm">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEdit ? '编辑分类' : '添加分类' }}</h3>
          <button class="close-btn" @click="closeForm">×</button>
        </div>
        <form @submit.prevent="save" class="modal-body">
          <div class="form-group">
            <label>分类名称 *</label>
            <input v-model="form.name" type="text" required placeholder="如：纸类、塑料" />
            <span v-if="isEdit" class="form-hint">修改名称会同步更新图片分类及物理目录</span>
          </div>
          <div class="form-group">
            <label>类型</label>
            <select v-model="form.type">
              <option value="">请选择</option>
              <option value="可回收">可回收</option>
              <option value="厨余垃圾">厨余垃圾</option>
              <option value="有害垃圾">有害垃圾</option>
              <option value="其他">其他</option>
            </select>
          </div>
          <div class="form-group">
            <label>描述</label>
            <input v-model="form.description" type="text" placeholder="简要说明" />
          </div>
          <div class="form-group">
            <label>排序</label>
            <input v-model.number="form.sort_order" type="number" min="0" placeholder="数字越小越靠前" />
          </div>
          <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
          <div class="modal-footer">
            <button type="button" class="btn-cancel" @click="closeForm">取消</button>
            <button type="submit" class="btn-submit" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDelete" class="modal-overlay" @click="showDelete = false">
      <div class="modal-content delete-modal" @click.stop>
        <div class="modal-header">
          <h3>确认删除</h3>
        </div>
        <div class="modal-body">
          <p>确定要删除分类 <strong>{{ toDelete?.name }}</strong> 吗？</p>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showDelete = false">取消</button>
            <button class="btn-delete-confirm" @click="doDelete" :disabled="saving">
              {{ saving ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const categories = ref([])
const loading = ref(false)
const showForm = ref(false)
const showDelete = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const isEdit = ref(false)
const editingId = ref(null)
const toDelete = ref(null)

const form = ref({
  name: '',
  type: '',
  description: '',
  sort_order: 0
})

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    const res = await api.get('/data/categories/list')
    categories.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openAdd() {
  form.value = { name: '', type: '', description: '', sort_order: categories.value.length }
  isEdit.value = false
  editingId.value = null
  errorMessage.value = ''
  showForm.value = true
}

function openEdit(cat) {
  form.value = {
    name: cat.name,
    type: cat.type || '',
    description: cat.description || '',
    sort_order: cat.sort_order
  }
  isEdit.value = true
  editingId.value = cat.id
  errorMessage.value = ''
  showForm.value = true
}

function closeForm() {
  showForm.value = false
}

function confirmDelete(cat) {
  if (cat.image_count > 0) return
  toDelete.value = cat
  showDelete.value = true
}

async function save() {
  saving.value = true
  errorMessage.value = ''
  try {
    if (isEdit.value) {
      await api.put(`/data/categories/${editingId.value}`, form.value)
    } else {
      await api.post('/data/categories', form.value)
    }
    closeForm()
    load()
  } catch (e) {
    errorMessage.value = e.response?.data?.detail || '操作失败'
  } finally {
    saving.value = false
  }
}

async function doDelete() {
  if (!toDelete.value) return
  saving.value = true
  try {
    await api.delete(`/data/categories/${toDelete.value.id}`)
    showDelete.value = false
    toDelete.value = null
    load()
  } catch (e) {
    errorMessage.value = e.response?.data?.detail || '删除失败'
  } finally {
    saving.value = false
  }
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('zh-CN')
}
</script>

<style scoped>
.categories-page {
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

.btn-primary {
  padding: 8px 20px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary:hover {
  background: #40a9ff;
}

.table-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
}

.table-wrap {
  overflow-x: auto;
  margin-bottom: 12px;
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

.desc-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.loading-cell,
.empty-cell {
  text-align: center;
  color: #8c8c8c;
  padding: 48px 16px !important;
}

.table-hint {
  font-size: 13px;
  color: #8c8c8c;
  margin: 0;
}

.type-badge {
  padding: 2px 8px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
  font-size: 12px;
}

.btn-edit,
.btn-delete {
  padding: 4px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 8px;
}

.btn-edit {
  background: #1890ff;
  color: white;
}

.btn-delete {
  background: #ff4d4f;
  color: white;
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #8c8c8c;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #262626;
  margin-bottom: 8px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-hint {
  display: block;
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

.error-message {
  color: #ff4d4f;
  font-size: 14px;
  margin-bottom: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.btn-cancel {
  padding: 8px 20px;
  background: #fff;
  color: #595959;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-submit {
  padding: 8px 20px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-delete-confirm {
  padding: 8px 20px;
  background: #ff4d4f;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
</style>
