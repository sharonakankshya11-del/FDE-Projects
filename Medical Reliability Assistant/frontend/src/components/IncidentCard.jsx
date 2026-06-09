import { AlertTriangle, Info, Zap, Activity } from 'lucide-react'

const SEV = {
  high:   { accent: 'var(--danger)',  bg: 'var(--danger-bg)',  bd: 'var(--danger-bd)',  icon: AlertTriangle },
  medium: { accent: 'var(--warning)', bg: 'var(--warning-bg)', bd: 'var(--warning-bd)', icon: Zap },
  low:    { accent: 'var(--success)', bg: 'var(--success-bg)', bd: 'var(--success-bd)', icon: Activity },
  info:   { accent: 'var(--blue)',    bg: 'var(--blue-light)', bd: 'var(--blue-mid)',   icon: Info },
}

export default function IncidentCard({ incident, rank }) {
  const cfg  = SEV[incident.severity] || SEV.info
  const Icon = cfg.icon

  return (
    <div style={{
      background: '#fff',
      border: '1px solid var(--border)',
      borderLeft: `4px solid ${cfg.accent}`,
      borderRadius: 8, padding: '12px 16px', marginBottom: 8,
      boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
      transition: 'box-shadow 0.15s',
    }}
      onMouseEnter={e => e.currentTarget.style.boxShadow = '0 3px 12px rgba(45,74,58,0.08)'}
      onMouseLeave={e => e.currentTarget.style.boxShadow = '0 1px 4px rgba(0,0,0,0.04)'}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <span style={{
          background: 'var(--bg-alt)', color: 'var(--text-muted)',
          borderRadius: 5, padding: '1px 8px', fontSize: 11, fontWeight: 700,
        }}>#{rank}</span>
        <Icon size={13} color={cfg.accent} />
        <span style={{
          background: cfg.bg, border: `1px solid ${cfg.bd}`, color: cfg.accent,
          borderRadius: 4, padding: '1px 9px', fontSize: 10.5, fontWeight: 700,
          textTransform: 'uppercase', letterSpacing: '0.4px',
        }}>{incident.severity}</span>
        <span style={{ color: 'var(--text)', fontSize: 13, fontWeight: 600 }}>{incident.equipment_type}</span>
        {incident.hospital_unit && (
          <span style={{ color: 'var(--text-muted)', fontSize: 12, marginLeft: 'auto', flexShrink: 0 }}>
            {incident.hospital_unit}
          </span>
        )}
      </div>

      <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 5 }}>
        <strong style={{ color: 'var(--text)', fontWeight: 600 }}>Failure: </strong>
        {incident.failure_type || 'No Failure'}
      </div>

      <div style={{ fontSize: 12.5, color: 'var(--text-light)', lineHeight: 1.6 }}>
        {incident.text}
      </div>

      {incident.rerank_score != null && (
        <div style={{ fontSize: 11, color: 'var(--text-light)', marginTop: 8, display: 'flex', gap: 16 }}>
          <span>Relevance: <strong style={{ color: 'var(--text-muted)' }}>{(incident.rerank_score * 100).toFixed(0)}%</strong></span>
          <span>RRF: <strong style={{ color: 'var(--text-muted)' }}>{incident.score.toFixed(4)}</strong></span>
        </div>
      )}
    </div>
  )
}
