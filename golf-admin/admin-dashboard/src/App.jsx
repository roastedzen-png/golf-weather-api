import { useState, useEffect } from 'react'
import { googleLogout, GoogleLogin } from '@react-oauth/google'
import { jwtDecode } from 'jwt-decode'
import { useTranslation } from 'react-i18next'
import Dashboard from './components/Dashboard'
import ApiKeys from './components/ApiKeys'
import Usage from './components/Usage'
import Logs from './components/Logs'
import ApiPlayground from './components/ApiPlayground'
import SystemHealth from './components/SystemHealth'
import Leads from './components/Leads'
import UnitToggle from './components/UnitToggle'
import LanguageSelector from './components/LanguageSelector'
import { UnitProvider } from './contexts/UnitContext'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://golf-weather-api-production.up.railway.app'

function App() {
  const { t } = useTranslation(['common'])
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [authError, setAuthError] = useState(null)
  const [loading, setLoading] = useState(false)

  // Check for existing token on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('admin_token')
    const savedUser = localStorage.getItem('admin_user')
    if (savedToken && savedUser) {
      setToken(savedToken)
      setUser(JSON.parse(savedUser))
      // Verify token is still valid
      verifyToken(savedToken)
    }
  }, [])

  const verifyToken = async (idToken) => {
    try {
      const response = await fetch(`${API_BASE}/admin-api/health`, {
        headers: { 'Authorization': `Bearer ${idToken}` }
      })
      if (!response.ok) {
        handleLogout()
      }
    } catch (err) {
      console.error('Token verification failed:', err)
    }
  }

  const handleGoogleSuccess = async (credentialResponse) => {
    setLoading(true)
    setAuthError(null)
    try {
      // The credential is the ID token (JWT)
      const idToken = credentialResponse.credential

      // Decode the JWT to get user info
      const userInfo = jwtDecode(idToken)

      // Verify with our backend
      const verifyResponse = await fetch(`${API_BASE}/admin-api/health`, {
        headers: { 'Authorization': `Bearer ${idToken}` }
      })

      if (verifyResponse.ok) {
        setUser(userInfo)
        setToken(idToken)
        localStorage.setItem('admin_token', idToken)
        localStorage.setItem('admin_user', JSON.stringify(userInfo))
      } else {
        const error = await verifyResponse.json()
        setAuthError(error.error?.message || 'Authentication failed')
      }
    } catch (err) {
      setAuthError('Login failed: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleError = () => {
    setAuthError('Google login failed')
  }

  const handleLogout = () => {
    googleLogout()
    setUser(null)
    setToken(null)
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
  }

  // Login screen
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Golf Physics</h1>
            <p className="text-gray-600">{t('app_name')}</p>
          </div>

          {authError && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {authError}
            </div>
          )}

          {loading ? (
            <div className="w-full bg-gray-100 py-3 px-4 rounded-lg text-center text-gray-600">
              {t('auth.signing_in')}
            </div>
          ) : (
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={handleGoogleError}
                useOneTap
                theme="filled_blue"
                size="large"
                width="300"
              />
            </div>
          )}

          <p className="text-sm text-gray-500 text-center mt-4">
            {t('auth.restricted')}
          </p>
        </div>
      </div>
    )
  }

  // Main dashboard
  const tabs = [
    { id: 'dashboard', labelKey: 'navigation.dashboard', icon: '📊' },
    { id: 'leads', labelKey: 'navigation.leads', icon: '👥' },
    { id: 'apikeys', labelKey: 'navigation.api_keys', icon: '🔑' },
    { id: 'usage', labelKey: 'navigation.usage', icon: '📈' },
    { id: 'logs', labelKey: 'navigation.logs', icon: '📋' },
    { id: 'system', labelKey: 'navigation.system', icon: '⚙️' },
    { id: 'playground', labelKey: 'navigation.playground', icon: '🧪' },
  ]

  return (
    <UnitProvider>
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-900">Golf Physics Admin</h1>
          <div className="flex items-center gap-4">
            <LanguageSelector />
            <UnitToggle />
            <span className="text-sm text-gray-600">{user.email}</span>
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:text-red-800"
            >
              {t('actions.logout')}
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-4">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <span className="mr-1">{tab.icon}</span>
                {t(tab.labelKey)}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'dashboard' && <Dashboard token={token} apiBase={API_BASE} />}
        {activeTab === 'leads' && <Leads token={token} apiBase={API_BASE} />}
        {activeTab === 'apikeys' && <ApiKeys token={token} apiBase={API_BASE} />}
        {activeTab === 'usage' && <Usage token={token} apiBase={API_BASE} />}
        {activeTab === 'logs' && <Logs token={token} apiBase={API_BASE} />}
        {activeTab === 'system' && <SystemHealth token={token} apiBase={API_BASE} />}
        {activeTab === 'playground' && <ApiPlayground apiBase={API_BASE} />}
      </main>
    </div>
    </UnitProvider>
  )
}

export default App
