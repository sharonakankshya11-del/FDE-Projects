/**
 * Parses and renders structured markdown recommendation output.
 * Handles: ## headings, **bold**, numbered lists, bullet lists, paragraphs.
 */

const SECTION_COLORS = {
  // Recommendation sections
  'ROOT CAUSE':   { accent: '#9a3232', bg: '#faeaea', icon: '🔎' },
  'IMMEDIATE':    { accent: '#8a6214', bg: '#fef8ea', icon: '⚡' },
  'PREVENTIVE':   { accent: '#2d4a3a', bg: '#edf5f0', icon: '🛡️' },
  'CONFIDENCE':   { accent: '#4a6257', bg: '#f0f5f2', icon: '📊' },
  'CITATION':     { accent: '#6b7a72', bg: '#f5f7f5', icon: '📎' },
  // Maintenance pattern sections
  'KEY MAINTENAN':{ accent: '#4a6a9f', bg: '#eef3f9', icon: '🔑' },
  'RECURRING':    { accent: '#9a3232', bg: '#faeaea', icon: '🔄' },
  'RECOMMENDED':  { accent: '#2d4a3a', bg: '#edf5f0', icon: '📅' },
  'EQUIPMENT UTI':{ accent: '#8a6214', bg: '#fef8ea', icon: '⚠️' },
  'UTILISATION':  { accent: '#8a6214', bg: '#fef8ea', icon: '⚠️' },
  'UTILIZATION':  { accent: '#8a6214', bg: '#fef8ea', icon: '⚠️' },
  'SCHEDULE':     { accent: '#2d4a3a', bg: '#edf5f0', icon: '📅' },
  'FAILURE MODE': { accent: '#9a3232', bg: '#faeaea', icon: '🔄' },
  'DEFAULT':      { accent: '#2d4a3a', bg: '#edf5f0', icon: '📋' },
}

function getSectionStyle(heading) {
  const upper = heading.toUpperCase()
  for (const key of Object.keys(SECTION_COLORS)) {
    if (upper.includes(key)) return SECTION_COLORS[key]
  }
  return SECTION_COLORS.DEFAULT
}

/* Render inline markdown: **bold** and plain text */
function InlineText({ text }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={i} style={{ color: 'var(--text)', fontWeight: 700 }}>{part.slice(2, -2)}</strong>
        }
        return <span key={i}>{part}</span>
      })}
    </>
  )
}

/* One numbered or bullet list item */
function ListItem({ text, number }) {
  // Split "**Title**: rest" into title + body
  const titleMatch = text.match(/^\*\*([^*]+)\*\*[:：]?\s*(.*)/)

  return (
    <div style={{ display: 'flex', gap: 12, marginBottom: 10, alignItems: 'flex-start' }}>
      <div style={{
        width: 24, height: 24, borderRadius: '50%',
        background: 'var(--navy)', color: '#fff',
        fontSize: 11, fontWeight: 800, flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        marginTop: 1,
      }}>
        {number || '•'}
      </div>
      <div style={{ flex: 1, fontSize: 13.5, color: 'var(--text-muted)', lineHeight: 1.7 }}>
        {titleMatch ? (
          <>
            <span style={{ fontWeight: 700, color: 'var(--text)' }}>{titleMatch[1]}</span>
            {titleMatch[2] && <span>: {titleMatch[2]}</span>}
          </>
        ) : (
          <InlineText text={text} />
        )}
      </div>
    </div>
  )
}

/* One ## section block */
function Section({ heading, lines }) {
  const style = getSectionStyle(heading)

  // Separate list items from paragraphs
  const numbered = []
  const paragraphs = []
  let listCounter = 0

  lines.forEach(line => {
    const numberedMatch = line.match(/^(\d+)\.\s+(.+)/)
    const bulletMatch   = line.match(/^[-•]\s+(.+)/)
    if (numberedMatch) {
      listCounter++
      numbered.push({ number: listCounter, text: numberedMatch[2] })
    } else if (bulletMatch) {
      listCounter++
      numbered.push({ number: listCounter, text: bulletMatch[1] })
    } else if (line.trim()) {
      paragraphs.push(line.trim())
    }
  })

  return (
    <div style={{
      background: '#fff',
      border: `1px solid ${style.accent}22`,
      borderLeft: `4px solid ${style.accent}`,
      borderRadius: 10,
      overflow: 'hidden',
      marginBottom: 14,
      boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
    }}>
      {/* Section header */}
      <div style={{
        background: style.bg,
        padding: '10px 18px',
        display: 'flex', alignItems: 'center', gap: 10,
        borderBottom: `1px solid ${style.accent}18`,
      }}>
        <span style={{ fontSize: 16 }}>{style.icon}</span>
        <span style={{
          fontFamily: 'Catamaran, sans-serif',
          fontWeight: 800, fontSize: 14,
          color: style.accent, letterSpacing: '0.02em',
          textTransform: 'uppercase',
        }}>
          {heading.replace(/^#+\s*/, '')}
        </span>
      </div>

      {/* Content */}
      <div style={{ padding: '16px 18px' }}>
        {paragraphs.map((p, i) => (
          <p key={i} style={{
            fontSize: 13.5, color: 'var(--text-muted)',
            lineHeight: 1.75, marginBottom: numbered.length ? 12 : (i < paragraphs.length - 1 ? 10 : 0),
          }}>
            <InlineText text={p} />
          </p>
        ))}
        {numbered.length > 0 && (
          <div style={{ marginTop: paragraphs.length ? 4 : 0 }}>
            {numbered.map((item, i) => (
              <ListItem key={i} text={item.text} number={item.number} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function RecommendationRenderer({ text, confidence }) {
  if (!text) return null

  // Split into sections by ## headings
  const lines = text.split('\n')
  const sections = []
  let currentHeading = null
  let currentLines   = []

  lines.forEach(line => {
    if (/^#{1,4}\s/.test(line)) {
      if (currentHeading !== null) {
        sections.push({ heading: currentHeading, lines: currentLines })
      }
      currentHeading = line.replace(/^#+\s*/, '').trim()
      currentLines   = []
    } else {
      currentLines.push(line)
    }
  })
  if (currentHeading !== null) {
    sections.push({ heading: currentHeading, lines: currentLines })
  }

  // If no sections found, render as plain formatted paragraphs
  if (sections.length === 0) {
    return (
      <div style={{ fontSize: 13.5, color: 'var(--text-muted)', lineHeight: 1.75 }}>
        <InlineText text={text} />
      </div>
    )
  }

  return (
    <div>
      {/* Confidence bar (shown above sections if available) */}
      {confidence !== undefined && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: 14,
          background: 'var(--bg-alt)', border: '1px solid var(--border)',
          borderRadius: 8, padding: '10px 16px', marginBottom: 16,
        }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
            Confidence
          </span>
          <div style={{ flex: 1, height: 6, background: 'var(--border)', borderRadius: 3, overflow: 'hidden' }}>
            <div style={{
              height: '100%',
              width: `${Math.round(confidence * 100)}%`,
              background: confidence > 0.75 ? 'var(--success)' : confidence > 0.5 ? 'var(--warning)' : 'var(--danger)',
              borderRadius: 3, transition: 'width 0.6s ease',
            }} />
          </div>
          <span style={{
            fontSize: 14, fontWeight: 800, fontFamily: 'Catamaran, sans-serif',
            color: confidence > 0.75 ? 'var(--success)' : confidence > 0.5 ? 'var(--warning)' : 'var(--danger)',
            minWidth: 38, textAlign: 'right',
          }}>
            {Math.round(confidence * 100)}%
          </span>
        </div>
      )}

      {sections.map((sec, i) => (
        <Section key={i} heading={sec.heading} lines={sec.lines} />
      ))}
    </div>
  )
}
