<template>
  <div class="roles-page">
    <h1 class="page-title">角色权限</h1>
    <p class="page-desc">配置各角色可访问的权限模块</p>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else class="roles-list">
      <div v-for="role in roles" :key="role.id" class="role-card">
        <div class="role-header">
          <h2 class="role-name">{{ role.name }}</h2>
          <span class="role-desc">{{ role.description || '-' }}</span>
        </div>
        <div class="perm-grid">
          <label
            v-for="perm in permissions"
            :key="perm.id"
            class="perm-item"
          >
            <input
              type="checkbox"
              :checked="role.permission_ids.includes(perm.id)"
              @change="togglePerm(role, perm.id)"
            />
            <span>{{ perm.name }}</span>
          </label>
        </div>
        <div class="role-actions">
          <button
            class="btn-save"
            :disabled="saving[role.id]"
            @click="saveRole(role)"
          >
            {{ saving[role.id] ? '保存中...' : '保存' }}
          </button>
          <span v-if="message[role.id]" :class="['msg', success[role.id] ? 'success' : 'error']">
            {{ message[role.id] }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const roles = ref([])
const permissions = ref([])
const loading = ref(true)
const saving = ref({})
const message = ref({})
const success = ref({})
const pendingChanges = ref({})

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    const [rolesRes, permsRes] = await Promise.all([
      api.get('/admin/roles'),
      api.get('/admin/permissions')
    ])
    roles.value = rolesRes.data
    permissions.value = permsRes.data
    pendingChanges.value = {}
  } catch (e) {
    console.error('加载失败:', e)
  } finally {
    loading.value = false
  }
}

function togglePerm(role, permId) {
  const key = role.id
  if (!pendingChanges.value[key]) {
    pendingChanges.value[key] = [...role.permission_ids]
  }
  const arr = pendingChanges.value[key]
  const idx = arr.indexOf(permId)
  if (idx >= 0) {
    arr.splice(idx, 1)
  } else {
    arr.push(permId)
  }
  role.permission_ids = [...arr]
}

async function saveRole(role) {
  saving.value[role.id] = true
  message.value[role.id] = ''
  try {
    await api.put(`/admin/roles/${role.id}/permissions`, {
      permission_ids: role.permission_ids
    })
    message.value[role.id] = '保存成功'
    success.value[role.id] = true
    pendingChanges.value[role.id] = undefined
    setTimeout(() => {
      message.value[role.id] = ''
    }, 3000)
  } catch (e) {
    message.value[role.id] = e.response?.data?.detail || '保存失败'
    success.value[role.id] = false
  } finally {
    saving.value[role.id] = false
  }
}
</script>

<style scoped>
.roles-page {
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

.loading {
  text-align: center;
  padding: 48px;
  color: #8c8c8c;
}

.roles-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.role-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
}

.role-header {
  margin-bottom: 20px;
}

.role-name {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 4px 0;
}

.role-desc {
  font-size: 13px;
  color: #8c8c8c;
}

.perm-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.perm-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #595959;
  cursor: pointer;
}

.perm-item input {
  width: 16px;
  height: 16px;
}

.role-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-save {
  padding: 8px 20px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-save:hover:not(:disabled) {
  background: #40a9ff;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.msg {
  font-size: 14px;
}

.msg.success {
  color: #52c41a;
}

.msg.error {
  color: #ff4d4f;
}
</style>
