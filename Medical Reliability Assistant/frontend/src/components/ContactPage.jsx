import { useState } from 'react'
import { Mail, Phone, MapPin, Send, CheckCircle } from 'lucide-react'

const CONTACT_INFO = [
  {
    icon: Mail, label: 'Email Support',
    value: 'support@drbleep.health',
    sub: 'Response within 24 hours',
    color: 'var(--blue)',
  },
  {
    icon: Phone, label: 'Helpline',
    value: '+1 (800) 274-5337',
    sub: 'Mon–Fri  8 AM – 6 PM EST',
    color: 'var(--success)',
  },
  {
    icon: MapPin, label: 'Headquarters',
    value: 'Boston Medical District',
    sub: '100 Reliability Ave, MA 02115',
    color: '#7c3aed',
  },
]

export default function ContactPage() {
  const [form, setForm]     = useState({ name: '', email: '', subject: '', message: '' })
  const [loading, setLoading] = useState(false)
  const [sent, setSent]       = useState(false)

  const set = k => e => setForm(prev => ({ ...prev, [k]: e.target.value }))

  const handleSubmit = (e) => {
    e.preventDefault()
    setLoading(true)
    setTimeout(() => { setLoading(false); setSent(true) }, 1200)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>

      {/* Contact info cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        {CONTACT_INFO.map(({ icon: Icon, label, value, sub, color }) => (
          <div key={label} style={{
            background: '#fff', border: '1px solid var(--border)',
            borderTop: `3px solid ${color}`,
            borderRadius: 12, padding: '20px 22px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
            transition: 'box-shadow 0.15s',
          }}
            onMouseEnter={e => e.currentTarget.style.boxShadow = '0 6px 20px rgba(0,0,0,0.08)'}
            onMouseLeave={e => e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)'}
          >
            <div style={{
              width: 40, height: 40, borderRadius: 10,
              background: `${color}12`, border: `1px solid ${color}22`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              marginBottom: 14,
            }}>
              <Icon size={18} color={color} />
            </div>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-light)', textTransform: 'uppercase', letterSpacing: '0.6px', marginBottom: 5 }}>
              {label}
            </div>
            <div style={{ fontFamily: 'Catamaran, sans-serif', fontWeight: 700, fontSize: 15, color: 'var(--navy)', marginBottom: 3 }}>
              {value}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-light)' }}>{sub}</div>
          </div>
        ))}
      </div>

      {/* Contact form */}
      <div style={{
        background: '#fff', border: '1px solid var(--border)',
        borderRadius: 14, overflow: 'hidden',
        boxShadow: '0 2px 12px rgba(0,0,0,0.04)',
      }}>
        {/* Form header */}
        <div style={{
          background: 'var(--bg-alt)', padding: '18px 28px',
          borderBottom: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', gap: 10,
        }}>
          <Send size={16} color="var(--blue)" />
          <div>
            <div style={{ fontFamily: 'Catamaran, sans-serif', fontWeight: 800, fontSize: 16, color: 'var(--navy)' }}>
              Send Us a Message
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-light)', marginTop: 1 }}>
              We typically respond within one business day
            </div>
          </div>
        </div>

        <div style={{ padding: '28px' }}>
          {sent ? (
            <div style={{ textAlign: 'center', padding: '24px 0' }}>
              <CheckCircle size={48} color="var(--success)" style={{ marginBottom: 16 }} />
              <div style={{ fontFamily: 'Catamaran, sans-serif', fontWeight: 800, fontSize: 20, color: 'var(--navy)', marginBottom: 8 }}>
                Message Sent!
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: 14, lineHeight: 1.6, maxWidth: 400, margin: '0 auto 20px' }}>
                Thank you for reaching out. Our biomedical engineering support team will get back to you within 24 hours.
              </p>
              <button onClick={() => { setSent(false); setForm({ name:'', email:'', subject:'', message:'' }) }} style={{
                background: 'var(--navy)', border: 'none', borderRadius: 8,
                padding: '10px 24px', color: '#fff', fontSize: 13, fontWeight: 700,
                fontFamily: 'inherit', cursor: 'pointer',
              }}>Send Another</button>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                <FormField label="Full Name" required>
                  <input
                    type="text" required placeholder="Dr. Jane Smith"
                    value={form.name} onChange={set('name')}
                    style={inputStyle}
                    onFocus={focusStyle} onBlur={blurStyle}
                  />
                </FormField>
                <FormField label="Work Email" required>
                  <input
                    type="email" required placeholder="jane@hospital.org"
                    value={form.email} onChange={set('email')}
                    style={inputStyle}
                    onFocus={focusStyle} onBlur={blurStyle}
                  />
                </FormField>
              </div>

              <FormField label="Subject" required style={{ marginBottom: 16 }}>
                <select
                  required value={form.subject} onChange={set('subject')}
                  style={{ ...inputStyle, cursor: 'pointer' }}
                  onFocus={focusStyle} onBlur={blurStyle}
                >
                  <option value="">Select a subject…</option>
                  <option>General Enquiry</option>
                  <option>Technical Support</option>
                  <option>Data Ingestion Issue</option>
                  <option>Agent Pipeline Error</option>
                  <option>Feature Request</option>
                  <option>Other</option>
                </select>
              </FormField>

              <FormField label="Message" required style={{ marginBottom: 24 }}>
                <textarea
                  required rows={5} placeholder="Describe your issue or question in detail…"
                  value={form.message} onChange={set('message')}
                  style={{ ...inputStyle, resize: 'vertical', lineHeight: 1.6 }}
                  onFocus={focusStyle} onBlur={blurStyle}
                />
              </FormField>

              <button type="submit" disabled={loading} style={{
                background: loading ? 'var(--bg-alt)' : 'var(--navy)',
                border: 'none', borderRadius: 8, padding: '12px 28px',
                color: loading ? 'var(--text-muted)' : '#fff',
                fontSize: 14, fontWeight: 700, fontFamily: 'Catamaran, sans-serif',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex', alignItems: 'center', gap: 8,
                transition: 'all 0.15s',
              }}>
                {loading
                  ? <><span style={{ width: 14, height: 14, border: '2px solid var(--border)', borderTopColor: 'var(--blue)', borderRadius: '50%', animation: 'spin 0.8s linear infinite', display:'inline-block' }} /> Sending…</>
                  : <><Send size={14} /> Send Message</>
                }
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

function FormField({ label, required, children, style }) {
  return (
    <div style={style}>
      <label style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>
        {label}{required && <span style={{ color: 'var(--danger)', marginLeft: 3 }}>*</span>}
      </label>
      {children}
    </div>
  )
}

const inputStyle = {
  width: '100%', padding: '10px 14px',
  background: '#fff', border: '1px solid var(--border)',
  borderRadius: 8, color: 'var(--text)', fontSize: 13.5,
  fontFamily: 'inherit', outline: 'none',
  transition: 'border-color 0.15s, box-shadow 0.15s',
  boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
}
const focusStyle = e => { e.target.style.borderColor = 'var(--blue)'; e.target.style.boxShadow = '0 0 0 3px rgba(74,144,112,0.12)' }
const blurStyle  = e => { e.target.style.borderColor = 'var(--border)'; e.target.style.boxShadow = '0 1px 3px rgba(0,0,0,0.04)' }
