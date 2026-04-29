import { defineStore } from 'pinia'

// 从 localStorage 恢复会话记录
const savedSessions = JSON.parse(localStorage.getItem('documind_sessions') || '[]')
const savedCurrentId = localStorage.getItem('documind_current_id') || null

export const useChatStore = defineStore('chat', {
    state: () => ({
        sessions: savedSessions, // List of sessions: { id, title, messages: [] }
        currentSessionId: savedCurrentId,
        selectedDoc: null,
        useDeepDiscuss: false,
        documents: [],
        currentReferences: [],
    }),
    getters: {
        currentSession: (state) => state.sessions.find(s => s.id === state.currentSessionId),
        currentMessages(state) {
            return this.currentSession ? this.currentSession.messages : []
        }
    },
    actions: {
        _saveToLocal() {
            localStorage.setItem('documind_sessions', JSON.stringify(this.sessions))
            localStorage.setItem('documind_current_id', this.currentSessionId || '')
        },
        setDocuments(docs) {
            this.documents = docs
        },
        startNewSession() {
            const newId = Date.now().toString()
            this.sessions.push({
                id: newId,
                title: `新对话\u00A0${new Date().toLocaleTimeString()}`,
                messages: []
            })
            this.currentSessionId = newId
            this.currentReferences = []
            this._saveToLocal()
        },
        switchSession(id) {
            this.currentSessionId = id
            this.currentReferences = [] // clear refs on switch
            this._saveToLocal()
        },
        addMessage(message) {
            if (!this.currentSessionId) {
                this.startNewSession()
            }
            this.currentSession.messages.push(message)
            // auto update title based on first user message if it's the default
            if (this.currentSession.messages.length === 1 && message.role === 'user') {
                this.currentSession.title = message.content.substring(0, 15) + (message.content.length > 15 ? '...' : '')
            }
            this._saveToLocal()
        },
        updateLastMessage(content, sourceDocs = []) {
            if (this.currentSession && this.currentSession.messages.length > 0) {
                const lastMsg = this.currentSession.messages[this.currentSession.messages.length - 1]
                lastMsg.loading = false
                lastMsg.content = content
            }
            this.currentReferences = sourceDocs || []
            this._saveToLocal()
        },
        updateSessionIdFromServer(realSessionId) {
            if (!this.currentSession) return
            this.currentSession.id = realSessionId
            this.currentSessionId = realSessionId
            this._saveToLocal()
        }
    }
})