<template>
  <div class="dashboard-page">
    <h1 class="page-title">首页</h1>
    <div class="welcome-card">
      <p class="welcome-text">欢迎, <strong>{{ user?.username }}</strong></p>
      <p v-if="user?.role === 1" class="role-desc">您拥有管理员权限，可以管理用户、查看操作记录。</p>
      <p v-else class="role-desc">您是普通用户。</p>
    </div>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🗑️</div>
        <div class="stat-content">
          <div class="stat-label">垃圾分类识别</div>
          <div class="stat-desc">基于百度智能云 AI 能力</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👤</div>
        <div class="stat-content">
          <div class="stat-label">当前用户</div>
          <div class="stat-desc">{{ user?.username }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const user = computed(() => authStore.user)

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
  } else {
    await authStore.fetchUser()
  }
})
</script>

<style scoped>
.dashboard-page {
  min-height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 24px 0;
}

.welcome-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
  margin-bottom: 20px;
}

.welcome-text {
  font-size: 16px;
  color: #595959;
}

.welcome-text strong {
  color: #1890ff;
}

.role-desc {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 40px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 8px;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 4px;
}

.stat-desc {
  font-size: 14px;
  color: #8c8c8c;
}
</style>
