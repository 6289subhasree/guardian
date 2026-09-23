import { useEffect, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Network,
  Shield,
  ShieldAlert,
  Wifi,
} from 'lucide-react'
import './App.css'
function App() {
  const [devices, setDevices] = useState([])
  const [detections, setDetections] = useState([])
  const [observations, setObservations] = useState([])
  const [error, setError] = useState('')

  const load = async () => {
    try {
      const responses = await Promise.all([
        fetch('http://127.0.0.1:8000/devices'),
        fetch('http://127.0.0.1:8000/detections'),
        fetch('http://127.0.0.1:8000/network/observations'),
      ])
      if (responses.some((response) => !response.ok)) throw new Error('Backend request failed')
      const [nextDevices, nextDetections, nextObservations] = await Promise.all(responses.map((response) => response.json()))
      setDevices(nextDevices)
      setDetections(nextDetections)
      setObservations(nextObservations)
      setError('')
    } catch (cause) {
      setError(cause.message)
    }
  }

  useEffect(() => {
    const initial = setTimeout(load, 0)
    const timer = setInterval(load, 5000)
    return () => { clearTimeout(initial); clearInterval(timer) }
  }, [])
  const latest = detections[0]
  const suspicious = detections.filter((detection) => detection.classification === 'SUSPICIOUS')
  const isolated = devices.filter((device) => device.status === 'isolated')
  return (
    <div className="dashboard">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <Shield size={24} />
          </div>
          <div>
            <h1>GUARDIAN-X</h1>
            <span>AI-Powered IoT Security Platform</span>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot online" />
          <span>{error ? 'Backend unavailable' : 'Backend connected'}</span>
        </div>
      </header>

      <main className="main-content">
        <section className="page-heading">
          <div>
            <p className="eyebrow">SECURITY COMMAND CENTER</p>
            <h2>Network Overview</h2>
            <p className="subtitle">
              Device monitoring, recorded detections and response state. Updates every five seconds.
            </p>
          </div>

          <div className="monitoring-badge">
            <Activity size={17} />
            {error || 'Dashboard connected'}
          </div>
        </section>

        <section className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon blue">
              <Cpu size={21} />
            </div>
            <div>
              <span>Registered Devices</span>
              <strong>{devices.length}</strong>
              <small>IoT devices</small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon green">
              <Wifi size={21} />
            </div>
            <div>
              <span>Online Devices</span>
              <strong>{devices.filter((device) => device.status === 'online').length}</strong>
              <small>Currently connected</small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon purple">
              <Network size={21} />
            </div>
            <div>
              <span>Network Activity</span>
              <strong>{observations.length}</strong>
              <small>Observed packets in this session</small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon green">
              <ShieldAlert size={21} />
            </div>
            <div>
              <span>Threat Status</span>
              <strong>{suspicious.length ? 'Suspicious' : latest ? 'Normal' : 'Unknown'}</strong>
              <small>{detections.length} recorded detections</small>
            </div>
          </div>
        </section>

        <section className="content-grid">
          <div className="panel devices-panel">
            <div className="panel-header">
              <div>
                <h3>IoT Devices</h3>
                <p>Registered devices and current security state</p>
              </div>
              <Cpu size={20} />
            </div>

            <div className="device-list">
  {devices.map((device) => (
    <div className="device-row" key={device.device_id}>
      <div className="device-info">
        <div className="device-avatar">
          <Cpu size={18} />
        </div>
        <div>
          <strong>{device.device_id}</strong>
          <span>{device.ip_address}</span>
        </div>
      </div>

      <div className="device-state">
        <span
          className={`status-dot ${
            device.status === 'online' ? 'online' : 'offline'
          }`}
        />
        {device.status}
      </div>
    </div>
  ))}
</div>
</div>
          <div className="panel detection-panel">
            <div className="panel-header">
              <div>
                <h3>AI Detection</h3>
                <p>GraphSAGE threat analysis</p>
              </div>
              <ShieldAlert size={20} />
            </div>

            <div className="detection-state">
              <div className="check-icon">
                <CheckCircle2 size={34} />
              </div>
              <h4>{latest ? latest.classification : 'No detection run yet'}</h4>
              <p>{latest ? `Latest device: ${latest.device_id}` : 'Capture traffic, then run a detection.'}</p>
            </div>

            <div className="risk-row">
              <span>Current Risk Score</span>
              <strong>{latest ? latest.risk_score.toFixed(3) : '—'}</strong>
            </div>

            <div className="risk-bar">
              <div className="risk-fill" style={{ width: `${(latest?.risk_score || 0) * 100}%` }} />
            </div>
          </div>
        </section>

        <section className="panel response-panel">
          <div className="panel-header">
            <div>
              <h3>Autonomous Response</h3>
              <p>Isolation and recovery activity</p>
            </div>
            <AlertTriangle size={20} />
          </div>

          <div className="response-content">
            <div className="response-status">
              <CheckCircle2 size={22} />
              <div>
                <strong>{isolated.length ? `${isolated.length} device(s) flagged isolated` : 'No devices flagged isolated'}</strong>
                <span>{isolated.length ? isolated.map((device) => device.device_id).join(', ') : 'Status reflects backend records.'}</span>
              </div>
            </div>

            <div className="pipeline">
              <span>Detection</span>
              <span>→</span>
              <span>Risk Assessment</span>
              <span>→</span>
              <span>Isolation</span>
              <span>→</span>
              <span>Recovery</span>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
