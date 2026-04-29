import request from '../utils/request'

export const getDocuments = () => {
    return request.get('/documents')
}

export const deleteDocument = (docId) => {
    return request.delete(`/documents/${docId}`)
}

export const chat = (data) => {
    return request.post('/chat', data)
}

export const deepDiscuss = (data) => {
    return request.post('/chat/deep_discuss', data)
}