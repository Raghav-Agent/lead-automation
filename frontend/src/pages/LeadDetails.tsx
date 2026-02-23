import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import axios from 'axios'
import '../styles/LeadDetails.css'

const API_URL = 'http://localhost:8000/api'

export default function LeadDetails() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const leadId = parseInt(id || '0')

  const { data: lead, isLoading } = useQuery(['lead', leadId], () =>
    axios.get(`${API_URL}/leads/${leadId}`).then(res => res.data)
  )

  const { data: emailsData } = useQuery(['lead-emails', leadId], () =>
    axios.get(`${API_URL}/emails/${leadId}`).then(res => res.data)
  )

  const { data: websitesData } = useQuery(['lead-websites', leadId], () =>
    axios.get(`${API_URL}/websites/${leadId}`).then(res => res.data)
  )

  const sendEmailMutation = useMutation(
    () => axios.post(`${API_URL}/emails/send/${leadId}`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['lead', leadId])
        queryClient.invalidateQueries('leads')
      }
    }
  )

  const createWebsiteMutation = useMutation(
    (template_type: string) => axios.post(`${API_URL}/websites/create/${leadId}?template_type=${template_type}`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['lead', leadId])
        queryClient.invalidateQueries('leads')
      }
    }
  )

  if (isLoading) return <div className="loading">Loading...</div>
  if (!lead) return <div className="not-found">Lead not found</div>

  const emails = emailsData?.campaigns || []
  const websites = websitesData?.websites || []

  return (
    <div className="lead-details">
      <div className="header">
        <button className="back-btn" onClick={() => navigate('/')}>← Back to Dashboard</button>
        <h1>{lead.business_name}</h1>
        <span className={`badge badge-${lead.status}`}>{lead.status}</span>
      </div>

      <div className="details-grid">
        <section className="card">
          <h2>Contact Information</h2>
          <p><strong>Name:</strong> {lead.name}</p>
          <p><strong>Email:</strong> {lead.email || <em>None</em>}</p>
          <p><strong>Phone:</strong> {lead.phone || <em>None</em>}</p>
          <p><strong>Address:</strong> {lead.address || <em>None</em>}</p>
          <p><strong>Location:</strong> {lead.location}</p>
          <p><strong>Website:</strong> {lead.website_url || <em>None</em>}</p>
          <p><strong>Business Type:</strong> {lead.business_type}</p>
          <p><strong>Niche:</strong> {lead.niche}</p>
        </section>

        <section className="card">
          <h2>Actions</h2>
          <div className="actions">
            {lead.email ? (
              <button
                className="btn btn-primary"
                onClick={() => sendEmailMutation.mutate()}
                disabled={sendEmailMutation.isLoading || lead.email_sent}
              >
                {sendEmailMutation.isLoading ? 'Sending...' : lead.email_sent ? '✓ Email Sent' : '📧 Send Pitch Email'}
              </button>
            ) : (
              <p className="muted">No email address available</p>
            )}
            {lead.prototype_created && websites.length > 0 ? (
              <a href={`http://localhost:8000${lead.prototype_url}`} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
                🌐 View Website
              </a>
            ) : (
              <div>
                <button
                  className="btn btn-secondary"
                  onClick={() => createWebsiteMutation.mutate('modern')}
                  disabled={createWebsiteMutation.isLoading}
                >
                  {createWebsiteMutation.isLoading ? 'Building...' : '🌐 Create Website'}
                </button>
              </div>
            )}
          </div>
        </section>

        {emails.length > 0 && (
          <section className="card full-width">
            <h2>Email History</h2>
            <ul className="email-list">
              {emails.map((email: any) => (
                <li key={email.id}>
                  <strong>{email.subject}</strong> – {email.status} – {new Date(email.sent_at).toLocaleString()}
                </li>
              ))}
            </ul>
          </section>
        )}

        {websites.length > 0 && (
          <section className="card full-width">
            <h2>Websites</h2>
            <ul className="website-list">
              {websites.map((site: any) => (
                <li key={site.id}>
                  <a href={`http://localhost:8000${site.website_url}`} target="_blank" rel="noopener noreferrer">
                    {site.template_type} – Created {new Date(site.created_at).toLocaleDateString()}
                  </a>
                </li>
              ))}
            </ul>
          </section>
        )}

        <section className="card full-width">
          <h2>Notes</h2>
          <p>{lead.notes || 'No notes.'}</p>
        </section>
      </div>
    </div>
  )
}
