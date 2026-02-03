import { useState } from 'react'
import Onboarding from './components/Onboarding'
import QueryInterface from './components/QueryInterface'
import Metrics from './components/Metrics'
import UserManagement from './components/UserManagement'

type TabType = 'onboarding' | 'query' | 'metrics' | 'manage'

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('onboarding')

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">
            AI Briefing Agent
          </h1>
          <p className="text-white/80 text-lg">
            Get personalized news briefings powered by AI
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white/10 backdrop-blur-lg rounded-t-2xl shadow-xl">
          <div className="flex border-b border-white/20">
            <button
              onClick={() => setActiveTab('onboarding')}
              className={`flex-1 py-4 px-6 text-center font-semibold transition-all ${
                activeTab === 'onboarding'
                  ? 'bg-white text-purple-600 rounded-tl-2xl'
                  : 'text-white hover:bg-white/10'
              }`}
            >
              Get Started
            </button>
            <button
              onClick={() => setActiveTab('query')}
              className={`flex-1 py-4 px-6 text-center font-semibold transition-all ${
                activeTab === 'query'
                  ? 'bg-white text-purple-600'
                  : 'text-white hover:bg-white/10'
              }`}
            >
              Search Now
            </button>
            <button
              onClick={() => setActiveTab('metrics')}
              className={`flex-1 py-4 px-6 text-center font-semibold transition-all ${
                activeTab === 'metrics'
                  ? 'bg-white text-purple-600'
                  : 'text-white hover:bg-white/10'
              }`}
            >
              My Metrics
            </button>
            <button
              onClick={() => setActiveTab('manage')}
              className={`flex-1 py-4 px-6 text-center font-semibold transition-all ${
                activeTab === 'manage'
                  ? 'bg-white text-purple-600 rounded-tr-2xl'
                  : 'text-white hover:bg-white/10'
              }`}
            >
              Manage Users
            </button>
          </div>

          {/* Content */}
          <div className="bg-white rounded-b-2xl p-8">
            {activeTab === 'onboarding' && <Onboarding />}
            {activeTab === 'query' && <QueryInterface />}
            {activeTab === 'metrics' && <Metrics />}
            {activeTab === 'manage' && <UserManagement />}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-white/60 text-sm">
          <p>Powered by Groq, Tavily, and LangGraph</p>
        </div>
      </div>
    </div>
  )
}

export default App
