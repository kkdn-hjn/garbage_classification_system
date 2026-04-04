<template>
  <div class="data-images-page">
    <h1 class="page-title">垃圾图片管理</h1>

    <div class="toolbar">
      <div class="upload-area" @click="triggerUpload" @dragover.prevent @drop.prevent="onDrop">
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          multiple
          @change="onFileSelect"
        />
        <span class="upload-text">点击上传图片</span>
      </div>
      <div class="upload-area folder-area" @click="triggerFolderUpload" @dragover.prevent @drop.prevent="onDrop">
        <input
          ref="folderInput"
          type="file"
          accept="image/*"
          multiple
          webkitdirectory
          directory
          @change="onFolderSelect"
        />
        <span class="upload-text">选择文件夹上传<br><small>文件夹名即分类（纸类、塑料等）</small></span>
      </div>
      <div class="filter-row">
        <span class="filter-label">筛选：</span>
        <select v-model="filterCategory" @change="loadImages" class="filter-select">
          <option value="">全部分类</option>
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
        <span class="filter-label">上传分类：</span>
        <select v-model="uploadCategory" class="filter-select">
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
        <button class="btn-refresh" @click="loadImages">刷新</button>
      </div>
    </div>

    <div v-if="uploading" class="uploading-hint">上传中...</div>

    <div class="images-grid" v-if="!loading && images.length > 0">
      <div v-for="img in images" :key="img.id" class="image-card">
        <div class="image-wrap">
          <img :src="imageUrl(img)" :alt="img.filename" referrerpolicy="no-referrer" @error="onImgError" />
        </div>
        <div class="image-info">
          <select
            v-model="img.category"
            class="category-select"
            @change="updateCategory(img)"
          >
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
          <span class="image-date">{{ formatDate(img.created_at) }}</span>
        </div>
        <button class="btn-delete" @click="confirmDelete(img)" title="删除">删除</button>
      </div>
    </div>

    <div v-else-if="loading" class="loading">加载中...</div>
    <div v-else class="empty">暂无图片，请上传</div>

    <div class="pagination" v-if="total > pageSize">
      <button class="page-btn" @click="prevPage" :disabled="currentPage <= 1">上一页</button>
      <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页，共 {{ total }} 张</span>
      <button class="page-btn" @click="nextPage" :disabled="currentPage >= totalPages">下一页</button>
    </div>

    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal-content" @click.stop>
        <p>确定删除该图片吗？</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showDeleteModal = false">取消</button>
          <button class="btn-confirm" @click="doDelete" :disabled="deleting">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

const fileInput = ref(null)
const folderInput = ref(null)
const images = ref([])
const categories = ref([])
const loading = ref(false)
const uploading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const filterCategory = ref('')
const uploadCategory = ref('其他')
const showDeleteModal = ref(false)
const deleting = ref(false)
const imageToDelete = ref(null)

const totalPages = ref(1)

onMounted(() => {
  loadCategories()
  loadImages()
})

function imageUrl(img) {
  if (!img || !img.id) return ''
  const auth = useAuthStore()
  const token = auth.token ? `?token=${encodeURIComponent(auth.token)}` : ''
  return `/api/data/images/file/${img.id}${token}`
}

function onImgError(e) {
  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" fill="%23ddd"><rect width="100" height="100"/><text x="50" y="50" text-anchor="middle" dy=".3em" fill="%23999" font-size="12">加载失败</text></svg>'
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('zh-CN')
}

async function loadCategories() {
  try {
    const res = await api.get('/data/images/categories')
    categories.value = res.data.categories || []
  } catch (e) {
    categories.value = ['纸类', '塑料', '玻璃', '金属', '织物', '厨余', '有害', '可回收物', '电池', '灯管', '药品', '其他']
  }
}

async function loadImages() {
  loading.value = true
  try {
    const params = { skip: (currentPage.value - 1) * pageSize, limit: pageSize }
    if (filterCategory.value) params.category = filterCategory.value
    const res = await api.get('/data/images', { params })
    images.value = res.data.images
    total.value = res.data.total
    totalPages.value = Math.ceil(total.value / pageSize) || 1
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function triggerUpload() {
  fileInput.value?.click()
}

function triggerFolderUpload() {
  folderInput.value?.click()
}

function onFileSelect(e) {
  const files = e.target.files
  if (files?.length) uploadFiles(Array.from(files), null)
  e.target.value = ''
}

function onFolderSelect(e) {
  const files = Array.from(e.target.files || []).filter(f => /\.(jpg|jpeg|png|gif|webp|bmp)$/i.test(f.name))
  if (files.length) uploadFiles(files, true)
  e.target.value = ''
}

function onDrop(e) {
  const files = e.dataTransfer?.files
  if (files?.length) uploadFiles(Array.from(files).filter(f => f.type.startsWith('image/')), null)
}

async function uploadFiles(files, fromFolder) {
  if (!files.length) return
  uploading.value = true
  let ok = 0
  for (const f of files) {
    try {
      const fd = new FormData()
      fd.append('file', f)
      fd.append('category', uploadCategory.value || '其他')
      if (fromFolder && f.webkitRelativePath) {
        fd.append('rel_path', f.webkitRelativePath)
      }
      await api.post('/data/images/upload', fd)
      ok++
    } catch (e) {
      console.error('Upload fail:', f.name, e)
    }
  }
  uploading.value = false
  if (ok) loadImages()
}

async function updateCategory(img) {
  try {
    await api.put(`/data/images/${img.id}`, { category: img.category })
  } catch (e) {
    console.error(e)
  }
}

function confirmDelete(img) {
  imageToDelete.value = img
  showDeleteModal.value = true
}

async function doDelete() {
  if (!imageToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/data/images/${imageToDelete.value.id}`)
    showDeleteModal.value = false
    imageToDelete.value = null
    loadImages()
  } catch (e) {
    console.error(e)
  } finally {
    deleting.value = false
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    loadImages()
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadImages()
  }
}
</script>

<style scoped>
.data-images-page {
  min-height: 100%;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 24px 0;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
  margin-bottom: 24px;
}

.upload-area {
  flex: 1;
  min-width: 200px;
  height: 100px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
}

.upload-area:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.upload-area input {
  display: none;
}

.upload-text {
  font-size: 14px;
  color: #8c8c8c;
}

.upload-text small {
  display: block;
  font-size: 12px;
  margin-top: 4px;
  opacity: 0.8;
}

.folder-area {
  border-style: dotted;
}

.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-label {
  font-size: 14px;
  color: #666;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  min-width: 120px;
}

.btn-refresh {
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-refresh:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.uploading-hint {
  margin-bottom: 16px;
  font-size: 14px;
  color: #1890ff;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}

.image-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
  overflow: hidden;
  position: relative;
}

.image-wrap {
  aspect-ratio: 1;
  background: #f5f5f5;
  overflow: hidden;
}

.image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-info {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-select {
  padding: 6px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
}

.image-date {
  font-size: 12px;
  color: #8c8c8c;
}

.btn-delete {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  background: rgba(0,0,0,0.6);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-delete:hover {
  background: #ff4d4f;
}

.loading,
.empty {
  text-align: center;
  padding: 48px;
  color: #8c8c8c;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.page-btn {
  padding: 6px 14px;
  border: 1px solid #d9d9d9;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  min-width: 320px;
}

.modal-content p {
  margin: 0 0 20px 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm {
  padding: 8px 16px;
  background: #ff4d4f;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm:disabled {
  opacity: 0.6;
}
</style>
