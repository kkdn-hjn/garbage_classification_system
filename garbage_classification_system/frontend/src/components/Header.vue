<template>
  <div class="header-container">
    <div class="header-left">
      <button class="collapse-btn" @click="$emit('toggle-sidebar')" title="收起/展开">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
        <line x1="3" y1="12" x2="21" y2="12"/>
        <line x1="3" y1="6" x2="21" y2="6"/>
        <line x1="3" y1="18" x2="21" y2="18"/>
      </svg>
      </button>
      <div class="breadcrumb">
        <span class="breadcrumb-item">首页</span>
        <span v-if="breadcrumb" class="breadcrumb-sep">/</span>
        <span v-if="breadcrumb" class="breadcrumb-item">{{ breadcrumb }}</span>
      </div>
    </div>
    <div class="header-right">
      <div class="user-area">
        <div class="avatar">
          {{ user?.username?.charAt(0) || '?' }}
        </div>
        <div class="user-detail">
          <span class="username">{{ user?.username }}</span>
          <span class="user-id">ID: {{ shortId }}</span>
        </div>
      </div>
      <button class="logout-btn" @click="handleLogout">退出</button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

defineEmits(['toggle-sidebar'])

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUser()
  }
})

const user = computed(() => authStore.user)

const shortId = computed(() => {
  const u = authStore.user
  if (!u) return '-'
  return String(u.id || u.username || '').slice(0, 8)
})

const breadcrumb = computed(() => {
  return route.meta?.title || ''
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.header-container {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 999;
}

.collapse-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  color: #595959;
}

.collapse-btn:hover {
  color: #1890ff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.breadcrumb-item {
  color: #595959;
}

.breadcrumb-sep {
  color: #8c8c8c;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #1890ff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
}

.user-detail {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.user-id {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 2px;
}

.logout-btn {
  padding: 6px 14px;
  background: #fff;
  color: #595959;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.logout-btn:hover {
  color: #1890ff;
  border-color: #1890ff;
}
</style>
