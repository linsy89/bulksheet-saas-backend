import axios from 'axios';

// 从环境变量获取API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// 创建axios实例
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000,  // 180秒超时（AI生成可能需要较长时间）
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response.data;
  },
  (error) => {
    console.error('Response Error:', error.response?.status, error.response?.data);

    // 统一错误处理
    const message = error.response?.data?.detail || error.message || '请求失败';

    return Promise.reject(new Error(message));
  }
);
