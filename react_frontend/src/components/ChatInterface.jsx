import { useState, useEffect, useRef } from 'react'
import apiService from '../services/apiService'

const ChatInterface = () => {
  const [messages, setMessages] = useState([])
  const [currentInput, setCurrentInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationState, setConversationState] = useState(null)
  const [currentPrompt, setCurrentPrompt] = useState('')
  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load initial prompt when component mounts
  useEffect(() => {
    loadCurrentPrompt()
    loadConversationState()
  }, [])

  const loadCurrentPrompt = async () => {
    try {
      const response = await apiService.getCurrentPrompt()
      setCurrentPrompt(response.data.prompt)
      
      // Add system message if there's a prompt
      if (response.data.prompt && response.data.prompt !== 'No scenario loaded. Please load a scenario first.') {
        setMessages(prev => [...prev, {
          type: 'system',
          content: response.data.prompt,
          timestamp: new Date().toISOString()
        }])
      }
    } catch (error) {
      console.error('Error loading current prompt:', error)
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Failed to load current prompt. Please check your connection.',
        timestamp: new Date().toISOString()
      }])
    }
  }

  const loadConversationState = async () => {
    try {
      const response = await apiService.getConversationState()
      setConversationState(response.data)
    } catch (error) {
      console.error('Error loading conversation state:', error)
    }
  }

  const handleSubmitResponse = async (e) => {
    e.preventDefault()
    if (!currentInput.trim()) return

    setIsLoading(true)
    
    // Add user message
    const userMessage = {
      type: 'user',
      content: currentInput,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    
    try {
      const response = await apiService.submitStudentResponse(currentInput)
      const result = response.data
      
      // Add system response
      let systemMessage = {
        type: 'system',
        timestamp: new Date().toISOString()
      }

      if (result.status === 'success') {
        systemMessage = {
          ...systemMessage,
          content: result.feedback,
          nextPrompt: result.next_prompt
        }
        
        // Add next prompt as a separate message if it exists
        if (result.next_prompt) {
          setTimeout(() => {
            setMessages(prev => [...prev, {
              type: 'system',
              content: result.next_prompt,
              timestamp: new Date().toISOString()
            }])
          }, 1000)
        }
      } else if (result.status === 'needs_correction') {
        systemMessage = {
          ...systemMessage,
          type: 'error',
          content: result.feedback,
          correctedResponse: result.corrected_response,
          attemptCount: result.attempt_count
        }
      } else {
        systemMessage = {
          ...systemMessage,
          content: result.feedback || 'Please continue...'
        }
      }
      
      setMessages(prev => [...prev, systemMessage])
      
      // Update conversation state
      await loadConversationState()
      
    } catch (error) {
      console.error('Error submitting response:', error)
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Sorry, there was an error processing your response. Please try again.',
        timestamp: new Date().toISOString()
      }])
    } finally {
      setIsLoading(false)
      setCurrentInput('')
    }
  }

  const clearChat = () => {
    setMessages([])
    if (currentPrompt && currentPrompt !== 'No scenario loaded. Please load a scenario first.') {
      setMessages([{
        type: 'system',
        content: currentPrompt,
        timestamp: new Date().toISOString()
      }])
    }
  }

  const resetConversation = async () => {
    setIsLoading(true)
    try {
      await apiService.resetConversation()
      setMessages([])
      await loadCurrentPrompt()
      await loadConversationState()
    } catch (error) {
      console.error('Error resetting conversation:', error)
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Failed to reset conversation. Please try again.',
        timestamp: new Date().toISOString()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const isScenarioLoaded = currentPrompt && currentPrompt !== 'No scenario loaded. Please load a scenario first.'

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="loading">
            {!isScenarioLoaded
              ? '🎯 Please load a scenario to start chatting...'
              : '💬 Start your conversation by typing a message below...'
            }
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              <div className="message-header">
                {message.type === 'system' ? '🤖 Teacher' : 
                 message.type === 'user' ? '👤 You' : 
                 message.type === 'error' ? '⚠️ Teacher (Correction)' : '💬 System'}
              </div>
              <div>{message.content}</div>
              {message.correctedResponse && (
                <div className="corrected-response">
                  <strong>✏️ Corrected version:</strong> {message.correctedResponse}
                </div>
              )}
              {message.attemptCount && (
                <div className="attempt-count">
                  📊 Attempt {message.attemptCount}
                </div>
              )}
            </div>
          ))
        )}
        {isLoading && (
          <div className="loading">
            <div>🤖 Teacher is thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-section">
        <form onSubmit={handleSubmitResponse}>
          <div className="input-group">
            <input
              type="text"
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              placeholder={isScenarioLoaded ? "Type your response here..." : "Please load a scenario first..."}
              disabled={isLoading || !isScenarioLoaded}
              autoComplete="off"
            />
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={isLoading || !currentInput.trim() || !isScenarioLoaded}
            >
              {isLoading ? '⏳' : '📤 Send'}
            </button>
          </div>
        </form>
        
        <div className="input-controls">
          <button 
            onClick={clearChat}
            className="btn btn-secondary"
            disabled={isLoading}
          >
            🗑️ Clear Chat
          </button>
          <button 
            onClick={resetConversation}
            className="btn btn-danger"
            disabled={isLoading}
          >
            🔄 Reset Conversation
          </button>
        </div>
      </div>

      {conversationState && (
        <div className="status-info">
          <h3>📊 Conversation Status</h3>
          <p><strong>Scenario:</strong> {conversationState.scenario_name || 'None loaded'}</p>
          <p><strong>Current Event:</strong> {conversationState.current_event_index}</p>
          <p><strong>Attempts:</strong> {conversationState.attempts}</p>
          {conversationState.variables && Object.keys(conversationState.variables).length > 0 && (
            <div>
              <strong>Variables:</strong>
              <pre>{JSON.stringify(conversationState.variables, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ChatInterface
