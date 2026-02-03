import { useState, useEffect } from 'react'
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

  // Edit form state
  const [editTopics, setEditTopics] = useState<string[]>([])
  const [customTopic, setCustomTopic] = useState('')
  const [editTimezone, setEditTimezone] = useState('')
  const [editBriefingTime, setEditBriefingTime] = useState('')

  // Load all users on component mount
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
        setMessage({ type: 'error', text: 'No users found. Register a user first!' })
      }
    } catch (err: any) {
      setMessage({ type: 'error', text: 'Failed to load users from database' })
      console.error('Error loading users:', err)
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
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
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
      setMessage({ type: 'error', text: 'Please select at least one topic' })
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

      setMessage({ type: 'success', text: 'User preferences updated successfully!' })
      // Reload users list
      await loadUsers()
      // Refresh selected user data
      const updatedUser = await api.getPreferences(selectedUser.email)
      setSelectedUser(updatedUser)
      setIsEditing(false)
    } catch (err: any) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to update preferences' })
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (email: string) => {
    if (!window.confirm(`Are you sure you want to delete user ${email}? This action cannot be undone.`)) {
      return
    }

    setLoading(true)
    setMessage(null)

    try {
      await api.deleteUser(email)
      setMessage({ type: 'success', text: 'User deleted successfully!' })
      // Reload users list
      await loadUsers()
      // Clear selection if deleted user was selected
      if (selectedUser?.email === email) {
        setSelectedUser(null)
      }
      setIsEditing(false)
    } catch (err: any) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to delete user' })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setIsEditing(false)
    setMessage(null)
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">User Management</h2>
          <p className="text-gray-600 mt-1">
            View and manage all registered users
          </p>
        </div>
        <button
          onClick={loadUsers}
          disabled={loading}
          className="px-4 py-2 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-all"
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Messages */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg border ${
          message.type === 'success' 
            ? 'bg-green-50 border-green-200 text-green-800' 
            : 'bg-red-50 border-red-200 text-red-800'
        }`}>
          <p>{message.type === 'success' ? '✓' : '✗'} {message.text}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Users List */}
        <div className="lg:col-span-1">
          <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
            <h3 className="font-semibold text-gray-800 mb-4">
              All Users ({users.length})
            </h3>
            
            {loading && users.length === 0 ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                <p className="text-gray-500 mt-2 text-sm">Loading users...</p>
              </div>
            ) : users.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500 text-sm">No users registered yet</p>
                <p className="text-gray-400 text-xs mt-1">Go to "Get Started" to add users</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {users.map((user) => (
                  <button
                    key={user.email}
                    onClick={() => handleSelectUser(user)}
                    className={`w-full text-left p-3 rounded-lg transition-all ${
                      selectedUser?.email === user.email
                        ? 'bg-purple-100 border-2 border-purple-500'
                        : 'bg-white border border-gray-300 hover:border-purple-400'
                    }`}
                  >
                    <p className="font-semibold text-gray-800 text-sm truncate">
                      {user.email}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {user.preferences.topics.length} topics • {user.timezone}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* User Details / Edit Panel */}
        <div className="lg:col-span-2">
          {!selectedUser ? (
            <div className="text-center py-16 bg-gray-50 rounded-lg border border-gray-200">
              <svg
                className="mx-auto h-16 w-16 text-gray-400 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">
                Select a User
              </h3>
              <p className="text-gray-500">
                Click on a user from the list to view or edit their details
              </p>
            </div>
          ) : isEditing ? (
            /* Edit Mode */
            <div className="bg-white rounded-lg p-6 border border-gray-300 shadow-sm">
              <h3 className="text-xl font-bold text-gray-800 mb-6">Edit User Preferences</h3>

              <div className="space-y-6">
                {/* Email (Read-only) */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Email (cannot be changed)
                  </label>
                  <input
                    type="email"
                    value={selectedUser.email}
                    disabled
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-100 text-gray-600 cursor-not-allowed"
                  />
                </div>

                {/* Topics */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Topics of Interest
                  </label>
                  
                  {/* Popular Topics */}
                  <div className="flex flex-wrap gap-2 mb-3">
                    {POPULAR_TOPICS.map((topic) => (
                      <button
                        key={topic}
                        type="button"
                        onClick={() => handleTopicToggle(topic)}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                          editTopics.includes(topic)
                            ? 'bg-purple-600 text-white'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        {topic}
                      </button>
                    ))}
                  </div>

                  {/* Custom Topic Input */}
                  <div className="flex gap-2 mb-3">
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

                  {/* Selected Topics */}
                  {editTopics.length > 0 && (
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-sm font-semibold text-gray-700 mb-2">
                        Selected Topics ({editTopics.length}):
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {editTopics.map((topic) => (
                          <span
                            key={topic}
                            className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm"
                          >
                            {topic}
                            <button
                              type="button"
                              onClick={() => handleRemoveTopic(topic)}
                              className="ml-1 text-purple-500 hover:text-purple-700 font-bold"
                            >
                              ×
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Timezone and Time */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Timezone
                    </label>
                    <select
                      value={editTimezone}
                      onChange={(e) => setEditTimezone(e.target.value)}
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
                      value={editBriefingTime}
                      onChange={(e) => setEditBriefingTime(e.target.value)}
                      required
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <button
                    onClick={handleSaveChanges}
                    disabled={loading || editTopics.length === 0}
                    className="flex-1 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {loading ? 'Saving...' : 'Save Changes'}
                  </button>
                  <button
                    onClick={handleCancel}
                    disabled={loading}
                    className="px-6 py-3 bg-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-400 disabled:opacity-50 transition-all"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* View Mode */
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <div className="flex justify-between items-start mb-6">
                <h3 className="text-xl font-bold text-gray-800">User Details</h3>
                <div className="flex gap-2">
                  <button
                    onClick={handleEdit}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all text-sm font-semibold"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(selectedUser.email)}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all text-sm font-semibold"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-600 mb-2">Email</label>
                  <p className="text-gray-800 font-medium text-lg">{selectedUser.email}</p>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-600 mb-2">
                    Topics ({selectedUser.preferences.topics.length})
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {selectedUser.preferences.topics.map((topic: string) => (
                      <span
                        key={topic}
                        className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-600 mb-2">Timezone</label>
                    <p className="text-gray-800 font-medium">{selectedUser.timezone}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-600 mb-2">Briefing Time</label>
                    <p className="text-gray-800 font-medium">{selectedUser.briefing_time}</p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-600 mb-2">Registered</label>
                  <p className="text-gray-800">{new Date(selectedUser.created_at).toLocaleString()}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Stats Footer */}
      <div className="mt-6 bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-blue-900">Database Status</p>
            <p className="text-xs text-blue-700 mt-1">
              {users.length} {users.length === 1 ? 'user' : 'users'} registered • Connected to Neon PostgreSQL
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-blue-600">All changes save directly to database</p>
          </div>
        </div>
      </div>
    </div>
  )
}
