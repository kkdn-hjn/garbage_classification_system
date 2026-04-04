<template>
  <div class="sidebar-container" :class="{ collapsed: collapsed }">
    <div class="logo-area">
      <div class="logo-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7" rx="1"/>
          <rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/>
          <rect x="14" y="14" width="7" height="7" rx="1"/>
        </svg>
      </div>
      <div v-if="!collapsed" class="logo-text">
        <span class="logo-title">垃圾分类识别系统</span>
        <span class="logo-sub">后台管理</span>
      </div>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/dashboard" class="nav-item" :class="{ active: route.path === '/dashboard' || route.path === '/dashboard/' }">
        <span class="nav-icon" v-html="icons.dashboard"></span>
        <span v-if="!collapsed" class="nav-title">首页</span>
      </router-link>

      <div v-for="group in menuGroups" :key="group.key" class="nav-group">
        <div
          class="nav-parent"
          :class="{ active: isGroupActive(group), expanded: expandedKeys.includes(group.key) }"
          @click="toggleGroup(group.key)"
        >
          <span class="nav-icon" v-html="group.icon"></span>
          <span v-if="!collapsed" class="nav-title">{{ group.title }}</span>
          <span v-if="!collapsed" class="nav-arrow">{{ expandedKeys.includes(group.key) ? '▼' : '▶' }}</span>
        </div>
        <div v-if="expandedKeys.includes(group.key) && !collapsed" class="submenu">
          <router-link
            v-for="item in group.children"
            :key="item.path"
            :to="item.path"
            class="nav-item nav-child"
            :class="{ active: isActiveRoute(item.path) }"
          >
            <span class="nav-title">{{ item.title }}</span>
          </router-link>
        </div>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

defineProps({
  collapsed: { type: Boolean, default: false }
})

const route = useRoute()
const authStore = useAuthStore()
const expandedKeys = ref(['data', 'model', 'service', 'recognize', 'system'])

const icons = {
  dashboard: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="10" width="7" height="8" rx="1"/><rect x="3" y="14" width="7" height="4" rx="1"/></svg>',
  data: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/></svg>',
  model: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/></svg>',
  service: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>',
  recognize: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>',
  system: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
}

const menuGroups = computed(() => {
  const sysPerms = ['user_manage', 'role_manage', 'system_logs', 'system_settings']
  const showSystem = sysPerms.some((p) => authStore.hasPermission(p))
  const groups = [
    {
      key: 'data',
      title: '数据管理',
      icon: icons.data,
      children: [
        { path: '/dashboard/data/collect', title: '数据采集' },
        { path: '/dashboard/data/images', title: '垃圾图片管理' },
        { path: '/dashboard/data/categories', title: '垃圾类别管理' },
        { path: '/dashboard/data/statistics', title: '数据集统计' }
      ]
    },
    {
      key: 'model',
      title: '模型管理',
      icon: icons.model,
      children: [
        { path: '/dashboard/model/list', title: '模型列表' },
        { path: '/dashboard/model/evaluation', title: '模型评估' },
        { path: '/dashboard/model/versions', title: '模型版本管理' }
      ]
    },
    {
      key: 'service',
      title: '服务管理',
      icon: icons.service,
      children: [
        { path: '/dashboard/service/status', title: '识别服务状态' },
        { path: '/dashboard/service/api-logs', title: 'API调用记录' },
        { path: '/dashboard/service/config', title: '服务配置' }
      ]
    },
    {
      key: 'recognize',
      title: '识别测试',
      icon: icons.recognize,
      children: [
        { path: '/dashboard/recognize/test', title: '在线图片识别' },
        { path: '/dashboard/recognize/history', title: '识别历史记录' }
      ]
    },
    ...(showSystem ? [{
      key: 'system',
      title: '系统管理',
      icon: icons.system,
      children: [
        { path: '/dashboard/system/users', title: '用户管理' },
        { path: '/dashboard/system/roles', title: '角色权限' },
        { path: '/dashboard/system/logs', title: '操作日志' },
        { path: '/dashboard/system/settings', title: '系统设置' }
      ]
    }] : [])
  ]
  return groups
})

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUser()
  }
  ensureActiveGroupExpanded()
})

watch(() => route.path, () => ensureActiveGroupExpanded())

function ensureActiveGroupExpanded() {
  const path = route.path
  for (const g of menuGroups.value) {
    if (g.children.some(c => path.startsWith(c.path))) {
      if (!expandedKeys.value.includes(g.key)) {
        expandedKeys.value = [...expandedKeys.value, g.key]
      }
      break
    }
  }
}

function toggleGroup(key) {
  const idx = expandedKeys.value.indexOf(key)
  if (idx >= 0) {
    expandedKeys.value = expandedKeys.value.filter(k => k !== key)
  } else {
    expandedKeys.value = [...expandedKeys.value, key]
  }
}

function isGroupActive(group) {
  return group.children.some(c => route.path.startsWith(c.path))
}

function isActiveRoute(path) {
  return route.path === path || (path !== '/dashboard' && route.path.startsWith(path))
}
</script>

<style scoped>
.sidebar-container {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 220px;
  background: #fff;
  border-right: 1px solid #e8e8e8;
  transition: width 0.3s;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-container.collapsed {
  width: 72px;
}

.logo-area {
  height: 64px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  border-bottom: 1px solid #f0f0f0;
}

.logo-icon {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  color: #1890ff;
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.logo-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.logo-title {
  font-size: 15px;
  font-weight: 600;
  color: #262626;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logo-sub {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 2px;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-group {
  margin-bottom: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: #595959;
  text-decoration: none;
  transition: all 0.2s;
}

.nav-item:hover {
  background: #e6f7ff;
  color: #1890ff;
}

.nav-item.active {
  background: #e6f7ff;
  color: #1890ff;
}

.nav-parent {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: #595959;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-parent:hover {
  background: #e6f7ff;
  color: #1890ff;
}

.nav-parent.active {
  color: #1890ff;
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-right: 12px;
}

.nav-icon :deep(svg) {
  width: 100%;
  height: 100%;
}

.nav-title {
  font-size: 14px;
  white-space: nowrap;
  flex: 1;
}

.nav-arrow {
  font-size: 10px;
  color: #8c8c8c;
}

.submenu {
  background: #fafafa;
  overflow: hidden;
}

.nav-child {
  padding-left: 48px;
  font-size: 13px;
}

.nav-child .nav-icon {
  display: none;
}

.sidebar-container.collapsed .nav-title,
.sidebar-container.collapsed .nav-arrow,
.sidebar-container.collapsed .submenu {
  display: none;
}

.sidebar-container.collapsed .nav-parent {
  justify-content: center;
  padding: 12px;
}

.sidebar-container.collapsed .nav-parent .nav-icon {
  margin-right: 0;
}

.sidebar-container.collapsed .logo-text {
  display: none;
}

.sidebar-container.collapsed .logo-area {
  justify-content: center;
}
</style>
