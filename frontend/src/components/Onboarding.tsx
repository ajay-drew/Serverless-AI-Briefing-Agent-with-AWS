import { useState } from 'react'
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
  'Asia/Kolkata',  // India (Mumbai/Delhi)
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
      // Reset form
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
    <div className="max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-800 mb-4">
        Get Daily AI Briefings
      </h2>
      <p className="text-gray-600 mb-8">
        Sign up to receive personalized news briefings delivered to your inbox every day.
      </p>

      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 font-semibold">
            ✓ Registration successful!
          </p>
          <p className="text-green-700 text-sm mt-1">
            You'll start receiving briefings at {briefingTime} {timezone}. Check your email for confirmation.
          </p>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">✗ {error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Email */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Email Address
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="your@email.com"
          />
        </div>

        {/* Topics */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Topics of Interest
          </label>
          <div className="flex flex-wrap gap-2 mb-3">
            {POPULAR_TOPICS.map((topic) => (
              <button
                key={topic}
                type="button"
                onClick={() => handleTopicToggle(topic)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  selectedTopics.includes(topic)
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {topic}
              </button>
            ))}
          </div>

          {/* Custom topic input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={customTopic}
              onChange={(e) => setCustomTopic(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomTopic())}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Add custom topic..."
            />
            <button
              type="button"
              onClick={handleAddCustomTopic}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Add
            </button>
          </div>

          {selectedTopics.length > 0 && (
            <p className="text-sm text-gray-600 mt-2">
              Selected: {selectedTopics.length} topic(s)
            </p>
          )}
        </div>

        {/* Timezone and Time */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Timezone
            </label>
            <select
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {TIMEZONES.map((tz) => (
                <option key={tz} value={tz}>
                  {tz}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Briefing Time
            </label>
            <input
              type="time"
              value={briefingTime}
              onChange={(e) => setBriefingTime(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || selectedTopics.length === 0}
          className="w-full py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
        >
          {loading ? 'Registering...' : 'Start Receiving Briefings'}
        </button>
      </form>
    </div>
  )
}
