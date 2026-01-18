import { useState, useEffect } from 'react'

export default function Leads({ token, apiBase }) {
  const [leads, setLeads] = useState([])
  const [stats, setStats] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Filters
  const [sourceFilter, setSourceFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [highValueFilter, setHighValueFilter] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  // Pagination
  const [page, setPage] = useState(0)
  const [total, setTotal] = useState(0)
  const limit = 50

  // Modal
  const [selectedLead, setSelectedLead] = useState(null)

  useEffect(() => {
    loadLeads()
    loadStats()
  }, [token])

  useEffect(() => {
    loadLeads()
  }, [sourceFilter, statusFilter, highValueFilter, searchTerm, page])

  const loadLeads = async () => {
    setLoading(true)
    setError(null)

    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: (page * limit).toString()
    })

    if (sourceFilter) params.append('source', sourceFilter)
    if (statusFilter) params.append('status', statusFilter)
    if (highValueFilter) params.append('is_high_value', highValueFilter)
    if (searchTerm) params.append('search', searchTerm)

    try {
      const response = await fetch(`${apiBase}/admin-api/leads?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setLeads(data.leads)
        setTotal(data.total)
      } else {
        setError('Failed to load leads')
      }
    } catch (err) {
      setError('Failed to load leads')
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch(`${apiBase}/admin-api/leads/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        setStats(await response.json())
      }
    } catch (err) {
      console.error('Failed to load stats:', err)
    }
  }

  const updateLeadStatus = async (leadId, status) => {
    try {
      const response = await fetch(`${apiBase}/admin-api/leads/${leadId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
      })

      if (response.ok) {
        loadLeads()
        loadStats()
      } else {
        setError('Failed to update lead status')
      }
    } catch (err) {
      setError('Failed to update lead status')
    }
  }

  const exportLeads = async () => {
    const params = new URLSearchParams()
    if (sourceFilter) params.append('source', sourceFilter)

    try {
      const response = await fetch(`${apiBase}/admin-api/leads/export?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `leads-${new Date().toISOString().split('T')[0]}.csv`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        setError('Failed to export leads')
      }
    } catch (err) {
      setError('Failed to export leads')
    }
  }

  const getSourceBadge = (source) => {
    const badges = {
      'api_key_request': { color: 'bg-blue-100 text-blue-800', label: 'API Key' },
      'contact_form': { color: 'bg-green-100 text-green-800', label: 'Contact' },
      'newsletter': { color: 'bg-purple-100 text-purple-800', label: 'Newsletter' }
    }
    const badge = badges[source] || { color: 'bg-gray-100 text-gray-800', label: source }
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${badge.color}`}>
        {badge.label}
      </span>
    )
  }

  const getStatusBadge = (status) => {
    const badges = {
      'new': { color: 'bg-yellow-100 text-yellow-800', label: 'New' },
      'contacted': { color: 'bg-blue-100 text-blue-800', label: 'Contacted' },
      'qualified': { color: 'bg-green-100 text-green-800', label: 'Qualified' },
      'converted': { color: 'bg-emerald-100 text-emerald-800', label: 'Converted' },
      'lost': { color: 'bg-red-100 text-red-800', label: 'Lost' }
    }
    const badge = badges[status] || { color: 'bg-gray-100 text-gray-800', label: status }
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${badge.color}`}>
        {badge.label}
      </span>
    )
  }

  if (loading && leads.length === 0) {
    return <div className="text-center py-8">Loading leads...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Leads</h2>
          <p className="text-gray-600">Manage all leads from API requests and contact forms</p>
        </div>
        <button
          onClick={exportLeads}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition flex items-center gap-2"
        >
          <span>Export CSV</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
          <button onClick={() => setError(null)} className="float-right">&times;</button>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm font-medium text-gray-600">Total Leads</div>
          <div className="text-3xl font-bold text-gray-900 mt-1">{stats.total || 0}</div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm font-medium text-gray-600">New</div>
          <div className="text-3xl font-bold text-yellow-600 mt-1">{stats.new || 0}</div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm font-medium text-gray-600">High Value</div>
          <div className="text-3xl font-bold text-red-600 mt-1">{stats.high_value || 0}</div>
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm font-medium text-gray-600">This Week</div>
          <div className="text-3xl font-bold text-green-600 mt-1">{stats.this_week || 0}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <input
              type="text"
              placeholder="Search by name, email, or company..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value)
                setPage(0)
              }}
              className="w-full border rounded-lg px-3 py-2"
            />
          </div>

          {/* Source Filter */}
          <select
            value={sourceFilter}
            onChange={(e) => {
              setSourceFilter(e.target.value)
              setPage(0)
            }}
            className="border rounded-lg px-3 py-2"
          >
            <option value="">All Sources</option>
            <option value="api_key_request">API Key Requests</option>
            <option value="contact_form">Contact Forms</option>
            <option value="newsletter">Newsletter</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setPage(0)
            }}
            className="border rounded-lg px-3 py-2"
          >
            <option value="">All Statuses</option>
            <option value="new">New</option>
            <option value="contacted">Contacted</option>
            <option value="qualified">Qualified</option>
            <option value="converted">Converted</option>
            <option value="lost">Lost</option>
          </select>

          {/* High Value Filter */}
          <select
            value={highValueFilter}
            onChange={(e) => {
              setHighValueFilter(e.target.value)
              setPage(0)
            }}
            className="border rounded-lg px-3 py-2"
          >
            <option value="">All Leads</option>
            <option value="true">High Value Only</option>
            <option value="false">Regular Only</option>
          </select>
        </div>

        <div className="mt-4 flex justify-between items-center text-sm text-gray-600">
          <div>Showing {leads.length} of {total} leads</div>
          <button
            onClick={() => {
              setSourceFilter('')
              setStatusFilter('')
              setHighValueFilter('')
              setSearchTerm('')
              setPage(0)
            }}
            className="text-blue-600 hover:text-blue-800"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contact</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {loading ? (
              <tr>
                <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                  Loading...
                </td>
              </tr>
            ) : leads.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                  No leads found
                </td>
              </tr>
            ) : (
              leads.map(lead => (
                <tr key={lead.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                    {new Date(lead.created_at).toLocaleDateString()}
                  </td>

                  <td className="px-4 py-3">
                    <div>
                      <div className="font-medium text-gray-900 flex items-center gap-2">
                        {lead.name}
                        {lead.is_high_value && (
                          <span className="px-2 py-0.5 text-xs font-medium bg-red-100 text-red-800 rounded-full">
                            High Value
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-500">{lead.email}</div>
                      {lead.company && (
                        <div className="text-sm text-gray-600">{lead.company}</div>
                      )}
                    </div>
                  </td>

                  <td className="px-4 py-3 whitespace-nowrap">
                    {getSourceBadge(lead.source)}
                  </td>

                  <td className="px-4 py-3">
                    {lead.source === 'api_key_request' ? (
                      <div className="text-sm">
                        <div className="font-medium">{lead.use_case || 'N/A'}</div>
                        <div className="text-gray-500">Volume: {lead.expected_volume || 'N/A'}</div>
                      </div>
                    ) : (
                      <div className="text-sm">
                        <div className="font-medium">{lead.subject || 'N/A'}</div>
                      </div>
                    )}
                  </td>

                  <td className="px-4 py-3 whitespace-nowrap">
                    {getStatusBadge(lead.status)}
                  </td>

                  <td className="px-4 py-3 whitespace-nowrap text-sm">
                    <div className="flex gap-2">
                      {lead.status === 'new' && (
                        <button
                          onClick={() => updateLeadStatus(lead.id, 'contacted')}
                          className="text-blue-600 hover:text-blue-800"
                          title="Mark as contacted"
                        >
                          Mark Contacted
                        </button>
                      )}

                      <a
                        href={`mailto:${lead.email}`}
                        className="text-green-600 hover:text-green-800"
                        title="Send email"
                      >
                        Email
                      </a>

                      <button
                        onClick={() => setSelectedLead(lead)}
                        className="text-gray-600 hover:text-gray-800"
                        title="View details"
                      >
                        Details
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {total > limit && (
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
          >
            Previous
          </button>

          <div className="px-4 py-2">
            Page {page + 1} of {Math.ceil(total / limit)}
          </div>

          <button
            onClick={() => setPage(p => p + 1)}
            disabled={(page + 1) * limit >= total}
            className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      )}

      {/* Lead Details Modal */}
      {selectedLead && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold">Lead Details</h3>
              <button
                onClick={() => setSelectedLead(null)}
                className="text-gray-500 hover:text-gray-700 text-xl"
              >
                &times;
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-500">Name</label>
                  <div className="text-gray-900">{selectedLead.name}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">Email</label>
                  <div className="text-gray-900">{selectedLead.email}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">Company</label>
                  <div className="text-gray-900">{selectedLead.company || 'N/A'}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">Source</label>
                  <div>{getSourceBadge(selectedLead.source)}</div>
                </div>
              </div>

              {selectedLead.source === 'api_key_request' && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-500">Use Case</label>
                    <div className="text-gray-900">{selectedLead.use_case || 'N/A'}</div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-500">Expected Volume</label>
                    <div className="text-gray-900">{selectedLead.expected_volume || 'N/A'}</div>
                  </div>
                </div>
              )}

              {selectedLead.source === 'contact_form' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-500">Subject</label>
                    <div className="text-gray-900">{selectedLead.subject || 'N/A'}</div>
                  </div>
                  {selectedLead.message && (
                    <div>
                      <label className="block text-sm font-medium text-gray-500">Message</label>
                      <div className="text-gray-900 bg-gray-50 p-3 rounded whitespace-pre-wrap">
                        {selectedLead.message}
                      </div>
                    </div>
                  )}
                </>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-500">Status</label>
                  <select
                    value={selectedLead.status}
                    onChange={(e) => {
                      updateLeadStatus(selectedLead.id, e.target.value)
                      setSelectedLead({ ...selectedLead, status: e.target.value })
                    }}
                    className="border rounded px-3 py-2 w-full mt-1"
                  >
                    <option value="new">New</option>
                    <option value="contacted">Contacted</option>
                    <option value="qualified">Qualified</option>
                    <option value="converted">Converted</option>
                    <option value="lost">Lost</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">Priority</label>
                  <div className="text-gray-900 mt-2">
                    {selectedLead.is_high_value ? (
                      <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
                        High Value
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">
                        Normal
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-500">Created</label>
                  <div className="text-gray-900">
                    {new Date(selectedLead.created_at).toLocaleString()}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500">Contacted</label>
                  <div className="text-gray-900">
                    {selectedLead.contacted_at
                      ? new Date(selectedLead.contacted_at).toLocaleString()
                      : 'Not yet'
                    }
                  </div>
                </div>
              </div>

              {selectedLead.internal_notes && (
                <div>
                  <label className="block text-sm font-medium text-gray-500">Internal Notes</label>
                  <div className="text-gray-900 bg-gray-50 p-3 rounded whitespace-pre-wrap">
                    {selectedLead.internal_notes}
                  </div>
                </div>
              )}

              <div className="flex gap-2 justify-end pt-4 border-t">
                <a
                  href={`mailto:${selectedLead.email}`}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                >
                  Send Email
                </a>
                <button
                  onClick={() => setSelectedLead(null)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
