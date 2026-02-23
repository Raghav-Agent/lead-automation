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
        alert('Email sent!')
      }
    }
  )

  const createWebsiteMutation = useMutation(
    () => axios.post(`${API_URL}/websites/create/${leadId}?template_type=modern`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['lead', leadId])
        queryClient.invalidateQueries('leads')
        alert('Website creation started!')
      }
    }
  )

  if (isLoading) return <div className="loading">Loading...</div>
  if (!lead) return <div className="not-found">Lead not found</div>

  const emails = emailsData?.campaigns || []
  const websites = websitesData?.websites || []

  return (
    <div className="lead-details">
      <button onClick={() => navigate('/')} className="btn btn-back">← Back to Dashboard</button>
      <div className="details-grid">
        {/* Lead Info */}
        <div className="card">
          <h2>Lead Information</h2>
          <div className="info-grid">
            <div>
              <label>Name:</label>
              <p>{lead.name}</p>
            </div>
            <div>
              <label>Business:</label>
              <p>{lead.business_name}</p>
            </div>
            <div>
              <label>Email:</label>
              <p><a href={`mailto:${lead.email}`}>{lead.email || 'N/A'}</a></p>
            </div>
            <div>
              <label>Phone:</label>
              <p>{lead.phone ? <a href={`tel:${lead.phone}`}>{lead.phone}</a> : 'N/A'}</p>
            </div>
            <div>
              <label>Niche:</label>
              <p>{lead.niche}</p>
            </div>
            <div>
              <label>Location:</label>
              <p>{lead.location}</p>
            </div>
            <div>
              <label>Status:</label>
              <p><span className={`badge badge-${lead.status}`}>{lead.status}</span></p>
            </div>
          </div>
        </div>

        {/* Website Section */}
        <div className="card">
          <h2>Website Prototype</h2>
          {websites.length > 0 ? (
            <div className="websites-list">
              {websites.map((site: any) => (
                <div key={site.id} className="website-item">
                  <p>Template: {site.template_type}</p>
                  <a href={`http://localhost:8000${site.website_url}`} target="_blank" rel="noopener noreferrer" className="btn btn-primary">
                    👁 View Website
                  </a>
                </div>
              ))}
            </div>
          ) : (
            <div>
              <p>No website created yet</p>
              <button onClick={() => createWebsiteMutation.mutate()} className="btn btn-primary" disabled={createWebsiteMutation.isLoading}>
                {createWebsiteMutation.isLoading ? '⏳ Creating...' : '🌐 Create Website'}
              </button>
            </div>
          )}
        </div>

        {/* Email Campaigns */}
        <div className="card">
          <h2>Email Campaigns</h2>
          {emails.length > 0 ? (
            <div className="campaigns-list">
              {emails.map((campaign: any) => (
                <div key={campaign.id} className="campaign-item">
                  <h4>{campaign.subject}</h4>
                  <p className="body-preview">{campaign.body.substring(0, 100)}...</p>
                  <p className="status">Status: <span className="badge">{campaign.status}</span></p>
                  <p className="date">Sent: {new Date(campaign.sent_at).toLocaleDateString()}</p>
                </div>
              ))}
            </div>
          ) : (
            <div>
              <p>No emails sent yet</p>
              <button onClick={() => sendEmailMutation.mutate()} className="btn btn-primary" disabled={sendEmailMutation.isLoading}>
                {sendEmailMutation.isLoading ? '⏳ Sending...' : '📧 Send Pitch Email'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
