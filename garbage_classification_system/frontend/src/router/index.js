import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Layout from '../components/Layout.vue'
import Dashboard from '../views/Dashboard.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  {
    path: '/dashboard',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: Dashboard, meta: { title: '首页' } },
      // 数据管理
      {
        path: 'data/collect',
        name: 'DataCollect',
        component: () => import('../views/DataCollect.vue'),
        meta: { title: '数据采集' }
      },
      {
        path: 'data/images',
        name: 'DataImages',
        component: () => import('../views/DataImages.vue'),
        meta: { title: '垃圾图片管理' }
      },
      {
        path: 'data/categories',
        name: 'DataCategories',
        component: () => import('../views/DataCategories.vue'),
        meta: { title: '垃圾类别管理' }
      },
      {
        path: 'data/statistics',
        name: 'DataStatistics',
        component: () => import('../views/DataStatistics.vue'),
        meta: { title: '数据集统计' }
      },
      // 模型管理
      {
        path: 'model/list',
        name: 'ModelList',
        component: () => import('../views/ModelList.vue'),
        meta: { title: '模型列表' }
      },
      {
        path: 'model/evaluation',
        name: 'ModelEvaluation',
        component: () => import('../views/ModelEvaluation.vue'),
        meta: { title: '模型评估' }
      },
      {
        path: 'model/versions',
        name: 'ModelVersions',
        component: () => import('../views/ModelVersions.vue'),
        meta: { title: '模型版本管理' }
      },
      // 服务管理
      {
        path: 'service/status',
        name: 'ServiceStatus',
        component: () => import('../views/ServiceStatus.vue'),
        meta: { title: '识别服务状态' }
      },
      {
        path: 'service/api-logs',
        name: 'ServiceApiLogs',
        component: () => import('../views/ServiceApiLogs.vue'),
        meta: { title: 'API调用记录' }
      },
      {
        path: 'service/config',
        name: 'ServiceConfig',
        component: () => import('../views/ServiceConfigPage.vue'),
        meta: { title: '服务配置' }
      },
      // 识别测试
      {
        path: 'recognize/test',
        name: 'RecognizeTest',
        component: () => import('../views/RecognizeTest.vue'),
        meta: { title: '在线图片识别' }
      },
      {
        path: 'recognize/history',
        name: 'RecognizeHistory',
        component: () => import('../views/RecognizeHistory.vue'),
        meta: { title: '识别历史记录' }
      },
      // 系统管理
      {
        path: 'system/users',
        name: 'UserManagement',
        component: () => import('../views/UserManagement.vue'),
        meta: { title: '用户管理', requiresPermission: 'user_manage' }
      },
      {
        path: 'system/roles',
        name: 'SystemRoles',
        component: () => import('../views/RolePermissions.vue'),
        meta: { title: '角色权限', requiresPermission: 'role_manage' }
      },
      {
        path: 'system/logs',
        name: 'Admin',
        component: () => import('../views/Admin.vue'),
        meta: { title: '操作日志', requiresPermission: 'system_logs' }
      },
      {
        path: 'system/settings',
        name: 'SystemSettings',
        component: () => import('../views/SystemSettings.vue'),
        meta: { title: '系统设置', requiresPermission: 'system_settings' }
      },
      // 兼容旧路径
      { path: 'users', redirect: '/dashboard/system/users' },
      { path: 'admin', redirect: '/dashboard/system/logs' }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.path === '/login' || to.path === '/register') {
    next()
  } else {
    if (!authStore.isAuthenticated) {
      next('/login')
    } else if (to.meta.requiresPermission && !authStore.hasPermission(to.meta.requiresPermission)) {
      next('/dashboard')
    } else {
      next()
    }
  }
})

export default router
