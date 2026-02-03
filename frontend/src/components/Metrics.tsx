import { useState } from 'react'
import { api, MetricsResponse } from '../api/client'

export default function Metrics() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setMetrics(null)

    try {
      const data = await api.getMetrics(email)
      setMetrics(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch metrics')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never'
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
    })
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-800 mb-4">
        Your Briefing Metrics
      </h2>
      <p className="text-gray-600 mb-8">
        View your briefing statistics and preferences.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Email Address
          </label>
          <div className="flex gap-2">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="your@email.com"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
            >
              {loading ? 'Loading...' : 'View Metrics'}
            </button>
          </div>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">✗ {error}</p>
        </div>
      )}

      {/* Metrics Display */}
      {metrics && (
        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-6 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg">
              <div className="text-purple-600 text-sm font-semibold mb-2">
                Total Articles Sent
              </div>
              <div className="text-4xl font-bold text-gray-800">
                {metrics.total_articles_sent}
              </div>
            </div>

            <div className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg">
              <div className="text-indigo-600 text-sm font-semibold mb-2">
                Last Briefing
              </div>
              <div className="text-lg font-semibold text-gray-800">
                {formatDate(metrics.last_briefing_at)}
              </div>
            </div>
          </div>

          {/* Topics */}
          <div className="p-6 bg-white border border-gray-200 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Your Topics
            </h3>
            <div className="flex flex-wrap gap-2">
              {metrics.topics.map((topic, index) => (
                <span
                  key={index}
                  className="px-4 py-2 bg-purple-100 text-purple-800 rounded-full text-sm font-medium"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>

          {/* Account Info */}
          <div className="p-6 bg-white border border-gray-200 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Account Information
            </h3>
            <div className="space-y-2 text-gray-700">
              <div className="flex justify-between">
                <span className="font-medium">Email:</span>
                <span>{metrics.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Member Since:</span>
                <span>{formatDate(metrics.created_at)}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Topics Subscribed:</span>
                <span>{metrics.topics.length}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {!loading && !metrics && !error && (
        <div className="text-center py-12">
          <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="text-gray-600">Enter your email to view your metrics</p>
        </div>
      )}
    </div>
  )
}
