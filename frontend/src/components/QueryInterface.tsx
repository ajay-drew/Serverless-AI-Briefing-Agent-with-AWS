import { useState } from 'react'
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
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-800 mb-4">
        Real-Time Search
      </h2>
      <p className="text-gray-600 mb-8">
        Search for news articles on any topic and get AI-powered summaries instantly.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        {/* Email */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Your Email
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

        {/* Search Query */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Search Query
          </label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="e.g., latest AI breakthroughs"
          />
        </div>

        {/* Max Results */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Number of Results: {maxResults}
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={maxResults}
            onChange={(e) => setMaxResults(Number(e.target.value))}
            className="w-full"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Searching...
            </span>
          ) : (
            'Search Now'
          )}
        </button>
      </form>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">✗ {error}</p>
        </div>
      )}

      {/* Results */}
      {articles.length > 0 && (
        <div>
          <h3 className="text-2xl font-bold text-gray-800 mb-4">
            Results ({articles.length} of {totalFound} found)
          </h3>
          <div className="space-y-4">
            {articles.map((article, index) => (
              <div
                key={index}
                className="p-6 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg hover:shadow-lg transition-shadow"
              >
                <h4 className="text-xl font-semibold text-gray-800 mb-2">
                  {article.title}
                </h4>
                <p className="text-gray-700 mb-3">{article.summary}</p>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-purple-600 hover:text-purple-800 font-medium inline-flex items-center"
                >
                  Read more
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && articles.length === 0 && query && (
        <div className="text-center py-12">
          <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-gray-600">No results found. Try a different search query.</p>
        </div>
      )}
    </div>
  )
}
