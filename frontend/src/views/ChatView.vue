<template>
  <div class="chat-view">
    <div class="sidebar">
      <div class="config-panel">
        <h3>对话配置</h3>
        <el-form label-position="top">
          <el-form-item label="选择文档 (可选, 用于RAG上下文)">
            <el-select v-model="selectedDoc" placeholder="请选择文档" clearable>
              <el-option
                v-for="doc in documents"
                :key="doc.doc_id"
                :label="doc.filename"
                :value="doc.doc_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="使用深度研讨 (Agent)">
            <el-switch v-model="useDeepDiscuss" />
          </el-form-item>
          <el-button @click="startNewSession">新对话</el-button>
        </el-form>
      </div>

      <div class="references-panel" v-if="currentReferences && currentReferences.length">
        <h3>参考引用</h3>
        <ul class="ref-list">
          <li v-for="(ref, index) in currentReferences" :key="index">
            <div class="ref-title">{{ ref.metadata?.filename || 'Unknown' }}</div>
            <div class="ref-content">{{ ref.page_content }}</div>
          </li>
        </ul>
      </div>
    </div>

    <div class="chat-main">
      <div class="messages" ref="messagesRef">
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          :class="['message', msg.role]"
        >
          <div class="bubble">
            <span v-if="msg.content" class="content">{{ msg.content }}</span>
            <el-icon v-if="msg.loading" class="is-loading"><Loading /></el-icon>
          </div>
        </div>
      </div>
      
      <div class="input-area">
        <el-input
          v-model="inputQuery"
          type="textarea"
          :rows="3"
          placeholder="输入您的问题..."
          @keyup.enter.native="handleSend"
        />
        <el-button type="primary" class="send-btn" @click="handleSend" :loading="sending">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { getDocuments, chat, deepDiscuss } from '../api/index'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const documents = ref([])
const selectedDoc = ref(null)
const useDeepDiscuss = ref(false)

const messages = ref([])
const inputQuery = ref('')
const sending = ref(false)
const sessionId = ref(null)
const currentReferences = ref([])
const messagesRef = ref(null)

const fetchDocuments = async () => {
  try {
    const res = await getDocuments()
    if (res.code === 200) {
      documents.value = res.data.documents
    }
  } catch (error) {
    console.error(error)
  }
}

const startNewSession = () => {
  sessionId.value = null
  messages.value = []
  currentReferences.value = []
  ElMessage.success('已开启新回话')
}

const handleSend = async () => {
  if (!inputQuery.value.trim() || sending.value) return

  const query = inputQuery.value.trim()
  messages.value.push({ role: 'user', content: query })
  inputQuery.value = ''
  
  messages.value.push({ role: 'assistant', content: '', loading: true })
  sending.value = true

  scrollToBottom()

  try {
    const payload = {
      query: query,
      session_id: sessionId.value,
      doc_id: selectedDoc.value || null
    }

    let res;
    if (useDeepDiscuss.value) {
      res = await deepDiscuss(payload)
    } else {
      res = await chat(payload)
    }

    if (res.code === 200) {
      sessionId.value = res.data.session_id
      
      // Update the last assistant message
      const lastMsg = messages.value[messages.value.length - 1]
      lastMsg.loading = false
      lastMsg.content = res.data.answer

      if (res.data.source_documents) {
        currentReferences.value = res.data.source_documents
      } else {
        currentReferences.value = []
      }
    } else {
      messages.value.pop()
      ElMessage.error(res.message || 'Error occurred')
    }
  } catch (error) {
    messages.value.pop()
    ElMessage.error('网络或服务器错误')
  } finally {
    sending.value = false
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.chat-view {
  display: flex;
  height: 100%;
  gap: 20px;
}
.sidebar {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  border-right: 1px solid #eee;
  padding-right: 20px;
}
.config-panel {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}
.references-panel {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}
.ref-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.ref-list li {
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ddd;
}
.ref-title {
  font-weight: bold;
  font-size: 12px;
  color: #666;
}
.ref-content {
  font-size: 12px;
  color: #333;
  margin-top: 5px;
  white-space: pre-wrap;
  word-break: break-all;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}
.message {
  display: flex;
  margin-bottom: 20px;
}
.message.user {
  justify-content: flex-end;
}
.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
.message.user .bubble {
  background: #409eff;
  color: #fff;
  border-top-right-radius: 2px;
}
.message.assistant .bubble {
  background: #fff;
  color: #333;
  border-top-left-radius: 2px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}
.input-area {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}
.send-btn {
  height: 75px; /* match textarea roughly */
}
</style>