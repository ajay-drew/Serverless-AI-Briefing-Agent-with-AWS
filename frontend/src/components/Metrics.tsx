import { useState } from 'react'
import { BarChart3, Loader2, AlertCircle, Mail, Calendar, Tag } from 'lucide-react'
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
      minute: '2-digit',
    })
  }

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-6 sm:mb-8">
        <h2 className="text-xl sm:text-2xl font-semibold text-ink-primary tracking-tight mb-1">
          Your metrics
        </h2>
        <p className="text-ink-secondary text-sm sm:text-base">
          Articles sent and preferences.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="mb-6 sm:mb-8">
        <label className="block text-sm font-medium text-ink-primary mb-2">
          Email
        </label>
        <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="flex-1 min-w-0 px-4 py-3 bg-surface border border-border rounded-lg text-ink-primary placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent text-sm"
            placeholder="you@example.com"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-3 bg-accent text-white font-medium rounded-lg hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm shrink-0 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
                Loading…
              </>
            ) : (
              'View metrics'
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="mb-6 p-4 sm:p-5 bg-surface border border-border-strong rounded-xl flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-ink-secondary shrink-0 mt-0.5" aria-hidden />
          <p className="text-ink-primary text-sm sm:text-base">{error}</p>
        </div>
      )}

      {metrics && (
        <div className="space-y-5 sm:space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
            <div className="p-4 sm:p-5 bg-surface border border-border rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-4 h-4 text-ink-tertiary" aria-hidden />
                <span className="text-xs font-medium text-ink-tertiary uppercase tracking-wide">
                  Articles sent
                </span>
              </div>
              <p className="text-2xl sm:text-3xl font-semibold text-ink-primary">
                {metrics.total_articles_sent}
              </p>
            </div>
            <div className="p-4 sm:p-5 bg-surface border border-border rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="w-4 h-4 text-ink-tertiary" aria-hidden />
                <span className="text-xs font-medium text-ink-tertiary uppercase tracking-wide">
                  Last briefing
                </span>
              </div>
              <p className="text-sm sm:text-base font-medium text-ink-primary">
                {formatDate(metrics.last_briefing_at)}
              </p>
            </div>
          </div>

          <div className="p-4 sm:p-5 bg-surface border border-border rounded-xl">
            <div className="flex items-center gap-2 mb-3">
              <Tag className="w-4 h-4 text-ink-tertiary" aria-hidden />
              <h3 className="text-sm font-semibold text-ink-primary">
                Topics
              </h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {metrics.topics.map((topic, index) => (
                <span
                  key={index}
                  className="px-3 py-1.5 bg-surface-muted text-ink-secondary rounded-lg text-sm"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>

          <div className="p-4 sm:p-5 bg-surface border border-border rounded-xl space-y-3">
            <div className="flex items-center gap-2 mb-3">
              <Mail className="w-4 h-4 text-ink-tertiary" aria-hidden />
              <h3 className="text-sm font-semibold text-ink-primary">
                Account
              </h3>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between py-2 border-b border-border">
                <span className="text-ink-tertiary">Email</span>
                <span className="text-ink-primary">{metrics.email}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-border">
                <span className="text-ink-tertiary">Member since</span>
                <span className="text-ink-primary">{formatDate(metrics.created_at)}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-ink-tertiary">Topics</span>
                <span className="text-ink-primary">{metrics.topics.length}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {!loading && !metrics && !error && (
        <div className="py-12 sm:py-16 text-center">
          <BarChart3 className="w-10 h-10 text-ink-muted mx-auto mb-3" aria-hidden />
          <p className="text-ink-secondary text-sm sm:text-base">
            Enter your email to view metrics.
          </p>
        </div>
      )}
    </div>
  )
}
