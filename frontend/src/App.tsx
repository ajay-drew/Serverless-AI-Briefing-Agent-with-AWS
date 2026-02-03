import { useState } from 'react'
import { Zap, Search, BarChart3, Settings, Sparkles } from 'lucide-react'
import Onboarding from './components/Onboarding'
import QueryInterface from './components/QueryInterface'
import Metrics from './components/Metrics'
import UserManagement from './components/UserManagement'

type TabType = 'onboarding' | 'query' | 'metrics' | 'manage'

const TABS: { id: TabType; label: string; icon: typeof Zap }[] = [
  { id: 'onboarding', label: 'Get Started', icon: Zap },
  { id: 'query', label: 'Search Now', icon: Search },
  { id: 'metrics', label: 'My Metrics', icon: BarChart3 },
  { id: 'manage', label: 'Manage Users', icon: Settings },
]

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('onboarding')

  return (
    <div className="min-h-screen bg-surface-subtle">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12 lg:py-16">
        {/* Header */}
        <header className="mb-10 sm:mb-12 lg:mb-14">
          <div className="flex items-baseline gap-2 sm:gap-3 mb-2">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-semibold tracking-tight text-ink-primary">
              Briefing Agent
            </h1>
            <span className="flex items-center gap-1 text-ink-tertiary text-sm sm:text-base font-normal">
              <Sparkles className="w-4 h-4" aria-hidden />
              by AI
            </span>
          </div>
          <p className="text-ink-secondary text-base sm:text-lg max-w-xl font-normal leading-relaxed">
            Daily intelligence, distilled and delivered.
          </p>
        </header>

        {/* Tabs */}
        <div className="bg-surface border border-border rounded-2xl shadow-sm overflow-hidden">
          <nav className="flex border-b border-border" aria-label="Main navigation">
            {TABS.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 min-w-0 flex items-center justify-center gap-2 py-4 px-3 sm:py-5 sm:px-4 text-sm font-medium transition-colors ${
                    isActive
                      ? 'text-ink-primary bg-surface border-b-2 border-ink-primary -mb-px'
                      : 'text-ink-tertiary hover:text-ink-secondary hover:bg-surface-muted'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" aria-hidden />
                  <span className="truncate">{tab.label}</span>
                </button>
              )
            })}
          </nav>

          {/* Content */}
          <main className="p-6 sm:p-8 lg:p-10 min-h-[480px] sm:min-h-[520px]">
            {activeTab === 'onboarding' && <Onboarding />}
            {activeTab === 'query' && <QueryInterface />}
            {activeTab === 'metrics' && <Metrics />}
            {activeTab === 'manage' && <UserManagement />}
          </main>
        </div>

        {/* Footer */}
        <footer className="mt-10 sm:mt-12 text-center">
          <p className="text-ink-muted text-xs sm:text-sm">
            Powered by Groq · Tavily · LangGraph
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App
