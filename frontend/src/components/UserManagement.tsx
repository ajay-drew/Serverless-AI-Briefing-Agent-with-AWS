import { useState, useEffect } from 'react'
import {
  CheckCircle,
  XCircle,
  RefreshCw,
  Users,
  User,
  Edit3,
  Trash2,
  Loader2,
  Plus,
  X,
} from 'lucide-react'
import { api, UserResponse } from '../api/client'

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

export default function UserManagement() {
  const [users, setUsers] = useState<UserResponse[]>([])
  const [selectedUser, setSelectedUser] = useState<UserResponse | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const [editTopics, setEditTopics] = useState<string[]>([])
  const [customTopic, setCustomTopic] = useState('')
  const [editTimezone, setEditTimezone] = useState('')
  const [editBriefingTime, setEditBriefingTime] = useState('')

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    setLoading(true)
    setMessage(null)
    try {
      const allUsers = await api.getAllUsers()
      setUsers(allUsers)
      if (allUsers.length === 0) {
        setMessage({ type: 'error', text: 'No users yet. Register one in Get Started.' })
      }
    } catch {
      setMessage({ type: 'error', text: 'Failed to load users.' })
    } finally {
      setLoading(false)
    }
  }

  const handleSelectUser = (user: UserResponse) => {
    setSelectedUser(user)
    setIsEditing(false)
    setMessage(null)
  }

  const handleEdit = () => {
    if (!selectedUser) return
    setEditTopics(selectedUser.preferences.topics || [])
    setEditTimezone(selectedUser.timezone)
    setEditBriefingTime(selectedUser.briefing_time)
    setIsEditing(true)
  }

  const handleTopicToggle = (topic: string) => {
    setEditTopics(prev =>
      prev.includes(topic) ? prev.filter(t => t !== topic) : [...prev, topic]
    )
  }

  const handleAddCustomTopic = () => {
    if (customTopic.trim() && !editTopics.includes(customTopic.trim())) {
      setEditTopics([...editTopics, customTopic.trim()])
      setCustomTopic('')
    }
  }

  const handleRemoveTopic = (topic: string) => {
    setEditTopics(prev => prev.filter(t => t !== topic))
  }

  const handleSaveChanges = async () => {
    if (!selectedUser) return
    if (editTopics.length === 0) {
      setMessage({ type: 'error', text: 'Select at least one topic.' })
      return
    }

    setLoading(true)
    setMessage(null)
    try {
      await api.updatePreferences(selectedUser.email, {
        preferences: { topics: editTopics },
        timezone: editTimezone,
        briefing_time: editBriefingTime,
      })
      setMessage({ type: 'success', text: 'Preferences updated.' })
      await loadUsers()
      const updated = await api.getPreferences(selectedUser.email)
      setSelectedUser(updated)
      setIsEditing(false)
    } catch (err: any) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Update failed.' })
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (email: string) => {
    if (!window.confirm(`Delete ${email}? This cannot be undone.`)) return

    setLoading(true)
    setMessage(null)
    try {
      await api.deleteUser(email)
      setMessage({ type: 'success', text: 'User deleted.' })
      await loadUsers()
      if (selectedUser?.email === email) setSelectedUser(null)
      setIsEditing(false)
    } catch (err: any) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Delete failed.' })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    setMessage(null)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl sm:text-2xl font-semibold text-ink-primary tracking-tight mb-1">
            Manage users
          </h2>
          <p className="text-ink-secondary text-sm sm:text-base">
            View and edit preferences.
          </p>
        </div>
        <button
          onClick={loadUsers}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-4 py-2.5 bg-surface border border-border rounded-lg text-ink-secondary hover:bg-surface-muted hover:text-ink-primary font-medium text-sm shrink-0 disabled:opacity-50 transition-colors"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
          ) : (
            <RefreshCw className="w-4 h-4" aria-hidden />
          )}
          Refresh
        </button>
      </div>

      {message && (
        <div className={`mb-6 p-4 sm:p-5 rounded-xl border flex items-start gap-3 ${
          message.type === 'success'
            ? 'bg-surface border-border'
            : 'bg-surface border-border-strong'
        }`}>
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5 text-ink-primary shrink-0 mt-0.5" aria-hidden />
          ) : (
            <XCircle className="w-5 h-5 text-ink-secondary shrink-0 mt-0.5" aria-hidden />
          )}
          <p className={message.type === 'success' ? 'text-ink-primary' : 'text-ink-primary'}>{message.text}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 sm:gap-6">
        {/* User list */}
        <div className="lg:col-span-1">
          <div className="bg-surface border border-border rounded-xl p-4 sm:p-5">
            <h3 className="flex items-center gap-2 text-sm font-semibold text-ink-primary mb-4">
              <Users className="w-4 h-4" aria-hidden />
              Users <span className="text-ink-muted font-normal">({users.length})</span>
            </h3>

            {loading && users.length === 0 ? (
              <div className="py-8 flex flex-col items-center gap-2">
                <Loader2 className="w-6 h-6 animate-spin text-ink-muted" aria-hidden />
                <p className="text-ink-muted text-sm">Loading…</p>
              </div>
            ) : users.length === 0 ? (
              <div className="py-8 text-center">
                <Users className="w-10 h-10 text-ink-muted mx-auto mb-2" aria-hidden />
                <p className="text-ink-secondary text-sm">No users yet</p>
                <p className="text-ink-muted text-xs mt-1">Use Get Started to add one</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[320px] overflow-y-auto custom-scrollbar pr-1">
                {users.map((user) => (
                  <button
                    key={user.email}
                    onClick={() => handleSelectUser(user)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedUser?.email === user.email
                        ? 'bg-accent text-white'
                        : 'bg-surface-muted hover:bg-surface-muted border border-transparent hover:border-border'
                    }`}
                  >
                    <p className="font-medium text-sm truncate">
                      {user.email}
                    </p>
                    <p className={`text-xs mt-1 ${selectedUser?.email === user.email ? 'text-white/80' : 'text-ink-tertiary'}`}>
                      {user.preferences.topics.length} topics · {user.timezone}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Detail / edit panel */}
        <div className="lg:col-span-2">
          {!selectedUser ? (
            <div className="py-12 sm:py-16 text-center bg-surface border border-border rounded-xl">
              <User className="w-10 h-10 text-ink-muted mx-auto mb-3" aria-hidden />
              <h3 className="text-lg font-semibold text-ink-primary mb-1">
                Select a user
              </h3>
              <p className="text-ink-secondary text-sm">
                Choose one from the list to view or edit.
              </p>
            </div>
          ) : isEditing ? (
            <div className="bg-surface border border-border rounded-xl p-5 sm:p-6">
              <h3 className="text-lg font-semibold text-ink-primary mb-5">
                Edit preferences
              </h3>

              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-ink-primary mb-2">
                    Email (read-only)
                  </label>
                  <input
                    type="email"
                    value={selectedUser.email}
                    disabled
                    className="w-full px-4 py-3 bg-surface-muted border border-border rounded-lg text-ink-muted cursor-not-allowed text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-ink-primary mb-2">
                    Topics
                  </label>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {POPULAR_TOPICS.map((topic) => (
                      <button
                        key={topic}
                        type="button"
                        onClick={() => handleTopicToggle(topic)}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          editTopics.includes(topic)
                            ? 'bg-accent text-white'
                            : 'bg-surface-muted text-ink-secondary border border-border hover:border-border-strong'
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
                      className="flex-1 min-w-0 px-4 py-2.5 bg-surface border border-border rounded-lg text-ink-primary placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-accent/20 text-sm"
                      placeholder="Add topic..."
                    />
                    <button
                      type="button"
                      onClick={handleAddCustomTopic}
                      className="flex items-center gap-1.5 px-4 py-2.5 bg-surface border border-border rounded-lg text-ink-secondary hover:bg-surface-muted font-medium text-sm shrink-0"
                    >
                      <Plus className="w-4 h-4" aria-hidden />
                      Add
                    </button>
                  </div>
                  {editTopics.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {editTopics.map((topic) => (
                        <span
                          key={topic}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-surface-muted rounded-lg text-sm"
                        >
                          {topic}
                          <button
                            type="button"
                            onClick={() => handleRemoveTopic(topic)}
                            className="text-ink-tertiary hover:text-ink-primary"
                            aria-label={`Remove ${topic}`}
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-ink-primary mb-2">
                      Timezone
                    </label>
                    <select
                      value={editTimezone}
                      onChange={(e) => setEditTimezone(e.target.value)}
                      className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-ink-primary text-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-accent/20"
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
                      value={editBriefingTime}
                      onChange={(e) => setEditBriefingTime(e.target.value)}
                      className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-ink-primary text-sm focus:outline-none focus:ring-2 focus:ring-accent/20"
                    />
                  </div>
                </div>

                <div className="flex flex-col-reverse sm:flex-row gap-2 sm:gap-3 pt-2">
                  <button
                    onClick={handleCancel}
                    disabled={loading}
                    className="px-5 py-2.5 bg-surface border border-border rounded-lg text-ink-secondary hover:bg-surface-muted font-medium text-sm disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSaveChanges}
                    disabled={loading || editTopics.length === 0}
                    className="flex items-center justify-center gap-2 px-5 py-2.5 bg-accent text-white rounded-lg hover:bg-accent-hover font-medium text-sm disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
                    ) : null}
                    Save
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-surface border border-border rounded-xl p-5 sm:p-6">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-5">
                <h3 className="text-lg font-semibold text-ink-primary">
                  User details
                </h3>
                <div className="flex gap-2">
                  <button
                    onClick={handleEdit}
                    className="flex items-center gap-2 px-4 py-2.5 bg-accent text-white rounded-lg hover:bg-accent-hover font-medium text-sm"
                  >
                    <Edit3 className="w-4 h-4" aria-hidden />
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(selectedUser.email)}
                    className="flex items-center gap-2 px-4 py-2.5 bg-surface border border-border-strong rounded-lg text-ink-secondary hover:bg-surface-muted hover:text-ink-primary font-medium text-sm"
                  >
                    <Trash2 className="w-4 h-4" aria-hidden />
                    Delete
                  </button>
                </div>
              </div>

              <div className="space-y-4 text-sm">
                <div>
                  <span className="text-ink-tertiary block mb-1">Email</span>
                  <p className="font-medium text-ink-primary">{selectedUser.email}</p>
                </div>
                <div>
                  <span className="text-ink-tertiary block mb-2">Topics ({selectedUser.preferences.topics.length})</span>
                  <div className="flex flex-wrap gap-2">
                    {selectedUser.preferences.topics.map((topic) => (
                      <span
                        key={topic}
                        className="px-3 py-1.5 bg-surface-muted text-ink-secondary rounded-lg"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-ink-tertiary block mb-1">Timezone</span>
                    <p className="font-medium text-ink-primary">{selectedUser.timezone}</p>
                  </div>
                  <div>
                    <span className="text-ink-tertiary block mb-1">Briefing time</span>
                    <p className="font-medium text-ink-primary">{selectedUser.briefing_time}</p>
                  </div>
                </div>
                <div>
                  <span className="text-ink-tertiary block mb-1">Registered</span>
                  <p className="text-ink-primary">{new Date(selectedUser.created_at).toLocaleString()}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 p-4 bg-surface border border-border rounded-xl">
        <p className="text-ink-muted text-xs">
          {users.length} {users.length === 1 ? 'user' : 'users'} · Connected to database
        </p>
      </div>
    </div>
  )
}
