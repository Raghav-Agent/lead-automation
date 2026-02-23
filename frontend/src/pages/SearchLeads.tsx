import { useState } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import './SearchLeads.css'

const API_URL = 'http://localhost:8000/api'

export default function SearchLeads() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form, setForm] = useState({
    niche: '',
    location: '',
    business_type: ''
  })

  const searchMutation = useMutation(
    (data: typeof form) => axios.post(`${API_URL}/leads/search`, data),
    {
      onSuccess: () => {
        alert('Lead search started! Check dashboard for results.')
        navigate('/')
      }
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    searchMutation.mutate(form)
  }

  return (
    <div className="search-leads">
      <h1>🔍 Search New Leads</h1>
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-group">
          <label>Niche (e.g., dental clinics, restaurants)</label>
          <input
            type="text"
            value={form.niche}
            onChange={(e) => setForm({ ...form, niche: e.target.value })}
            required
            placeholder="dental clinics"
          />
        </div>
        <div className="form-group">
          <label>Location (city, region)</label>
          <input
            type="text"
            value={form.location}
            onChange={(e) => setForm({ ...form, location: e.target.value })}
            required
            placeholder="Mumbai, India"
          />
        </div>
        <div className="form-group">
          <label>Business Type (optional)</label>
          <input
            type="text"
            value={form.business_type}
            onChange={(e) => setForm({ ...form, business_type: e.target.value })}
            placeholder="e.g., clinic, studio"
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={searchMutation.isLoading}>
          {searchMutation.isLoading ? 'Searching...' : 'Start Search'}
        </button>
      </form>
      <p className="info">
        This will use OSM and Brave Search to find businesses. Enrichment runs automatically to find contact details.
      </p>
    </div>
  )
}
