<template>
  <div class="versions-page">
    <div class="page-header">
      <h1 class="page-title">模型版本管理</h1>
    </div>

    <div class="table-card">
      <h3 class="section-title">模型版本列表</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>模型</th>
            <th>版本</th>
            <th>准确率</th>
            <th>F1 分数</th>
            <th>创建时间</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="v in versions" :key="v.id">
            <td><strong>{{ v.model }}</strong></td>
            <td>{{ v.version }}</td>
            <td>{{ v.accuracy }}</td>
            <td>{{ v.f1 }}</td>
            <td>{{ v.created }}</td>
            <td>
              <span class="status-badge" :class="v.current ? 'current' : ''">
                {{ v.current ? '当前使用' : '历史版本' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      <p class="table-hint">MobileNetV2 为当前识别服务使用模型，支持切换版本回滚。</p>
    </div>
  </div>
</template>

<script setup>
const versions = [
  { id: 1, model: 'MobileNetV2', version: 'v1.0', accuracy: '96.82%', f1: '96.15%', created: '2024-12-01', current: true },
  { id: 2, model: 'ResNet50', version: 'v1.0', accuracy: '95.34%', f1: '94.92%', created: '2024-11-28', current: false }
]
</script>

<style scoped>
.versions-page {
  min-height: 100%;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0;
}

.table-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 20px 0;
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

.data-table tr:hover {
  background: #fafafa;
}

.status-badge {
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  background: #f0f0f0;
  color: #8c8c8c;
}

.status-badge.current {
  background: #e6f7ff;
  color: #1890ff;
}

.table-hint {
  font-size: 13px;
  color: #8c8c8c;
  margin: 20px 0 0 0;
}
</style>
