<template>
  <div class="user-page">
    <div class="page-header">
      <h1 class="page-title">员工管理</h1>
      <button class="btn-primary" @click="showAddDialog = true">添加用户</button>
    </div>

    <div class="filter-card">
      <div class="filter-form">
        <div class="filter-item">
          <label>搜索</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索用户名或邮箱..."
            class="filter-input"
            @input="handleSearch"
          />
        </div>
        <div class="filter-actions">
          <button class="btn-query" @click="loadUsers">查询</button>
          <button class="btn-reset" @click="searchQuery = ''; currentPage = 1; loadUsers()">重置</button>
        </div>
      </div>
    </div>

    <div class="table-card">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="loading-cell">加载中...</td>
            </tr>
            <tr v-else-if="users.length === 0">
              <td colspan="6" class="empty-cell">暂无数据</td>
            </tr>
            <tr v-else v-for="user in users" :key="user.id" class="data-row">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
              <td>
                <span class="role-badge" :class="user.role === 1 ? 'admin' : 'user'">
                  {{ user.role === 1 ? '管理员' : '普通用户' }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <button class="btn-edit" @click="editUser(user)">编辑</button>
                <button
                  class="btn-delete"
                  @click="confirmDelete(user)"
                  :disabled="user.id === currentUserId"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination">
        <button class="page-btn" @click="changePage(currentPage - 1)" :disabled="currentPage === 1">
          上一页
        </button>
        <span class="page-info">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页（共 {{ total }} 条）
        </span>
        <button class="page-btn" @click="changePage(currentPage + 1)" :disabled="currentPage >= totalPages">
          下一页
        </button>
      </div>
    </div>

    <div v-if="showAddDialog || showEditDialog" class="modal-overlay" @click="closeDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ showAddDialog ? '添加用户' : '编辑用户' }}</h3>
          <button class="close-btn" @click="closeDialog">×</button>
        </div>
        <form @submit.prevent="saveUser" class="modal-body">
          <div class="form-group">
            <label>用户名 *</label>
            <input v-model="formData.username" type="text" required :disabled="showEditDialog" />
          </div>
          <div class="form-group">
            <label>邮箱 *</label>
            <input v-model="formData.email" type="email" required />
          </div>
          <div class="form-group">
            <label>密码 {{ showAddDialog ? '*' : '(留空则不修改)' }}</label>
            <input v-model="formData.password" type="password" :required="showAddDialog" />
          </div>
          <div class="form-group">
            <label>角色 *</label>
            <select v-model="formData.role" required>
              <option :value="2">普通用户</option>
              <option :value="1">管理员</option>
            </select>
          </div>
          <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
          <div class="modal-footer">
            <button type="button" class="btn-cancel" @click="closeDialog">取消</button>
            <button type="submit" class="btn-submit" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showDeleteDialog" class="modal-overlay" @click="showDeleteDialog = false">
      <div class="modal-content delete-modal" @click.stop>
        <div class="modal-header">
          <h3>确认删除</h3>
        </div>
        <div class="modal-body">
          <p>确定要删除用户 <strong>{{ userToDelete?.username }}</strong> 吗？此操作不可恢复。</p>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showDeleteDialog = false">取消</button>
            <button class="btn-delete-confirm" @click="deleteUser" :disabled="saving">
              {{ saving ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const users = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = 10
const searchQuery = ref('')
let searchTimeout = null

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const userToDelete = ref(null)

const formData = ref({ username: '', email: '', password: '', role: 2 })
const editingUserId = ref(null)
const totalPages = computed(() => Math.ceil(total.value / pageSize))

onMounted(() => loadUsers())

async function loadUsers() {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize
    const params = { skip, limit: pageSize }
    if (searchQuery.value) params.search = searchQuery.value
    const response = await api.get('/users', { params })
    users.value = response.data.users
    total.value = response.data.total
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadUsers()
  }, 500)
}

function changePage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadUsers()
  }
}

function formatDate(dateString) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

function editUser(user) {
  editingUserId.value = user.id
  formData.value = { username: user.username, email: user.email, password: '', role: user.role }
  showEditDialog.value = true
}

function confirmDelete(user) {
  userToDelete.value = user
  showDeleteDialog.value = true
}

function closeDialog() {
  showAddDialog.value = false
  showEditDialog.value = false
  errorMessage.value = ''
  editingUserId.value = null
  formData.value = { username: '', email: '', password: '', role: 2 }
}

async function saveUser() {
  saving.value = true
  errorMessage.value = ''
  try {
    if (showAddDialog.value) {
      await api.post('/users', formData.value)
    } else {
      const updateData = { ...formData.value }
      if (!updateData.password) delete updateData.password
      await api.put(`/users/${editingUserId.value}`, updateData)
    }
    closeDialog()
    loadUsers()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '操作失败'
  } finally {
    saving.value = false
  }
}

async function deleteUser() {
  if (!userToDelete.value) return
  saving.value = true
  try {
    await api.delete(`/users/${userToDelete.value.id}`)
    showDeleteDialog.value = false
    userToDelete.value = null
    loadUsers()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '删除失败'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.user-page {
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

.filter-item label {
  display: block;
  font-size: 14px;
  color: #595959;
  margin-bottom: 8px;
}

.filter-input {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
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

.btn-reset {
  padding: 8px 20px;
  background: #fff;
  color: #595959;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
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

.role-badge {
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
}

.role-badge.admin {
  background: #fff7e6;
  color: #fa8c16;
}

.role-badge.user {
  background: #e6f7ff;
  color: #1890ff;
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

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #8c8c8c;
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
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #8c8c8c;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #595959;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel {
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-submit {
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #ff4d4f;
  font-size: 14px;
  margin-bottom: 16px;
}

.btn-delete-confirm {
  padding: 8px 16px;
  background: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
</style>
