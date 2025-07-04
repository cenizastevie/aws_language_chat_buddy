import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import ScenarioManager from './components/ScenarioManager'

function App() {
  const [scenarioLoaded, setScenarioLoaded] = useState(false)

  const handleScenarioLoaded = (scenarioData) => {
    setScenarioLoaded(!!scenarioData)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🗣️ AWS Language Chat Buddy</h1>
        <p>Practice English with AI-powered conversation scenarios</p>
      </header>

      <ScenarioManager onScenarioLoaded={handleScenarioLoaded} />
      
      <ChatInterface />
    </div>
  )
}

export default App
