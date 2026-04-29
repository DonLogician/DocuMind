<template>
  <div class="chat-view">
    <!-- Left Sidebar: Chat History -->
    <div class="sidebar history-panel">
      <div class="sidebar-header">
        <el-button type="primary" @click="chatStore.startNewSession" style="width: 100%">
          <el-icon><Plus /></el-icon> 新对话
        </el-button>
      </div>
      <div class="session-list">
        <div 
          v-for="session in chatStore.sessions" 
          :key="session.id"
          :class="['session-item', { active: session.id === chatStore.currentSessionId }]"
          @click="chatStore.switchSession(session.id)"
        >
          <el-icon><ChatLineRound /></el-icon>
          <span class="session-title">{{ session.title }}</span>
        </div>
      </div>
    </div>

    <!-- Center: Chat Main Area (Standard LLM Interface) -->
    <div class="chat-main">
      <div class="messages" ref="messagesRef">
        <div 
          v-for="(msg, index) in chatStore.currentMessages" 
          :key="index" 
          :class="['message-row', msg.role]"
        >
          <div class="avatar">
            <el-avatar :size="36" v-if="msg.role === 'assistant'" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
            <el-avatar :size="36" v-else icon="UserFilled" />
          </div>
          <div class="message-content">
            <!-- Assistant: Markdown Rendering -->
            <div v-if="msg.role === 'assistant' && msg.content" class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
            <!-- User: Normal Text -->
            <span v-else-if="msg.content" class="text">{{ msg.content }}</span>
            
            <div v-if="msg.loading" class="loading-indicator">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
          </div>
        </div>
        <!-- Placeholder info if no messages -->
        <div v-if="chatStore.currentMessages.length === 0" class="empty-state">
          <h3>欢迎使用 DocuMind</h3>
          <p>请在右侧配置对话参数，然后在此输入问题。</p>
        </div>
      </div>
      
      <div class="input-container">
        <div class="input-wrapper">
          <el-input
            v-model="inputQuery"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 6 }"
            placeholder="在此输入您的消息..."
            @keyup.enter.native.exact="handleSend"
            class="chat-input"
          />
          <el-button type="primary" circle class="send-btn" @click="handleSend" :disabled="sending || !inputQuery.trim()">
            <el-icon><Position /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Right Sidebar: Configuration & References -->
    <div class="sidebar right-panel">
      <div class="config-panel">
        <h3>对话配置</h3>
        <el-form label-position="top">
          <el-form-item label="选择文档 (提供上下文)">
            <el-select v-model="chatStore.selectedDoc" placeholder="请选择或留空" clearable>
              <el-option
                v-for="doc in chatStore.documents"
                :key="doc.doc_id"
                :label="doc.filename"
                :value="doc.doc_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="深度研讨模式 (Agent)">
            <el-switch v-model="chatStore.useDeepDiscuss" active-text="开" inactive-text="关" />
          </el-form-item>
        </el-form>
      </div>

      <div class="references-panel" v-if="chatStore.currentReferences.length > 0">
        <h3>参考引用</h3>
        <ul class="ref-list">
          <li v-for="(ref, index) in chatStore.currentReferences" :key="index">
            <div class="ref-title">{{ ref.metadata?.filename || '来源' }} (段落 {{ index + 1 }})</div>
            <div class="ref-content">{{ ref.page_content }}</div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { getDocuments, chat, deepDiscuss } from '../api/index'
import { Plus, ChatLineRound, UserFilled, Position } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useChatStore } from '../store/chat'
import { marked } from 'marked'

const chatStore = useChatStore()
const inputQuery = ref('')
const sending = ref(false)
const messagesRef = ref(null)

const renderMarkdown = (text) => {
  if (!text) return ''
  return marked.parse(text)
}

const fetchDocuments = async () => {
  try {
    const res = await getDocuments()
    if (res.code === 200) {
      chatStore.setDocuments(res.data.documents)
    }
  } catch (error) {
    console.error(error)
  }
}

const handleSend = async (e) => {
  // 阻止默认回车换行（如果需要换行应使用 Shift+Enter，由于监听了 .exact 此处直接发送）
  if (e && e.preventDefault) e.preventDefault()
  
  if (!inputQuery.value.trim() || sending.value) return

  const query = inputQuery.value.trim()
  chatStore.addMessage({ role: 'user', content: query })
  inputQuery.value = ''
  
  chatStore.addMessage({ role: 'assistant', content: '', loading: true })
  sending.value = true

  scrollToBottom()

  try {
    const payload = {
      query: query,
      session_id: chatStore.currentSessionId,
      doc_id: chatStore.selectedDoc || null
    }

    let res;
    if (chatStore.useDeepDiscuss) {
      res = await deepDiscuss(payload)
    } else {
      res = await chat(payload)
    }

    if (res.code === 200) {
      chatStore.updateSessionIdFromServer(res.data.session_id)
      chatStore.updateLastMessage(res.data.answer, res.data.source_documents || [])
    } else {
      chatStore.currentSession.messages.pop()
      ElMessage.error(res.message || '系统错误')
    }
  } catch (error) {
    chatStore.currentSession.messages.pop()
    ElMessage.error('网络或服务器异常')
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
  if (chatStore.sessions.length === 0) {
    chatStore.startNewSession()
  }
})
</script>

<style scoped>
.chat-view {
  display: flex;
  height: 100%;
  gap: 15px;
  background-color: var(--bg-color);
}

/* Sidebar General */
.sidebar {
  width: 260px;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  overflow: hidden;
}

/* Left Panel: History */
.history-panel .sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
}
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}
.session-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 10px;
  border-radius: 8px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s ease;
  margin-bottom: 5px;
}
.session-item:hover {
  background-color: #f5f5f5;
}
.session-item.active {
  background-color: var(--primary-light);
  color: var(--text-main);
  font-weight: 500;
}
.session-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

/* Center Panel: LLM Chat Main */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  position: relative;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}
.empty-state {
  text-align: center;
  margin: auto;
  color: #999;
}
.message-row {
  display: flex;
  gap: 15px;
  align-items: flex-start;
  max-width: 80%;
}
.message-row.user {
  margin-left: auto;
  flex-direction: row-reverse;
}
.message-row.assistant {
  margin-right: auto;
  max-width: 90%;
}
.message-content {
  padding: 12px 18px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}
.message-row.user .message-content {
  background-color: var(--bubble-user);
  color: var(--text-main);
  border-top-right-radius: 2px;
}
.message-row.assistant .message-content {
  background-color: transparent;
  color: #333;
  padding: 0; 
  padding-top: 8px; /* 稍微与头像对齐 */
}

/* Markdown 内部基础样式优化 */
.markdown-body :deep(p:first-child) {
  margin-top: 0;
}
.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}
.markdown-body :deep(pre), .markdown-body :deep(code) {
  background-color: #f6f8fa;
  border-radius: 6px;
  font-family: monospace;
}
.markdown-body :deep(pre) {
  padding: 16px;
  overflow: auto;
}
.markdown-body :deep(code) {
  padding: 0.2em 0.4em;
}

/* Input Area */
.input-container {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
}
.input-wrapper {
  position: relative;
  display: flex;
  align-items: flex-end;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 8px 12px;
  transition: border-color 0.2s;
}
.input-wrapper:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 1px var(--primary-light);
}
.chat-input :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none;
  padding: 0;
  padding-right: 40px;
  background: transparent;
  resize: none;
}
.chat-input :deep(.el-textarea__inner:focus) {
  box-shadow: none;
}
.send-btn {
  position: absolute;
  right: 12px;
  bottom: 12px;
}

/* Loading Dots */
.loading-indicator {
  display: flex;
  gap: 4px;
  padding: 5px 0;
}
.dot {
  width: 6px;
  height: 6px;
  background-color: #aaa;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Right Panel: Config & References */
.right-panel {
  padding: 20px;
}
.config-panel {
  margin-bottom: 20px;
}
.config-panel h3, .references-panel h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: var(--text-main);
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 10px;
}
.references-panel {
  flex: 1;
  overflow-y: auto;
}
.ref-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.ref-list li {
  background: #fdfdfd;
  border: 1px solid #eaeaea;
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 10px;
}
.ref-title {
  font-weight: bold;
  font-size: 12px;
  color: var(--primary-color);
  margin-bottom: 5px;
}
.ref-content {
  font-size: 12px;
  color: #555;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>