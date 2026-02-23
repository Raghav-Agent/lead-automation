import { useState } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import './SearchLeads.css'

const API_URL = 'http://localhost:8000/api'

export default function SearchLeads() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    niche: '',
    location: '',
    business_type: '',
    radius_km: 50
  })
  const [message, setMessage] = useState('')

  const searchMutation = useMutation(
    () => axios.post(`${API_URL}/leads/search`, formData),
    {
      onSuccess: (data) => {
        setMessage('🔍 Searching... This may take a few minutes.')
        setTimeout(() => {
          setMessage('✅ Search complete! Leads have been added to your dashboard.')
          queryClient.invalidateQueries('leads')
          navigate('/')
        }, 5000)
      },
      onError: (error: any) => {
        setMessage(`❌ Error: ${error.response?.data?.detail || 'Unknown error'}`)
      }
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.niche || !formData.location) {
      alert('Please fill in niche and location')
      return
    }
    searchMutation.mutate()
  }

  return (
    <div className="search-container">
      <div className="search-card">
        <h1>🔎 Find New Leads</h1>
        <p>Autonomous agent will search for businesses in your niche</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Business Niche *</label>
            <input
              type="text"
              placeholder="e.g., Web Design, Plumbing, Fitness"
              value={formData.niche}
              onChange={(e) => setFormData({ ...formData, niche: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Location *</label>
            <input
              type="text"
              placeholder="e.g., New York, USA"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Business Type</label>
            <select
              value={formData.business_type}
              onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
            >
              <option value="">Any</option>
              <option value="B2B">B2B</option>
              <option value="B2C">B2C</option>
              <option value="Service">Service</option>
              <option value="Retail">Retail</option>
            </select>
          </div>
          <div className="form-group">
            <label>Search Radius (km)</label>
            <input
              type="number"
              value={formData.radius_km}
              onChange={(e) => setFormData({ ...formData, radius_km: parseInt(e.target.value) })}
              min="1"
              max="500"
            />
          </div>
          <button
            type="submit"
            className="btn btn-primary btn-large"
            disabled={searchMutation.isLoading}
          >
            {searchMutation.isLoading ? '⏳ Searching...' : '🚀 Start Search'}
          </button>
        </form>
        {message && <div className="message">{message}</div>}
      </div>
    </div>
  )
}
