import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { fetchDeviceStats } from '../utils/api'

const COLOR = (rate) => rate > 0.08 ? '#b91c1c' : rate > 0.04 ? '#b45309' : '#1a7a4a'

const LEGEND = [
  ['#b91c1c', '>8%',  'Critical'],
  ['#b45309', '4–8%', 'Elevated'],
  ['#1a7a4a', '<4%',  'Normal'],
]

function StatCard({ label, value, color, sub }) {
  return (
    <div style={{
      background: '#fff', border: '1px solid var(--border)',
      borderTop: `3px solid ${color}`,
      borderRadius: 10, padding: '16px 20px', flex: 1, minWidth: 120,
      boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
    }}>
      <div style={{ fontSize: 28, fontFamily: 'Catamaran, sans-serif', fontWeight: 800, color, lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 12.5, color: 'var(--text-muted)', marginTop: 5, fontWeight: 600 }}>{label}</div>
      {sub && <div style={{ fontSize: 11, color: 'var(--text-light)', marginTop: 2 }}>{sub}</div>}
    </div>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{
      background: '#fff', border: '1px solid var(--border)',
      borderRadius: 8, padding: '10px 14px',
      boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
    }}>
      <div style={{ color: 'var(--navy)', fontWeight: 700, fontSize: 13, marginBottom: 5 }}>{label}</div>
      <div style={{ fontSize: 12.5, color: 'var(--text-muted)' }}>
        Failure Rate: <strong style={{ color: COLOR(d.raw) }}>{d.failureRate}%</strong>
      </div>
      <div style={{ fontSize: 12, color: 'var(--text-light)', marginTop: 2 }}>
        {d.failures} failures / {d.total} total
      </div>
    </div>
  )
}

export default function DeviceHealthDashboard() {
  const [stats, setStats] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDeviceStats().then(d => setStats(d.stats || [])).catch(() => setStats([])).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ padding: '40px 20px', textAlign: 'center' }}>
      <div style={{ width: 28, height: 28, border: '3px solid var(--blue-mid)', borderTopColor: 'var(--blue)', borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 12px' }} />
      <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>Loading device statistics…</div>
    </div>
  )

  if (!stats.length) return (
    <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
      No device data available. Run ingestion first.
    </div>
  )

  const chartData = stats.map(s => ({
    name: s.device.replace(' System','').replace(' Scanner','').replace(' Machine',''),
    failureRate: parseFloat((s.failure_rate * 100).toFixed(1)),
    failures: s.failures, total: s.total, raw: s.failure_rate,
  }))

  const critical  = stats.filter(s => s.failure_rate > 0.08).length
  const elevated  = stats.filter(s => s.failure_rate > 0.04 && s.failure_rate <= 0.08).length
  const normal    = stats.length - critical - elevated

  return (
    <div>
      {/* Stat cards */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 28, flexWrap: 'wrap' }}>
        <StatCard label="Total Device Types" value={stats.length}  color="var(--blue)"    />
        <StatCard label="Critical Risk"       value={critical}      color="var(--danger)"  sub=">8% failure rate" />
        <StatCard label="Elevated Risk"       value={elevated}      color="var(--warning)" sub="4–8% failure rate" />
        <StatCard label="Normal"              value={normal}        color="var(--success)" sub="<4% failure rate" />
      </div>

      <div style={{ color: 'var(--navy)', fontSize: 14, fontWeight: 700, fontFamily: 'Catamaran, sans-serif', marginBottom: 16 }}>
        Failure Rate by Equipment Type
      </div>

      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={chartData} margin={{ top: 0, right: 10, left: -10, bottom: 65 }}>
          <XAxis dataKey="name" tick={{ fill: 'var(--text-light)', fontSize: 10.5 }} angle={-40} textAnchor="end" interval={0} />
          <YAxis tick={{ fill: 'var(--text-light)', fontSize: 10.5 }} tickFormatter={v => `${v}%`} axisLine={{ stroke: 'var(--border)' }} tickLine={false} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(45,74,58,0.04)' }} />
          <Bar dataKey="failureRate" radius={[4,4,0,0]} maxBarSize={38}>
            {chartData.map((e, i) => <Cell key={i} fill={COLOR(e.raw)} fillOpacity={0.85} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div style={{ display: 'flex', gap: 20, marginTop: 8, flexWrap: 'wrap' }}>
        {LEGEND.map(([color, range, label]) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
            <div style={{ width: 10, height: 10, borderRadius: 3, background: color }} />
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              <span style={{ color, fontWeight: 700 }}>{range}</span> — {label}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
