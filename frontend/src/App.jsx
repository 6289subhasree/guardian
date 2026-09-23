import { useCallback, useEffect, useMemo, useState } from 'react'
import { Activity, ArrowRight, Cpu, GitBranch, LockKeyhole, Play, Plus, Radio, RotateCcw, Shield, ShieldAlert, Wifi, Zap } from 'lucide-react'
import './App.css'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const empty = { devices: [], detections: [], observations: [], telemetry: [], graph: { nodes: [], edges: [] }, actions: [], mode: { mode: 'record' } }

async function request(path, options) {
  const response = await fetch(`${API}${path}`, options)
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail || `${response.status} ${response.statusText}`)
  return data
}

function statusLabel(status) {
  return status === 'isolated' ? 'Isolated' : status === 'online' ? 'Online' : 'Offline'
}

function formatTime(date) {
  return date ? new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '—'
}

function NetworkGraph({ graph, devices }) {
  const nodes = graph.nodes || []
  const count = nodes.length
  const positions = Object.fromEntries(nodes.map((node, i) => [node.device_id, {
    x: 50 + 32 * Math.cos((2 * Math.PI * i / Math.max(count, 1)) - Math.PI / 2),
    y: 50 + 31 * Math.sin((2 * Math.PI * i / Math.max(count, 1)) - Math.PI / 2),
  }]))
  if (!count) return <div className="empty-graph"><GitBranch size={28} /><strong>No graph yet</strong><span>Capture traffic from registered devices to form a graph.</span></div>
  return <div className="graph-stage">
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Device communication graph">
      {graph.edges.map((edge, i) => {
        const from = positions[edge.source_device_id]
        const to = positions[edge.destination_device_id]
        return from && to && <line key={`${i}-${edge.source_device_id}`} x1={from.x} y1={from.y} x2={to.x} y2={to.y} />
      })}
    </svg>
    {nodes.map((node) => {
      const device = devices.find((item) => item.device_id === node.device_id)
      const p = positions[node.device_id]
      return <div key={node.device_id} className={`graph-node ${device?.status === 'isolated' ? 'danger' : ''}`} style={{ left: `${p.x}%`, top: `${p.y}%` }} title={`${node.device_id}: ${node.features[0]} observed packets`}>
        <Cpu size={19} /><span>{node.device_id}</span>
      </div>
    })}
    <div className="graph-center"><Shield size={22} /><span>Network</span></div>
  </div>
}

function App() {
  const [data, setData] = useState(empty)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busy, setBusy] = useState(false)
  const [updated, setUpdated] = useState(null)
  const [showRegister, setShowRegister] = useState(false)
  const [newDevice, setNewDevice] = useState({ device_id: '', ip_address: '', firmware_version: 'demo-1' })

  const refresh = useCallback(async () => {
    try {
      const paths = ['/devices', '/detections?limit=30', '/network/observations', '/telemetry', '/graph', '/responses?limit=30', '/responses/mode']
      const results = await Promise.all(paths.map((path) => request(path)))
      setData(Object.fromEntries(['devices', 'detections', 'observations', 'telemetry', 'graph', 'actions', 'mode'].map((key, i) => [key, results[i]])))
      setUpdated(new Date())
      setError('')
    } catch (cause) { setError(cause.message) }
  }, [])

  useEffect(() => {
    const initial = setTimeout(refresh, 0)
    const interval = setInterval(refresh, 5000)
    return () => { clearTimeout(initial); clearInterval(interval) }
  }, [refresh])

  async function act(path, success) {
    setBusy(true); setNotice('')
    try {
      await request(path, { method: 'POST' })
      setNotice(success)
      await refresh()
    } catch (cause) { setNotice(cause.message) }
    finally { setBusy(false) }
  }

  async function register(event) {
    event.preventDefault()
    setBusy(true); setNotice('')
    try {
      await request('/devices/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(newDevice) })
      setNotice(`${newDevice.device_id} registered. Start its heartbeat and MQTT telemetry.`)
      setShowRegister(false)
      setNewDevice({ device_id: '', ip_address: '', firmware_version: 'demo-1' })
      await refresh()
    } catch (cause) { setNotice(cause.message) }
    finally { setBusy(false) }
  }

  const latestByDevice = useMemo(() => Object.fromEntries([...data.detections].reverse().map((d) => [d.device_id, d])), [data.detections])
  const suspicious = Object.values(latestByDevice).filter((d) => d.classification === 'SUSPICIOUS')
  const latest = data.detections[0]
  const isolated = data.devices.filter((d) => d.status === 'isolated')
  const cards = [
    { label: 'Registered devices', value: data.devices.length, detail: `${data.devices.filter((d) => d.status === 'online').length} online`, icon: Cpu },
    { label: 'Observed packets', value: data.observations.length, detail: 'Most recent 5 minutes', icon: Activity },
    { label: 'Devices at risk', value: suspicious.length, detail: 'Latest result per device', icon: ShieldAlert },
    { label: 'MQTT blocked', value: isolated.length, detail: data.mode.mode === 'firewall' ? 'Host firewall mode' : 'Enforcement disabled', icon: LockKeyhole },
  ]

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="logo"><div className="logo-mark"><Shield size={23} /></div><div><strong>GUARDIAN<span>—X</span></strong><small>IoT security workspace</small></div></div>
      <div className="nav-label">WORKSPACE</div>
      <div className="nav-item active"><Activity size={17} /> Overview</div>
      <div className="nav-item"><GitBranch size={17} /> Device graph</div>
      <div className="nav-item"><ShieldAlert size={17} /> Detection log</div>
      <div className="sidebar-bottom"><span className={`connection-dot ${error ? 'off' : ''}`} />{error ? 'Backend unavailable' : 'Backend connected'}<small>{updated ? `Updated ${formatTime(updated)}` : 'Connecting…'}</small></div>
    </aside>

    <main className="content">
      <div className="topline"><span>SECURITY OPERATIONS / OVERVIEW</span><div className="topline-right"><span className="mode-pill"><span className="connection-dot" />{data.mode.mode === 'firewall' ? 'FIREWALL ARMED' : 'MONITOR ONLY'}</span><span>{new Date().toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</span></div></div>
      <div className="heading"><div><p className="eyebrow">NETWORK COMMAND CENTER</p><h1>Know what your devices are doing.</h1><p className="lede">Packet observations, graph-based risk scoring, and auditable response in one view.</p></div><button className="primary-button" disabled={busy} onClick={() => act('/detections/run', 'Detection cycle completed.')}><Play size={16} fill="currentColor" /> Run detection</button></div>
      {error && <div className="banner error">Could not reach the backend: {error}. Check the API server at {API}.</div>}
      {notice && <div className="banner info">{notice}</div>}
      <div className="metrics">{cards.map(({ label, value, detail, icon: Icon }) => <div className="metric" key={label}><div className="metric-top"><span>{label}</span><Icon size={18} /></div><strong>{value}</strong><small>{detail}</small></div>)}</div>

      <div className="main-grid">
        <section className="panel graph-panel"><div className="panel-title"><div><p className="eyebrow">01 / TOPOLOGY</p><h2>Device communication graph</h2></div><span className="tag">{data.graph.edges.length} RELATIONSHIPS</span></div><NetworkGraph graph={data.graph} devices={data.devices} /><div className="panel-foot"><span className="legend-dot teal" /> Device node <span className="legend-line" /> Direct or shared destination relationship <span className="legend-dot red" /> Isolated</div></section>
        <section className="panel signals-panel"><div className="panel-title"><div><p className="eyebrow">02 / LIVE SIGNAL</p><h2>Detection status</h2></div><Zap size={19} /></div><div className={`signal-box ${latest?.classification === 'SUSPICIOUS' ? 'threat' : ''}`}><div className="signal-icon"><ShieldAlert size={27} /></div><p>{latest ? latest.classification : 'AWAITING DATA'}</p><h3>{latest ? `Latest: ${latest.device_id}` : 'No score yet'}</h3><span>{latest ? `Scored at ${formatTime(latest.created_at)}` : 'Run detection after capturing traffic.'}</span></div><div className="risk-line"><span>Latest model score</span><strong>{latest ? `${Math.round(latest.risk_score * 100)}%` : '—'}</strong></div><div className="risk-track"><div style={{ width: `${(latest?.risk_score || 0) * 100}%` }} /></div><p className="fineprint">Experimental model trained on synthetic samples. This score is not a calibrated probability of compromise.</p></section>
      </div>

      <div className="lower-grid">
        <section className="panel"><div className="panel-title"><div><p className="eyebrow">03 / INVENTORY</p><h2>Connected devices</h2></div><button className="outline-button" onClick={() => setShowRegister(!showRegister)}><Plus size={14} /> Add device</button></div>{showRegister && <form className="register-form" onSubmit={register}><input required placeholder="Device ID (ESP32-001)" value={newDevice.device_id} onChange={(e) => setNewDevice({ ...newDevice, device_id: e.target.value })} /><input required placeholder="Device IP from Serial Monitor" value={newDevice.ip_address} onChange={(e) => setNewDevice({ ...newDevice, ip_address: e.target.value })} /><button disabled={busy}>Register</button></form>}<div className="device-table"><div className="table-head"><span>DEVICE</span><span>IP ADDRESS</span><span>STATE</span><span>RISK</span><span>ACTION</span></div>{data.devices.length ? data.devices.map((device) => <div className="table-row" key={device.device_id}><strong><Cpu size={16} /> {device.device_id}</strong><span>{device.ip_address}</span><span className={`state ${device.status}`}>{statusLabel(device.status)}</span><span>{latestByDevice[device.device_id] ? `${Math.round(latestByDevice[device.device_id].risk_score * 100)}%` : '—'}</span><div>{device.status === 'isolated' ? <button className="text-button" disabled={busy} onClick={() => act(`/recovery/${encodeURIComponent(device.device_id)}`, `${device.device_id} recovered.`)}><RotateCcw size={14} /> Recover</button> : data.mode.mode === 'firewall' ? <button className="text-button" disabled={busy} onClick={() => act(`/responses/${encodeURIComponent(device.device_id)}/enforce`, `MQTT block requested for ${device.device_id}.`)}>Block MQTT</button> : <span className="muted">—</span>}</div></div>) : <div className="empty-row">No devices registered. Add the ESP32 IPs shown in Serial Monitor.</div>}</div></section>
        <section className="panel activity-panel"><div className="panel-title"><div><p className="eyebrow">04 / AUDIT TRAIL</p><h2>Recent activity</h2></div><Radio size={18} /></div><div className="timeline">{data.actions.length ? data.actions.slice(0, 5).map((action) => <div className="timeline-item" key={action.id}><span className={`timeline-dot ${action.outcome === 'FAILED' ? 'bad' : ''}`} /><div><strong>{action.action.replaceAll('_', ' ')} · {action.device_id}</strong><p>{action.detail}</p><small>{formatTime(action.created_at)} · {action.outcome}</small></div></div>) : <div className="empty-row">No response actions recorded yet.</div>}</div></section>
      </div>
      <section className="panel telemetry-panel"><div className="panel-title"><div><p className="eyebrow">05 / DEVICE TELEMETRY</p><h2>Latest MQTT readings</h2></div><span className="tag">{data.telemetry.length} SAMPLES</span></div><div className="telemetry-items">{data.telemetry.length ? data.telemetry.slice(0, 6).map((sample, index) => <div className="telemetry-item" key={`${sample.device_id}-${sample.timestamp}-${index}`}><span><Radio size={15} /> {sample.device_id}</span><strong>{sample.temperature.toFixed(1)}°C</strong><strong>{sample.humidity.toFixed(1)}% RH</strong><small>{formatTime(sample.timestamp)}</small></div>) : <div className="empty-row">Waiting for MQTT telemetry. The demo sketch sends fixed test readings.</div>}</div></section>
      <footer><Wifi size={15} /> Telemetry samples: {data.telemetry.length} <ArrowRight size={15} /> {data.mode.mode === 'firewall' ? 'Only MQTT ingress to this host is blocked.' : 'Firewall enforcement is off. Alerts are recorded only.'}</footer>
    </main>
  </div>
}

export default App
