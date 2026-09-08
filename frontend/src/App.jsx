import React, { useState, useEffect } from 'react'

const SERVICES = [
  { name: 'Backend API', url: 'http://localhost:8000/health' },
  { name: 'Identity Service', url: 'http://localhost:8101/health' },
  { name: 'Municipality Service', url: 'http://localhost:8102/health' },
  { name: 'Property Service', url: 'http://localhost:8103/health' },
  { name: 'Tax Service', url: 'http://localhost:8104/health' },
]

export default function App() {
  const [statuses, setStatuses] = useState({})
  const [loading, setLoading] = useState(false)

  const checkHealth = async () => {
    setLoading(true)
    const results = {}

    for (const service of SERVICES) {
      try {
        const res = await fetch(service.url, { signal: AbortSignal.timeout(3000) })
        if (res.ok) {
          const data = await res.json()
          results[service.name] = { online: true, data }
        } else {
          results[service.name] = { online: false, error: `HTTP ${res.status}` }
        }
      } catch (err) {
        results[service.name] = { online: false, error: 'Offline / Unreachable' }
      }
    }

    setStatuses(results)
    setLoading(false)
  }

  useEffect(() => {
    checkHealth()
  }, [])

  return (
    <div className="container">
      <header className="header">
        <div className="brand">
          <div className="logo-badge">GM</div>
          <div className="title-group">
            <h1>GovMesh SIH26129 Platform</h1>
            <p>Interoperable Government-Service Foundation</p>
          </div>
        </div>
        <div className="badge badge-success">
          Foundation Stack Operational
        </div>
      </header>

      <div className="grid">
        {/* Architecture & Tech Stack Card */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Finalized Stack Architecture</h2>
          </div>
          <div className="tech-stack-list">
            <div className="tech-item">
              <span className="tech-label">Frontend</span>
              <span className="tech-value">React + Vite + JS</span>
            </div>
            <div className="tech-item">
              <span className="tech-label">Backend</span>
              <span className="tech-value">Python + FastAPI</span>
            </div>
            <div className="tech-item">
              <span className="tech-label">Database</span>
              <span className="tech-value">PostgreSQL</span>
            </div>
            <div className="tech-item">
              <span className="tech-label">ORM & Migrations</span>
              <span className="tech-value">SQLAlchemy + Alembic</span>
            </div>
            <div className="tech-item">
              <span className="tech-label">Cache / Events</span>
              <span className="tech-value">Redis</span>
            </div>
            <div className="tech-item">
              <span className="tech-label">Auth</span>
              <span className="tech-value">JWT</span>
            </div>
          </div>
        </div>

        {/* System Services Health Card */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Services Health Monitor</h2>
            <button className="btn" onClick={checkHealth} disabled={loading}>
              {loading ? 'Checking...' : 'Refresh Status'}
            </button>
          </div>
          <div className="status-list">
            {SERVICES.map((s) => {
              const st = statuses[s.name]
              return (
                <div className="status-item" key={s.name}>
                  <div>
                    <div className="status-name">{s.name}</div>
                    <div className="status-url">{s.url}</div>
                  </div>
                  {st ? (
                    <span className={`badge ${st.online ? 'badge-success' : 'badge-warning'}`}>
                      {st.online ? 'Online' : st.error}
                    </span>
                  ) : (
                    <span className="badge badge-warning">Checking...</span>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>

      <footer className="footer">
        GovMesh Interoperability Platform &bull; SIH 26129 Hackathon Starter Foundation
      </footer>
    </div>
  )
}
