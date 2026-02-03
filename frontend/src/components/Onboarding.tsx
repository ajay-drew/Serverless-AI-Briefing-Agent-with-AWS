import { useState } from 'react'
import { CheckCircle, XCircle } from 'lucide-react'
import { api } from '../api/client'

const POPULAR_TOPICS = [
  'Artificial Intelligence',
  'Technology',
  'Business',
  'Science',
  'Politics',
  'Health',
  'Finance',
  'Climate',
  'Cybersecurity',
  'Space',
]

const TIMEZONES = [
  'Asia/Kolkata',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'Europe/London',
  'Europe/Paris',
  'Asia/Tokyo',
  'Asia/Shanghai',
  'Asia/Dubai',
  'Australia/Sydney',
  'UTC',
]

export default function Onboarding() {
  const [email, setEmail] = useState('')
  const [selectedTopics, setSelectedTopics] = useState<string[]>([])
  const [customTopic, setCustomTopic] = useState('')
  const [timezone, setTimezone] = useState('Asia/Kolkata')
  const [briefingTime, setBriefingTime] = useState('09:00')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const handleTopicToggle = (topic: string) => {
    setSelectedTopics(prev =>
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    )
  }

  const handleAddCustomTopic = () => {
    if (customTopic.trim() && !selectedTopics.includes(customTopic.trim())) {
      setSelectedTopics([...selectedTopics, customTopic.trim()])
      setCustomTopic('')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess(false)

    try {
      if (selectedTopics.length === 0) {
        throw new Error('Please select at least one topic')
      }

      await api.register({
        email,
        preferences: { topics: selectedTopics },
        timezone,
        briefing_time: briefingTime,
      })

      setSuccess(true)
      setEmail('')
      setSelectedTopics([])
      setTimezone('Asia/Kolkata')
      setBriefingTime('09:00')
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-8">
        <h2 className="text-xl sm:text-2xl font-semibold text-ink-primary tracking-tight mb-1">
          Get Daily Briefings
        </h2>
        <p className="text-ink-secondary text-sm sm:text-base">
          Curated intelligence delivered to your inbox at your chosen time.
        </p>
      </div>

      {success && (
        <div className="mb-6 p-4 sm:p-5 bg-surface border border-border rounded-xl flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-ink-primary shrink-0 mt-0.5" aria-hidden />
          <div className="min-w-0">
            <p className="font-medium text-ink-primary text-sm sm:text-base">
              Registration successful
            </p>
            <p className="text-ink-secondary text-sm mt-1">
              Briefings at <span className="font-medium text-ink-primary">{briefingTime}</span> ({timezone}).
            </p>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 sm:p-5 bg-surface border border-border-strong rounded-xl flex items-start gap-3">
          <XCircle className="w-5 h-5 text-ink-secondary shrink-0 mt-0.5" aria-hidden />
          <p className="text-ink-primary text-sm sm:text-base">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6 sm:space-y-7">
        <div>
          <label className="block text-sm font-medium text-ink-primary mb-2">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-ink-primary placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent text-sm sm:text-base"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-ink-primary mb-3">
            Topics
          </label>
          <div className="flex flex-wrap gap-2 sm:gap-2.5 mb-3">
            {POPULAR_TOPICS.map((topic) => (
              <button
                key={topic}
                type="button"
                onClick={() => handleTopicToggle(topic)}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedTopics.includes(topic)
                    ? 'bg-accent text-white'
                    : 'bg-surface-muted text-ink-secondary border border-border hover:border-border-strong hover:text-ink-primary'
                }`}
              >
                {topic}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={customTopic}
              onChange={(e) => setCustomTopic(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomTopic())}
              className="flex-1 min-w-0 px-4 py-2.5 bg-surface border border-border rounded-lg text-ink-primary placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent text-sm"
              placeholder="Add topic..."
            />
            <button
              type="button"
              onClick={handleAddCustomTopic}
              className="px-4 py-2.5 bg-surface border border-border rounded-lg text-ink-secondary hover:bg-surface-muted hover:text-ink-primary font-medium text-sm shrink-0"
            >
              Add
            </button>
          </div>
          {selectedTopics.length > 0 && (
            <p className="text-ink-muted text-xs mt-2">
              {selectedTopics.length} topic{selectedTopics.length !== 1 ? 's' : ''} selected
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
          <div>
            <label className="block text-sm font-medium text-ink-primary mb-2">
              Timezone
            </label>
            <select
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-ink-primary focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent text-sm sm:text-base cursor-pointer"
            >
              {TIMEZONES.map((tz) => (
                <option key={tz} value={tz}>{tz}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-ink-primary mb-2">
              Briefing time
            </label>
            <input
              type="time"
              value={briefingTime}
              onChange={(e) => setBriefingTime(e.target.value)}
              required
              className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-ink-primary focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent text-sm sm:text-base"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || selectedTopics.length === 0}
          className="w-full py-3.5 sm:py-4 bg-accent text-white font-medium rounded-lg hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm sm:text-base"
        >
          {loading ? 'Registering…' : 'Start receiving briefings'}
        </button>
      </form>
    </div>
  )
}
