<template>
  <div class="placeholder-page">
    <h1 class="page-title">{{ title }}</h1>
    <div class="placeholder-card">
      <p class="placeholder-desc">{{ description }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '页面' },
  description: { type: String, default: '' }
})
</script>

<style scoped>
.placeholder-page {
  min-height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 24px 0;
}

.placeholder-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 48px;
  text-align: center;
}

.placeholder-desc {
  font-size: 14px;
  color: #595959;
  margin-bottom: 12px;
}

.placeholder-hint {
  font-size: 13px;
  color: #8c8c8c;
}
</style>
