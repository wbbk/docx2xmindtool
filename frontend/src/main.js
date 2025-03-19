import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'

const app = createApp(App)

// 配置axios默认值
axios.defaults.baseURL = 'http://localhost:5001'
axios.defaults.headers.common['Content-Type'] = 'application/json;charset=UTF-8'

// 添加请求拦截器
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

app.config.globalProperties.$axios = axios

app.use(router)
app.use(ElementPlus)
app.mount('#app')