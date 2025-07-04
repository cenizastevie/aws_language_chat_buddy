import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Configure axios to include credentials for session management
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('❌ API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for debugging and error handling
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.message)
    
    // Handle specific error cases
    if (error.response?.status === 404) {
      console.error('API endpoint not found')
    } else if (error.response?.status >= 500) {
      console.error('Server error occurred')
    } else if (error.code === 'ECONNABORTED') {
      console.error('Request timeout')
    }
    
    return Promise.reject(error)
  }
)

export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Scenario management
  loadScenario: (scenarioPath) => 
    api.post('/load_scenario', { scenario_path: scenarioPath }),

  // Conversation flow
  getCurrentPrompt: () => api.get('/current_prompt'),
  
  submitStudentResponse: (response) => 
    api.post('/student_response', { student_response: response }),
  
  resetConversation: () => api.post('/reset'),
  
  getConversationState: () => api.get('/state'),

  // Session management
  clearSession: () => api.post('/session/clear'),
  
  getSessionInfo: () => api.get('/session/info'),
}

export default apiService
