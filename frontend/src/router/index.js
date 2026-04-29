import { createRouter, createWebHistory } from 'vue-router'
import DocumentView from '../views/DocumentView.vue'
import ChatView from '../views/ChatView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            redirect: '/documents'
        },
        {
            path: '/documents',
            name: 'documents',
            component: DocumentView
        },
        {
            path: '/chat',
            name: 'chat',
            component: ChatView
        }
    ]
})

export default router