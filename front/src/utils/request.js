import axios from 'axios'
import { Message } from 'element-ui'
import { Toast } from 'vant'
import store from '@/store'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

function redirectToLogin() {
  const isMobile = window.location.pathname.startsWith('/m')
  const loginPath = isMobile ? '/m/login' : '/admin/login'
  store.dispatch('logout')
  if (router.currentRoute.path !== loginPath) {
    router.replace(loginPath).catch(() => {})
  }
}

request.interceptors.request.use(config => {
  const token = store.state.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  response => {
    const res = response.data
    if (response.config.responseType === 'blob') {
      return response
    }
    if (res.code !== 0) {
      if (res.code === 401) {
        redirectToLogin()
        return Promise.reject(Object.assign(new Error(res.message), { silent: true }))
      }
      const isMobile = window.location.pathname.startsWith('/m')
      if (isMobile) {
        Toast.fail(res.message || '请求失败')
      } else {
        Message.error(res.message || '请求失败')
      }
      return Promise.reject(new Error(res.message))
    }
    return res
  },
  error => {
    const isMobile = window.location.pathname.startsWith('/m')
    const code = error.response?.data?.code
    const msg = error.response?.data?.message || error.response?.data?.detail || '网络错误'
    if (code === 401 || error.response?.status === 401) {
      redirectToLogin()
      return Promise.reject(Object.assign(new Error(msg), { silent: true }))
    }
    if (isMobile) {
      Toast.fail(msg)
    } else {
      Message.error(msg)
    }
    return Promise.reject(error)
  }
)

export default request
