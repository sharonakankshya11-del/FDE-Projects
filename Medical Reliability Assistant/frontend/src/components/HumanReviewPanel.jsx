import { useState } from 'react'
import { CheckCircle, XCircle, Edit3, Send } from 'lucide-react'
import { submitReview } from '../utils/api'

export default function HumanReviewPanel({ sessionId, recommendation, onReviewComplete }) {
  const [mode, setMode]           = useState(null)
  const [editedText, setEditedText] = useState(recommendation)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError]         = useState(null)

  const handleAction = async (action, edited = null) => {
    setSubmitting(true); setError(null)
    try {
      const result = await submitReview({ session_id: sessionId, action, edited_response: edited || null })
      onReviewComplete(result)
    } catch (e) { setError(e.message) }
    finally { setSubmitting(false) }
  }

  return (
    <div style={{
      background: 'var(--blue-light)',
      border: '1px solid var(--blue-mid)',
      borderLeft: '4px solid var(--blue)',
      borderRadius: 10, padding: 22,
      boxShadow: '0 2px 12px rgba(74,144,112,0.08)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        <div style={{
          width: 10, height: 10, borderRadius: '50%', background: 'var(--blue)',
          animation: 'pulse-dot 2s ease-in-out infinite',
        }} />
        <span style={{
          fontFamily: 'Catamaran, sans-serif',
          color: 'var(--navy)', fontWeight: 800, fontSize: 16,
        }}>
          Human Review Required
        </span>
      </div>

      <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 18, lineHeight: 1.6 }}>
        Review the AI recommendation before delivery. You may Approve, Edit, or Reject.
      </p>

      {mode === 'edit' ? (
        <div>
          <textarea
            value={editedText}
            onChange={e => setEditedText(e.target.value)}
            style={{
              width: '100%', minHeight: 160, padding: 14,
              background: '#fff', border: '1px solid var(--border)',
              borderRadius: 8, color: 'var(--text)', fontSize: 13,
              lineHeight: 1.65, resize: 'vertical', fontFamily: 'inherit',
            }}
            onFocus={e => { e.target.style.borderColor = 'var(--blue)'; e.target.style.boxShadow = '0 0 0 3px rgba(74,144,112,0.15)' }}
            onBlur={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.boxShadow = 'none' }}
          />
          <div style={{ display: 'flex', gap: 10, marginTop: 12 }}>
            <Btn onClick={() => handleAction('edit', editedText)} disabled={submitting} variant="primary" icon={<Send size={13} />} label="Submit Edit" />
            <Btn onClick={() => setMode(null)} disabled={submitting} variant="ghost" label="Cancel" />
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <Btn onClick={() => handleAction('approve')} disabled={submitting} variant="success" icon={<CheckCircle size={14} />} label="Approve" />
          <Btn onClick={() => setMode('edit')} disabled={submitting} variant="primary" icon={<Edit3 size={14} />} label="Edit" />
          <Btn onClick={() => handleAction('reject')} disabled={submitting} variant="danger" icon={<XCircle size={14} />} label="Reject" />
        </div>
      )}

      {error     && <p style={{ color: 'var(--danger)',   fontSize: 13, marginTop: 12 }}>{error}</p>}
      {submitting && <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 12 }}>Submitting review…</p>}
    </div>
  )
}

const VARIANT = {
  primary: { bg: 'var(--navy)',       border: 'var(--navy)',       color: '#fff' },
  success: { bg: 'var(--success-bg)', border: 'var(--success-bd)', color: 'var(--success)' },
  danger:  { bg: 'var(--danger-bg)',  border: 'var(--danger-bd)',  color: 'var(--danger)' },
  ghost:   { bg: '#fff',              border: 'var(--border)',      color: 'var(--text-muted)' },
}

function Btn({ onClick, disabled, variant = 'ghost', icon, label }) {
  const v = VARIANT[variant]
  return (
    <button onClick={onClick} disabled={disabled} style={{
      display: 'flex', alignItems: 'center', gap: 7,
      padding: '9px 18px',
      background: disabled ? 'var(--bg-alt)' : v.bg,
      border: `1px solid ${disabled ? 'var(--border)' : v.border}`,
      borderRadius: 7, color: disabled ? 'var(--text-light)' : v.color,
      cursor: disabled ? 'not-allowed' : 'pointer',
      fontSize: 13, fontWeight: 700, fontFamily: 'inherit',
      transition: 'all 0.15s ease',
    }}>
      {icon}{label}
    </button>
  )
}
