import { useState } from 'react'
import { X, Eye, EyeOff, LogIn, Lock, Mail, ShieldCheck } from 'lucide-react'
import { LogoMark } from './Logo.jsx'

export default function LoginModal({ onClose }) {
  const [mode, setMode]         = useState('login') // 'login' | 'forgot'
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading]   = useState(false)
  const [done, setDone]         = useState(false)
  const [form, setForm]         = useState({ email: '', password: '' })

  const set = (k) => (e) => setForm(prev => ({ ...prev, [k]: e.target.value }))

  const handleLogin = (e) => {
    e.preventDefault()
    setLoading(true)
    setTimeout(() => { setLoading(false); onClose() }, 1200)
  }

  const handleForgot = (e) => {
    e.preventDefault()
    setLoading(true)
    setTimeout(() => { setLoading(false); setDone(true) }, 1000)
  }

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0, zIndex: 200,
          background: 'rgba(30,45,38,0.45)',
          backdropFilter: 'blur(4px)',
          animation: 'fade-in 0.15s ease',
        }}
      />

      {/* Modal */}
      <div style={{
        position: 'fixed', top: '50%', left: '50%',
        transform: 'translate(-50%, -50%)',
        zIndex: 201, width: '100%', maxWidth: 420,
        background: '#fff', borderRadius: 16,
        boxShadow: '0 24px 64px rgba(0,0,0,0.18)',
        animation: 'fade-in 0.2s ease',
        overflow: 'hidden',
      }}>
        {/* Header stripe */}
        <div style={{
          background: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-hover) 100%)',
          padding: '28px 28px 24px',
          display: 'flex', alignItems: 'center', gap: 14,
        }}>
          <LogoMark size={40} />
          <div>
            <div style={{ fontFamily: 'Catamaran, sans-serif', fontWeight: 800, fontSize: 18, color: '#fff' }}>
              DR. BLEEP
            </div>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.6)', marginTop: 1 }}>
              {mode === 'login' ? 'Sign in to your account' : 'Reset your password'}
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              marginLeft: 'auto', background: 'rgba(255,255,255,0.12)',
              border: '1px solid rgba(255,255,255,0.2)', borderRadius: 8,
              width: 32, height: 32, display: 'flex', alignItems: 'center',
              justifyContent: 'center', cursor: 'pointer', color: '#fff',
              transition: 'background 0.15s',
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.22)'}
            onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.12)'}
          >
            <X size={15} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '28px 28px 24px' }}>

          {mode === 'login' && (
            <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <Field label="Email address" icon={<Mail size={14} color="var(--text-light)" />}>
                <input
                  type="email" required placeholder="engineer@hospital.org"
                  value={form.email} onChange={set('email')}
                  style={inputStyle}
                  onFocus={e => { e.target.style.borderColor = 'var(--blue)'; e.target.style.boxShadow = '0 0 0 3px rgba(74,144,112,0.12)' }}
                  onBlur={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.boxShadow = 'none' }}
                />
              </Field>

              <Field label="Password" icon={<Lock size={14} color="var(--text-light)" />}>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showPass ? 'text' : 'password'} required placeholder="••••••••"
                    value={form.password} onChange={set('password')}
                    style={{ ...inputStyle, paddingRight: 42 }}
                    onFocus={e => { e.target.style.borderColor = 'var(--blue)'; e.target.style.boxShadow = '0 0 0 3px rgba(74,144,112,0.12)' }}
                    onBlur={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.boxShadow = 'none' }}
                  />
                  <button type="button" onClick={() => setShowPass(v => !v)} style={{
                    position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                    background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-light)',
                    display: 'flex', alignItems: 'center',
                  }}>
                    {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
              </Field>

              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button type="button" onClick={() => setMode('forgot')} style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: 'var(--blue)', fontSize: 12.5, fontWeight: 600, fontFamily: 'inherit',
                }}>
                  Forgot password?
                </button>
              </div>

              <button type="submit" disabled={loading} style={{
                background: loading ? 'var(--bg-alt)' : 'var(--navy)',
                border: 'none', borderRadius: 8, padding: '12px 0',
                color: loading ? 'var(--text-muted)' : '#fff',
                fontSize: 14, fontWeight: 700, fontFamily: 'Catamaran, sans-serif',
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                transition: 'all 0.15s',
              }}>
                {loading
                  ? <><span style={{ width: 14, height: 14, border: '2px solid var(--border)', borderTopColor: 'var(--blue)', borderRadius: '50%', animation: 'spin 0.8s linear infinite', display: 'inline-block' }} /> Signing in…</>
                  : <><LogIn size={15} /> Sign In</>
                }
              </button>

              <div style={{ textAlign: 'center', fontSize: 12, color: 'var(--text-light)', marginTop: 4 }}>
                <ShieldCheck size={12} style={{ display: 'inline', marginRight: 5, verticalAlign: 'middle' }} />
                Protected by hospital-grade authentication
              </div>
            </form>
          )}

          {mode === 'forgot' && (
            <form onSubmit={handleForgot} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {done ? (
                <div style={{ textAlign: 'center', padding: '16px 0' }}>
                  <div style={{ fontSize: 40, marginBottom: 12 }}>📧</div>
                  <div style={{ fontFamily: 'Catamaran, sans-serif', fontWeight: 800, fontSize: 16, color: 'var(--navy)', marginBottom: 8 }}>
                    Check your inbox
                  </div>
                  <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                    If that email is registered, a password reset link has been sent.
                  </p>
                  <button type="button" onClick={() => { setMode('login'); setDone(false) }} style={{
                    marginTop: 18, background: 'var(--navy)', border: 'none', borderRadius: 8,
                    padding: '10px 24px', color: '#fff', fontSize: 13, fontWeight: 700,
                    fontFamily: 'inherit', cursor: 'pointer',
                  }}>Back to Sign In</button>
                </div>
              ) : (
                <>
                  <p style={{ fontSize: 13.5, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                    Enter your work email and we'll send a password reset link.
                  </p>
                  <Field label="Work email" icon={<Mail size={14} color="var(--text-light)" />}>
                    <input
                      type="email" required placeholder="engineer@hospital.org"
                      style={inputStyle}
                      onFocus={e => { e.target.style.borderColor = 'var(--blue)'; e.target.style.boxShadow = '0 0 0 3px rgba(74,144,112,0.12)' }}
                      onBlur={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.boxShadow = 'none' }}
                    />
                  </Field>
                  <div style={{ display: 'flex', gap: 10 }}>
                    <button type="button" onClick={() => setMode('login')} style={{
                      flex: 1, background: 'var(--bg-alt)', border: '1px solid var(--border)',
                      borderRadius: 8, padding: '11px 0', color: 'var(--text-muted)',
                      fontSize: 13, fontWeight: 600, fontFamily: 'inherit', cursor: 'pointer',
                    }}>Cancel</button>
                    <button type="submit" disabled={loading} style={{
                      flex: 2, background: loading ? 'var(--bg-alt)' : 'var(--navy)',
                      border: 'none', borderRadius: 8, padding: '11px 0',
                      color: loading ? 'var(--text-muted)' : '#fff',
                      fontSize: 13, fontWeight: 700, fontFamily: 'inherit', cursor: loading ? 'not-allowed' : 'pointer',
                    }}>
                      {loading ? 'Sending…' : 'Send Reset Link'}
                    </button>
                  </div>
                </>
              )}
            </form>
          )}
        </div>
      </div>
    </>
  )
}

function Field({ label, icon, children }) {
  return (
    <div>
      <label style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
        {icon}{label}
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
