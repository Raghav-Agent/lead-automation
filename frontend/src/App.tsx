import { Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import SearchLeads from './pages/SearchLeads'
import LeadDetails from './pages/LeadDetails'
import './App.css'

function App() {
  return (
    <div className="app">
      <nav className="nav">
        <Link to="/" className="nav-brand">🚀 Lead Generator</Link>
        <div className="nav-links">
          <Link to="/">Dashboard</Link>
          <Link to="/search">Search Leads</Link>
        </div>
      </nav>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/search" element={<SearchLeads />} />
          <Route path="/leads/:id" element={<LeadDetails />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
