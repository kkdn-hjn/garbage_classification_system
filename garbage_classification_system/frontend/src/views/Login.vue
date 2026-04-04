<template>
  <div class="login-wrapper">
    <div class="login-left">
      <div class="geometric-bg">
        <div class="shape circle-1"></div>
        <div class="shape circle-2"></div>
        <div class="shape circle-3"></div>
        <div class="shape pentagon"></div>
      </div>
      <h1 class="brand-title">基于百度智能云的垃圾分类识别系统</h1>
    </div>
    <div class="login-right">
      <div class="form-container">
        <h2 class="form-title">登录页</h2>
        <form @submit.prevent="handleLogin" class="login-form">
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
            <label for="password">密码</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              required
            />
          </div>
          <button type="submit" class="login-button" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
          <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        </form>
        <div class="register-link">
          还没有账号？<router-link to="/register">立即注册</router-link>
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
const form = ref({ username: '', password: '' })
const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  loading.value = true
  errorMessage.value = ''
  const result = await authStore.login(form.value.username, form.value.password)
  if (result.success) {
    router.push('/dashboard')
  } else {
    errorMessage.value = result.message
  }
  loading.value = false
}
</script>

<style scoped>
.login-wrapper {
  display: flex;
  min-height: 100vh;
}

.login-left {
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
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: rgba(26, 43, 75, 0.5);
  top: -100px;
  left: -100px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: rgba(35, 55, 90, 0.4);
  bottom: 10%;
  right: 15%;
}

.circle-3 {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(45, 70, 110, 0.3);
  top: 30%;
  right: 25%;
}

.pentagon {
  width: 180px;
  height: 180px;
  clip-path: polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%);
  background: rgba(55, 85, 130, 0.25);
  bottom: 20%;
  left: 20%;
}

.brand-title {
  position: relative;
  z-index: 1;
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  text-align: center;
  max-width: 80%;
  line-height: 1.5;
}

.login-right {
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
  margin-bottom: 32px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  padding: 12px 14px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #1890ff;
}

.login-button {
  background: #1890ff;
  color: #fff;
  border: none;
  padding: 14px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
  margin-top: 8px;
}

.login-button:hover:not(:disabled) {
  background: #40a9ff;
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #ff4d4f;
  font-size: 14px;
  text-align: center;
}

.register-link {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #666;
}

.register-link a {
  color: #1890ff;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
}

@media (max-width: 900px) {
  .login-wrapper {
    flex-direction: column;
  }
  .login-left {
    flex: none;
    min-height: 200px;
  }
  .login-right {
    flex: 1;
    min-width: auto;
  }
}
</style>
