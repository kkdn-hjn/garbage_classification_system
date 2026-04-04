<template>
  <div class="layout-container">
    <Sidebar :collapsed="sidebarCollapsed" />
    <div class="main-container" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <Header @toggle-sidebar="toggleSidebar" />
      <div class="app-main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'

const router = useRouter()
const authStore = useAuthStore()
const sidebarCollapsed = ref(false)

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
  } else if (!authStore.user) {
    await authStore.fetchUser()
  }
})

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 220px;
  transition: margin-left 0.3s;
  background: #f0f2f5;
}

.main-container.sidebar-collapsed {
  margin-left: 72px;
}

.app-main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
