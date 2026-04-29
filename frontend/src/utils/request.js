import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
    baseURL: '/api',
    timeout: 60000,
})

service.interceptors.request.use(
    config => config,
    error => Promise.reject(error)
)

service.interceptors.response.use(
    response => response.data,
    error => {
        ElMessage.error(error.response?.data?.detail || error.message || '请求失败')
        return Promise.reject(error)
    }
)

export default service