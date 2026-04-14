import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

request.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data && data.data !== undefined) {
      return data.data
    }
    return data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export function getDashboardStats() {
  return request.get('/inspections/stats')
}

export function getInspections(params) {
  return request.get('/inspections', { params })
}

export function createInspection(data) {
  return request.post('/inspections', data)
}

export function getInspectionDetail(id) {
  return request.get(`/inspections/${id}`)
}

export function cancelInspection(id) {
  return request.post(`/inspections/${id}/cancel`)
}

export function batchInspection(data) {
  return request.post('/inspections/batch', data)
}

export function getDatabases() {
  return request.get('/databases')
}

export function createDatabase(data) {
  return request.post('/databases', data)
}

export function updateDatabase(id, data) {
  return request.put(`/databases/${id}`, data)
}

export function deleteDatabase(id) {
  return request.delete(`/databases/${id}`)
}

export function testConnection(id) {
  return request.post(`/databases/${id}/test`)
}

export function getReports() {
  return request.get('/reports')
}

export function downloadReport(id) {
  return request.get(`/reports/${id}/download`, {
    responseType: 'blob'
  })
}

export default request