import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
    state: () => ({
        sessions: [], // List of sessions: { id, title, messages: [] }
        currentSessionId: null,
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
        },
        switchSession(id) {
            this.currentSessionId = id
            this.currentReferences = [] // clear refs on switch
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
        },
        updateLastMessage(content, sourceDocs = []) {
            if (this.currentSession && this.currentSession.messages.length > 0) {
                const lastMsg = this.currentSession.messages[this.currentSession.messages.length - 1]
                lastMsg.loading = false
                lastMsg.content = content
            }
            this.currentReferences = sourceDocs || []
        },
        updateSessionIdFromServer(realSessionId) {
            if (!this.currentSession) return
            this.currentSession.id = realSessionId
            this.currentSessionId = realSessionId
        }
    }
})