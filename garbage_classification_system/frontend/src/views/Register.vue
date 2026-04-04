<template>
  <div class="register-wrapper">
    <div class="register-left">
      <div class="geometric-bg">
        <div class="shape circle-1"></div>
        <div class="shape circle-2"></div>
        <div class="shape pentagon"></div>
      </div>
      <h1 class="brand-title">基于百度智能云的垃圾分类识别系统</h1>
    </div>
    <div class="register-right">
      <div class="form-container">
        <h2 class="form-title">注册页</h2>
        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              placeholder="请输入用户名"
              required
            />
          </div>
          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="请输入邮箱"
              required
            />
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              required
            />
          </div>
          <div class="form-group">
            <label for="confirmPassword">确认密码</label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              required
            />
          </div>
          <button type="submit" class="register-button" :disabled="loading">
            {{ loading ? '注册中...' : '注册' }}
          </button>
          <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
          <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
        </form>
        <div class="login-link">
          已有账号？<router-link to="/login">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

async function handleRegister() {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  if (form.value.password !== form.value.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    loading.value = false
    return
  }
  if (form.value.password.length < 6) {
    errorMessage.value = '密码长度至少为6位'
    loading.value = false
    return
  }
  const result = await authStore.register({
    username: form.value.username,
    email: form.value.email,
    password: form.value.password
  })
  if (result.success) {
    successMessage.value = '注册成功！正在跳转到登录页面...'
    setTimeout(() => router.push('/login'), 1500)
  } else {
    errorMessage.value = result.message
  }
  loading.value = false
}
</script>

<style scoped>
.register-wrapper {
  display: flex;
  min-height: 100vh;
}

.register-left {
  flex: 0 0 65%;
  background: #1a2b4b;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.geometric-bg {
  position: absolute;
  inset: 0;
}

.shape {
  position: absolute;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.circle-1 {
  width: 350px;
  height: 350px;
  border-radius: 50%;
  background: rgba(26, 43, 75, 0.5);
  top: -80px;
  right: -80px;
}

.circle-2 {
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: rgba(35, 55, 90, 0.4);
  bottom: 15%;
  left: 10%;
}

.pentagon {
  width: 150px;
  height: 150px;
  clip-path: polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%);
  background: rgba(55, 85, 130, 0.25);
  top: 25%;
  left: 25%;
}

.brand-title {
  position: relative;
  z-index: 1;
  font-size: 30px;
  font-weight: 700;
  color: #fff;
  text-align: center;
  max-width: 80%;
}

.register-right {
  flex: 0 0 35%;
  min-width: 380px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.form-container {
  width: 100%;
  max-width: 360px;
}

.form-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 28px;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #333;
  font-weight: 500;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #1890ff;
}

.register-button {
  background: #1890ff;
  color: #fff;
  border: none;
  padding: 14px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 8px;
}

.register-button:hover:not(:disabled) {
  background: #40a9ff;
}

.register-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #ff4d4f;
  font-size: 14px;
}

.success-message {
  color: #52c41a;
  font-size: 14px;
}

.login-link {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #666;
}

.login-link a {
  color: #1890ff;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
