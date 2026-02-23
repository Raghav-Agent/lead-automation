import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import axios from 'axios'
import { Link, useParams } from 'react-router-dom'
import './Dashboard.css'

const API_URL = 'http://localhost:8000/api'

interface Lead {
  id: number
  name: string
  email?: string
  phone?: string
  business_type: string
  business_name: string
  location: string
  status: string
  email_sent: boolean
  prototype_created: boolean
  prototype_url?: string
}

interface DashboardStats {
  total_leads: number
  emails_sent: number
  websites_created: number
  status_breakdown: { [key: string]: number }
  conversion_rate: number
}

export default function Dashboard() {
  const queryClient = useQueryClient()
  const { data: stats } = useQuery<DashboardStats>('dashboard-stats', () =>
    axios.get(`${API_URL}/dashboard/stats`).then(res => res.data)
  )
  const [filters, setFilters] = useState({ niche: '', location: '' })
  const { data: leadsData } = useQuery(['leads', filters], () =>
    axios.get(`${API_URL}/leads?limit=100${filters.niche ? `&niche=${filters.niche}` : ''}${filters.location ? `&location=${filters.location}` : ''}`).then(res => res.data)
  )

  const sendEmailMutation = useMutation(
    (leadId: number) => axios.post(`${API_URL}/emails/send/${leadId}`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('leads')
        alert('Email queued for sending!')
      }
    }
  )

  const createWebsiteMutation = useMutation(
    (leadId: number) => axios.post(`${API_URL}/websites/create/${leadId}?template_type=modern`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('leads')
        alert('Website creation started!')
      }
    }
  )

  const leads: Lead[] = leadsData?.leads || []

  return (
    <div className="dashboard">
      <div className="header">
        <h1>🚀 Autonomous Lead Generator</h1>
        <Link to="/search" className="btn btn-primary">Search New Leads</Link>
      </div>

      {/* Stats */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total_leads}</div>
            <div className="stat-label">Total Leads</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.emails_sent}</div>
            <div className="stat-label">Emails Sent</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.websites_created}</div>
            <div className="stat-label">Websites Created</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.conversion_rate.toFixed(1)}%</div>
            <div className="stat-label">Conversion Rate</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="filters">
        <input
          type="text"
          placeholder="Filter by niche..."
          value={filters.niche}
          onChange={(e) => setFilters({ ...filters, niche: e.target.value })}
        />
        <input
          type="text"
          placeholder="Filter by location..."
          value={filters.location}
          onChange={(e) => setFilters({ ...filters, location: e.target.value })}
        />
      </div>

      {/* Leads Table */}
      <div className="leads-container">
        <table className="leads-table">
          <thead>
            <tr>
              <th>Business Name</th>
              <th>Contact</th>
              <th>Niche</th>
              <th>Location</th>
              <th>Type</th>
              <th>Status</th>
              <th>Email</th>
              <th>Website</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => (
              <tr key={lead.id} className={`status-${lead.status}`}>
                <td>
                  <Link to={`/leads/${lead.id}`} className="lead-name">
                    {lead.business_name}
                  </Link>
                </td>
                <td>
                  <div className="contact-info">
                    <div>{lead.name}</div>
                    {lead.phone && <div className="phone">☎ {lead.phone}</div>}
                  </div>
                </td>
                <td>{lead.niche}</td>
                <td>{lead.location}</td>
                <td>{lead.business_type}</td>
                <td>
                  <span className={`badge badge-${lead.status}`}>{lead.status}</span>
                </td>
                <td>
                  {lead.email_sent ? (
                    <span className="badge badge-success">✓ Sent</span>
                  ) : (
                    <button
                      className="btn btn-small btn-email"
                      onClick={() => sendEmailMutation.mutate(lead.id)}
                      disabled={sendEmailMutation.isLoading || !lead.email}
                    >
                      📧 Send Email
                    </button>
                  )}
                </td>
                <td>
                  {lead.prototype_created && lead.prototype_url ? (
                    <a href={`http://localhost:8000${lead.prototype_url}`} target="_blank" rel="noopener noreferrer" className="btn btn-small btn-view">
                      👁 View
                    </a>
                  ) : (
                    <button
                      className="btn btn-small btn-create"
                      onClick={() => createWebsiteMutation.mutate(lead.id)}
                      disabled={createWebsiteMutation.isLoading}
                    >
                      🌐 Create
                    </button>
                  )}
                </td>
                <td>
                  <Link to={`/leads/${lead.id}`} className="btn btn-small">Details</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
