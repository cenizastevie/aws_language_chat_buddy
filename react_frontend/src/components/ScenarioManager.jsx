import { useState, useEffect } from 'react'
import apiService from '../services/apiService'

const ScenarioManager = ({ onScenarioLoaded }) => {
  const [isLoading, setIsLoading] = useState(false)
  const [sessionInfo, setSessionInfo] = useState(null)
  const [backendHealth, setBackendHealth] = useState(null)
  const [availableScenarios] = useState([
    { 
      path: 'scenarios/friend.json', 
      name: 'Friend Conversation', 
      description: 'Practice casual conversation with a friend',
      emoji: '👥'
    },
    { 
      path: 'scenarios/weather.json', 
      name: 'Weather Talk', 
      description: 'Learn to discuss weather and climate',
      emoji: '🌤️'
    },
    // Add more scenarios as needed
  ])

  useEffect(() => {
    loadSessionInfo()
    checkHealth()
  }, [])

  const loadSessionInfo = async () => {
    try {
      const response = await apiService.getSessionInfo()
      setSessionInfo(response.data)
    } catch (error) {
      console.error('Error loading session info:', error)
    }
  }

  const checkHealth = async () => {
    try {
      const response = await apiService.healthCheck()
      setBackendHealth({ status: 'healthy', data: response.data })
    } catch (error) {
      console.error('Health check failed:', error)
      setBackendHealth({ status: 'unhealthy', error: error.message })
    }
  }

  const loadScenario = async (scenarioPath) => {
    setIsLoading(true)
    try {
      const response = await apiService.loadScenario(scenarioPath)
      console.log('Scenario loaded:', response.data)
      
      // Refresh session info
      await loadSessionInfo()
      
      // Notify parent component
      if (onScenarioLoaded) {
        onScenarioLoaded(response.data)
      }
      
      // Show success message
      alert(`✅ Scenario loaded successfully: ${response.data.scenario.scenario_name}`)
    } catch (error) {
      console.error('Error loading scenario:', error)
      alert('❌ Failed to load scenario. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const clearSession = async () => {
    setIsLoading(true)
    try {
      await apiService.clearSession()
      await loadSessionInfo()
      
      // Notify parent component
      if (onScenarioLoaded) {
        onScenarioLoaded(null)
      }
      
      alert('🗑️ Session cleared successfully!')
    } catch (error) {
      console.error('Error clearing session:', error)
      alert('❌ Failed to clear session. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleHealthCheck = async () => {
    setIsLoading(true)
    await checkHealth()
    setIsLoading(false)
    
    if (backendHealth?.status === 'healthy') {
      alert(`✅ Backend is healthy: ${backendHealth.data.status}`)
    } else {
      alert('❌ Backend health check failed. Please ensure the backend is running.')
    }
  }

  return (
    <div className="scenario-section">
      <h2>🎯 Scenario Management</h2>
      
      {/* Backend Health Status */}
      {backendHealth && (
        <div style={{ 
          marginBottom: '1rem', 
          padding: '0.5rem 1rem', 
          borderRadius: '8px',
          background: backendHealth.status === 'healthy' ? '#e8f5e8' : '#ffebee',
          color: backendHealth.status === 'healthy' ? '#2e7d32' : '#c62828',
          fontSize: '0.9rem'
        }}>
          {backendHealth.status === 'healthy' ? '✅ Backend Connected' : '❌ Backend Disconnected'}
        </div>
      )}
      
      <div style={{ marginBottom: '1.5rem' }}>
        <h3>📚 Available Scenarios</h3>
        <div className="scenario-buttons">
          {availableScenarios.map((scenario, index) => (
            <div key={index} className="scenario-item">
              <button
                onClick={() => loadScenario(scenario.path)}
                className="btn btn-primary"
                disabled={isLoading}
                style={{ width: '100%', marginBottom: '0.5rem' }}
              >
                {isLoading ? '⏳ Loading...' : `${scenario.emoji} Load ${scenario.name}`}
              </button>
              <small>{scenario.description}</small>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <h3>⚙️ Session Management</h3>
        <div className="scenario-buttons">
          <button
            onClick={clearSession}
            className="btn btn-danger"
            disabled={isLoading}
          >
            {isLoading ? '⏳' : '🗑️ Clear Session'}
          </button>
          <button
            onClick={handleHealthCheck}
            className="btn btn-secondary"
            disabled={isLoading}
          >
            {isLoading ? '⏳' : '🔍 Check Backend Health'}
          </button>
        </div>
      </div>

      {sessionInfo && (
        <div className="status-info">
          <h3>📋 Session Information</h3>
          <p><strong>Has Prompter State:</strong> {sessionInfo.has_prompter_state ? '✅ Yes' : '❌ No'}</p>
          <p><strong>Session ID:</strong> {sessionInfo.session_id || 'Not set'}</p>
        </div>
      )}
    </div>
  )
}

export default ScenarioManager
