/* ─────────────────────────────────────────────────────────────
   DR. BLEEP  —  Medical Equipment Reliability Intelligence
   "Finding failures before they go *bleep*."
   ───────────────────────────────────────────────────────────── */

export function LogoMark({ size = 40 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="22" cy="22" r="22" fill="#2d4a3a" />
      <circle cx="22" cy="22" r="19" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="1" />
      <polyline
        points="2,22 8,22 10.5,11 13.5,33 16.5,11 19.5,33 22,22 42,22"
        fill="none"
        stroke="#4a9070"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="22" cy="22" r="2.2" fill="#fff" />
    </svg>
  )
}

export function LogoFull({ inverted = false }) {
  const nameColor = inverted ? '#fff'                   : '#2d4a3a'
  const tagColor  = inverted ? 'rgba(255,255,255,0.55)' : '#546e7a'
  const dotColor  = '#4a9070'

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <LogoMark size={42} />
      <div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 3 }}>
          <span style={{
            fontFamily: 'Catamaran, sans-serif',
            fontWeight: 800, fontSize: 20,
            color: nameColor,
            letterSpacing: '-0.02em', lineHeight: 1,
          }}>
            DR
          </span>
          <span style={{ color: dotColor, fontWeight: 900, fontSize: 22, lineHeight: 1 }}>.</span>
          <span style={{
            fontFamily: 'Catamaran, sans-serif',
            fontWeight: 800, fontSize: 20,
            color: nameColor,
            letterSpacing: '-0.02em', lineHeight: 1,
          }}>
            BLEEP
          </span>
        </div>
        <div style={{ fontSize: 11, color: tagColor, marginTop: 2, fontStyle: 'italic' }}>
          Finding failures before they go{' '}
          <span style={{ color: '#4a9070', fontWeight: 700, fontStyle: 'normal' }}>*bleep*</span>
        </div>
      </div>
    </div>
  )
}

/* Hero logo for the About Me page */
export function LogoHero() {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20,
      padding: '40px 32px 36px',
      background: 'linear-gradient(135deg, #2d4a3a 0%, #3a5e4a 55%, #4a9070 100%)',
      borderRadius: 16,
      marginBottom: 32,
    }}>
      {/* Big mark */}
      <svg width="90" height="90" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="22" cy="22" r="22" fill="rgba(255,255,255,0.1)" />
        <circle cx="22" cy="22" r="19" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
        <polyline
          points="2,22 8,22 10.5,11 13.5,33 16.5,11 19.5,33 22,22 42,22"
          fill="none" stroke="#fff" strokeWidth="2.4"
          strokeLinecap="round" strokeLinejoin="round"
        />
        <circle cx="22" cy="22" r="2.4" fill="#4a9070" />
      </svg>

      {/* Wordmark */}
      <div style={{ textAlign: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'center', gap: 3 }}>
          <span style={{
            fontFamily: 'Catamaran, sans-serif',
            fontWeight: 800, fontSize: 42, color: '#fff',
            letterSpacing: '-0.03em', lineHeight: 1,
          }}>DR</span>
          <span style={{ color: '#4a9070', fontWeight: 900, fontSize: 48, lineHeight: 1 }}>.</span>
          <span style={{
            fontFamily: 'Catamaran, sans-serif',
            fontWeight: 800, fontSize: 42, color: '#fff',
            letterSpacing: '-0.03em', lineHeight: 1,
          }}>BLEEP</span>
        </div>

        {/* Tagline */}
        <div style={{
          color: 'rgba(255,255,255,0.7)',
          fontSize: 14, marginTop: 8, fontStyle: 'italic', letterSpacing: '0.01em',
        }}>
          "Finding failures before they go&nbsp;
          <span style={{ color: '#fff', fontWeight: 700, fontStyle: 'normal' }}>*bleep*</span>"
        </div>
      </div>

      {/* Pill tags */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'center' }}>
        {['AI-Powered','Multi-Agent','Hybrid Retrieval','Human-in-the-Loop','Biomedical Engineering'].map(t => (
          <span key={t} style={{
            background: 'rgba(255,255,255,0.12)',
            border: '1px solid rgba(255,255,255,0.2)',
            color: 'rgba(255,255,255,0.85)',
            fontSize: 11.5, fontWeight: 600,
            padding: '4px 13px', borderRadius: 20,
          }}>{t}</span>
        ))}
      </div>
    </div>
  )
}
