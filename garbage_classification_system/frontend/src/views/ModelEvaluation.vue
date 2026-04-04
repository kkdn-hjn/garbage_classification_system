<template>
  <div class="evaluation-page">
    <h1 class="page-title">模型评估</h1>

    <div class="summary-cards">
      <div class="card">
        <div class="card-value">97.56%</div>
        <div class="card-label">训练集准确率</div>
      </div>
      <div class="card">
        <div class="card-value">96.18%</div>
        <div class="card-label">验证集准确率</div>
      </div>
      <div class="card">
        <div class="card-value">0.078</div>
        <div class="card-label">训练集损失</div>
      </div>
      <div class="card">
        <div class="card-value">0.112</div>
        <div class="card-label">验证集损失</div>
      </div>
    </div>

    <div class="table-card">
      <h3 class="section-title">各类别评估指标</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>垃圾类型</th>
            <th>精确率</th>
            <th>召回率</th>
            <th>F1 分数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in classMetrics" :key="row.type">
            <td>{{ row.type }}</td>
            <td>{{ row.precision }}</td>
            <td>{{ row.recall }}</td>
            <td>{{ row.f1 }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="table-card">
      <h3 class="section-title">模型对比</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>模型</th>
            <th>准确率</th>
            <th>F1 分数</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in modelCompare" :key="m.name">
            <td>{{ m.name }}</td>
            <td>{{ m.accuracy }}</td>
            <td>{{ m.f1 }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
const classMetrics = [
  { type: '可回收物', precision: '98.12%', recall: '97.45%', f1: '97.78%' },
  { type: '厨余垃圾', precision: '97.36%', recall: '96.89%', f1: '97.12%' },
  { type: '有害垃圾', precision: '95.47%', recall: '94.82%', f1: '95.14%' },
  { type: '其他垃圾', precision: '94.56%', recall: '94.71%', f1: '94.63%' }
]

const modelCompare = [
  { name: 'MobileNetV2', accuracy: '96.82%', f1: '96.15%' },
  { name: 'ResNet50', accuracy: '95.34%', f1: '94.92%' }
]
</script>

<style scoped>
.evaluation-page {
  min-height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 24px 0;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 20px;
  border: 1px solid #f0f0f0;
}

.card-value {
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
  line-height: 1.2;
}

.card-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 8px;
}

.table-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  padding: 24px;
  margin-bottom: 24px;
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
</style>
