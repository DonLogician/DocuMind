<template>
  <div class="document-view">
    <div class="header">
      <h2>文档管理</h2>
      <el-upload
        class="upload-demo"
        action="/api/upload"
        :show-file-list="false"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
      >
        <el-button type="primary" :loading="uploading">上传文档</el-button>
      </el-upload>
    </div>

    <el-table :data="documents" style="width: 100%" v-loading="loading">
      <el-table-column prop="filename" label="文件名" />
      <el-table-column prop="extension" label="格式" width="120" />
      <el-table-column prop="chunks_count" label="分块数" width="120" />
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button type="danger" size="small" @click="handleDelete(scope.row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDocuments, deleteDocument } from '../api/index'

const documents = ref([])
const loading = ref(false)
const uploading = ref(false)

const fetchDocuments = async () => {
  loading.value = true
  try {
    const res = await getDocuments()
    if (res.code === 200) {
      documents.value = res.data.documents
    }
  } catch (error) {
    console.error('Failed to fetch documents', error)
  } finally {
    loading.value = false
  }
}

const beforeUpload = () => {
  uploading.value = true
  return true
}

const handleUploadSuccess = (res) => {
  uploading.value = false
  if (res.code === 200) {
    ElMessage.success('上传成功')
    fetchDocuments()
  } else {
    ElMessage.error(res.message || '上传失败')
  }
}

const handleUploadError = () => {
  uploading.value = false
  ElMessage.error('上传出错')
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除文档 ${row.filename} 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      const res = await deleteDocument(row.doc_id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        fetchDocuments()
      } else {
        ElMessage.error(res.message || '删除失败')
      }
    } catch (error) {
      console.error(error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.document-view {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>