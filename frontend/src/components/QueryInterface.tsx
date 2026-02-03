import { useState } from 'react'
import { Search, Loader2, ExternalLink, AlertCircle } from 'lucide-react'
import { api, Article } from '../api/client'

export default function QueryInterface() {
  const [email, setEmail] = useState('')
  const [query, setQuery] = useState('')
  const [maxResults, setMaxResults] = useState(5)
  const [loading, setLoading] = useState(false)
  const [articles, setArticles] = useState<Article[]>([])
  const [error, setError] = useState('')
  const [totalFound, setTotalFound] = useState(0)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setArticles([])

    try {
      const response = await api.query({
        email,
        query,
        max_results: maxResults,
      })

      if (response.success) {
        setArticles(response.articles)
        setTotalFound(response.total_found)
      } else {
        setError('Search failed: ' + (response.errors?.join(', ') || 'Unknown error'))
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6 sm:mb-8">
        <h2 className="text-xl sm:text-2xl font-semibold text-ink-primary tracking-tight mb-1">
          Real-time search
        </h2>
        <p className="text-ink-secondary text-sm sm:text-base">
          Get curated summaries on any topic.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5 sm:space-y-6 mb-8">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-5">
          <div className="sm:col-span-1">
            <label className="block text-sm font-medium text-ink-primary mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-ink-primary placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent text-sm"
              placeholder="you@example.com"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-ink-primary mb-2">
              Query
            </label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
              className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-ink-primary placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent text-sm"
              placeholder="e.g. latest in quantum computing"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-ink-primary mb-2">
            Results: <span className="text-ink-secondary font-normal">{maxResults}</span>
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={maxResults}
            onChange={(e) => setMaxResults(Number(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-ink-muted mt-1">
            <span>1</span>
            <span>10</span>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3.5 sm:py-4 bg-accent text-white font-medium rounded-lg hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm sm:text-base flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
              Searching…
            </>
          ) : (
            <>
              <Search className="w-4 h-4" aria-hidden />
              Search
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mb-6 p-4 sm:p-5 bg-surface border border-border-strong rounded-xl flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-ink-secondary shrink-0 mt-0.5" aria-hidden />
          <p className="text-ink-primary text-sm sm:text-base">{error}</p>
        </div>
      )}

      {articles.length > 0 && (
        <div>
          <div className="flex items-baseline gap-2 mb-4">
            <h3 className="text-lg font-semibold text-ink-primary">
              Results
            </h3>
            <span className="text-ink-muted text-sm">
              {articles.length} of {totalFound}
            </span>
          </div>
          <div className="space-y-4">
            {articles.map((article, index) => (
              <article
                key={index}
                className="p-4 sm:p-5 bg-surface border border-border rounded-xl"
              >
                <h4 className="font-medium text-ink-primary text-sm sm:text-base mb-2">
                  {article.title}
                </h4>
                <p className="text-ink-secondary text-sm leading-relaxed mb-3">
                  {article.summary}
                </p>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-sm font-medium text-accent hover:text-accent-hover transition-colors"
                >
                  Read article
                  <ExternalLink className="w-3.5 h-3.5" aria-hidden />
                </a>
              </article>
            ))}
          </div>
        </div>
      )}

      {!loading && articles.length === 0 && query && (
        <div className="py-12 sm:py-16 text-center">
          <Search className="w-10 h-10 text-ink-muted mx-auto mb-3" aria-hidden />
          <p className="text-ink-secondary text-sm sm:text-base">
            No results. Try a different query.
          </p>
        </div>
      )}
    </div>
  )
}
