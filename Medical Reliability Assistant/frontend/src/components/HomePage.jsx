import { LogoMark } from './Logo.jsx'

const FEATURES = [
  {
    icon: '🔍',
    title: 'Hybrid Retrieval',
    desc: 'Combines ChromaDB vector search with BM25 keyword search, fused via Reciprocal Rank Fusion for maximum recall precision.',
    color: '#4a9070',
  },
  {
    icon: '🤖',
    title: 'Multi-Agent Pipeline',
    desc: 'Four specialist agents — Retrieval, Analysis, Maintenance, and Recommendation — orchestrated by LangGraph with full traceability.',
    color: '#7c3aed',
  },
  {
    icon: '🛡️',
    title: 'Dual Guardrails',
    desc: 'Input and output safety filters powered by Claude Sonnet detect PII, off-topic queries, and hallucinated medical advice.',
    color: '#1a7a4a',
  },
  {
    icon: '👩‍⚕️',
    title: 'Human-in-the-Loop',
    desc: 'Every recommendation can be reviewed, edited, or rejected by a biomedical engineer before delivery — zero blind automation.',
    color: '#b45309',
  },
  {
    icon: '📊',
    title: 'Anomaly Detection',
    desc: 'Z-score analysis flags statistically abnormal sensor readings — temperature, torque, rotational speed, and tool wear.',
    color: '#0891b2',
  },
  {
    icon: '📋',
    title: 'DeepEval Scoring',
    desc: 'Every response is scored on faithfulness, context precision, recall, and relevancy using Claude as an LLM judge.',
    color: '#dc2626',
  },
]

const PIPELINE_STEPS = [
  { label: 'Your Query',         icon: '💬', color: '#2d4a3a' },
  { label: 'Safety Check',       icon: '🔒', color: '#4a9070' },
  { label: 'Retrieve Incidents', icon: '🔍', color: '#7c3aed' },
  { label: 'Detect Anomalies',   icon: '📈', color: '#0891b2' },
  { label: 'Match Patterns',     icon: '🔧', color: '#1a7a4a' },
  { label: 'Recommendation',     icon: '✅', color: '#b45309' },
]

const STATS = [
  { value: '20,000+', label: 'Incident Records',     sub: 'AI4I + Predictive Maintenance' },
  { value: '4',       label: 'Specialist Agents',    sub: 'Retrieval · Analysis · Maintenance · Recommendation' },
  { value: '1536',    label: 'Embedding Dimensions', sub: 'text-embedding-3-small' },
  { value: '< 30s',   label: 'Pipeline Latency',     sub: 'Per query end-to-end' },
]

export default function HomePage({ onNavigate }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>

      {/* ── Hero ──────────────────────────────────────────────── */}
      <section style={{
        background: 'linear-gradient(135deg, #2d4a3a 0%, #3a5e4a 55%, #4a9070 100%)',
        padding: '80px 40px 72px',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Subtle grid texture */}
        <div style={{
          position: 'absolute', inset: 0, opacity: 0.04,
          backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }} />

        {/* Glow orbs */}
        <div style={{ position:'absolute', width:400, height:400, borderRadius:'50%', background:'rgba(74,144,112,0.15)', top:-100, right:-80, filter:'blur(60px)', pointerEvents:'none' }} />
        <div style={{ position:'absolute', width:300, height:300, borderRadius:'50%', background:'rgba(255,255,255,0.06)', bottom:-60, left:-60, filter:'blur(50px)', pointerEvents:'none' }} />

        <div style={{ position:'relative', maxWidth:700, margin:'0 auto' }}>
          {/* Logo mark */}
          <div style={{ display:'flex', justifyContent:'center', marginBottom:28 }}>
            <div style={{
              width:100, height:100, borderRadius:24,
              background:'rgba(255,255,255,0.1)',
              border:'1px solid rgba(255,255,255,0.2)',
              display:'flex', alignItems:'center', justifyContent:'center',
              boxShadow:'0 8px 32px rgba(0,0,0,0.2)',
            }}>
              <LogoMark size={64} />
            </div>
          </div>

          {/* Wordmark */}
          <div style={{ display:'flex', alignItems:'baseline', justifyContent:'center', gap:4, marginBottom:10 }}>
            <span style={{ fontFamily:'Catamaran, sans-serif', fontWeight:800, fontSize:56, color:'#fff', letterSpacing:'-0.03em', lineHeight:1 }}>DR</span>
            <span style={{ color:'#7abda0', fontWeight:900, fontSize:64, lineHeight:1 }}>.</span>
            <span style={{ fontFamily:'Catamaran, sans-serif', fontWeight:800, fontSize:56, color:'#fff', letterSpacing:'-0.03em', lineHeight:1 }}>BLEEP</span>
          </div>

          {/* Tagline */}
          <p style={{ color:'rgba(255,255,255,0.75)', fontSize:18, fontStyle:'italic', marginBottom:8 }}>
            "Finding failures before they go{' '}
            <span style={{ color:'#fff', fontWeight:800, fontStyle:'normal', fontFamily:'Catamaran, sans-serif' }}>*bleep*</span>"
          </p>

          <p style={{ color:'rgba(255,255,255,0.55)', fontSize:14, marginBottom:36, lineHeight:1.6 }}>
            AI-Powered Medical Equipment Reliability Intelligence<br/>
            for Biomedical Engineers
          </p>

          {/* CTAs */}
          <div style={{ display:'flex', gap:12, justifyContent:'center', flexWrap:'wrap' }}>
            <button
              onClick={() => onNavigate('query')}
              style={{
                background:'#fff', color:'#2d4a3a',
                border:'none', borderRadius:8,
                padding:'13px 32px', fontSize:14, fontWeight:800,
                fontFamily:'Catamaran, sans-serif',
                cursor:'pointer', letterSpacing:'-0.01em',
                boxShadow:'0 4px 16px rgba(0,0,0,0.2)',
                transition:'transform 0.15s, box-shadow 0.15s',
              }}
              onMouseEnter={e => { e.currentTarget.style.transform='translateY(-2px)'; e.currentTarget.style.boxShadow='0 8px 24px rgba(0,0,0,0.25)' }}
              onMouseLeave={e => { e.currentTarget.style.transform='translateY(0)'; e.currentTarget.style.boxShadow='0 4px 16px rgba(0,0,0,0.2)' }}
            >
              🔍 Start a Query
            </button>
            <button
              onClick={() => onNavigate('dashboard')}
              style={{
                background:'rgba(255,255,255,0.12)',
                color:'#fff',
                border:'1px solid rgba(255,255,255,0.3)',
                borderRadius:8, padding:'13px 32px',
                fontSize:14, fontWeight:700,
                fontFamily:'inherit', cursor:'pointer',
                transition:'background 0.15s',
              }}
              onMouseEnter={e => e.currentTarget.style.background='rgba(255,255,255,0.2)'}
              onMouseLeave={e => e.currentTarget.style.background='rgba(255,255,255,0.12)'}
            >
              📊 View Device Health
            </button>
          </div>
        </div>
      </section>

      {/* ── Stats bar ─────────────────────────────────────────── */}
      <section style={{
        background:'var(--navy)',
        padding:'0 40px',
        display:'flex', justifyContent:'center',
      }}>
        <div style={{
          maxWidth:960, width:'100%',
          display:'grid', gridTemplateColumns:'repeat(4, 1fr)',
        }}>
          {STATS.map((s, i) => (
            <div key={s.label} style={{
              padding:'22px 24px',
              borderRight: i < STATS.length - 1 ? '1px solid rgba(255,255,255,0.08)' : 'none',
              textAlign:'center',
            }}>
              <div style={{ fontFamily:'Catamaran, sans-serif', fontWeight:800, fontSize:28, color:'#fff', lineHeight:1 }}>{s.value}</div>
              <div style={{ fontSize:12, fontWeight:700, color:'rgba(255,255,255,0.7)', marginTop:5 }}>{s.label}</div>
              <div style={{ fontSize:10.5, color:'rgba(255,255,255,0.35)', marginTop:3 }}>{s.sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────────── */}
      <section style={{ background:'var(--bg-alt)', padding:'64px 40px' }}>
        <div style={{ maxWidth:960, margin:'0 auto' }}>
          <SectionHeader
            badge="Pipeline"
            title="How DR. BLEEP Works"
            desc="Six steps from natural-language query to actionable engineering recommendation."
          />

          <div style={{ display:'flex', alignItems:'center', flexWrap:'wrap', gap:0, marginTop:40 }}>
            {PIPELINE_STEPS.map((step, i) => (
              <div key={step.label} style={{ display:'flex', alignItems:'center', flex:1, minWidth:120 }}>
                <div style={{ display:'flex', flexDirection:'column', alignItems:'center', flex:1, gap:10 }}>
                  <div style={{
                    width:56, height:56, borderRadius:16,
                    background:'#fff',
                    border:`2px solid ${step.color}22`,
                    display:'flex', alignItems:'center', justifyContent:'center',
                    fontSize:24,
                    boxShadow:`0 4px 16px ${step.color}18`,
                    transition:'transform 0.2s',
                  }}
                    onMouseEnter={e => e.currentTarget.style.transform='translateY(-3px)'}
                    onMouseLeave={e => e.currentTarget.style.transform='translateY(0)'}
                  >
                    {step.icon}
                  </div>
                  <div style={{
                    width:24, height:24, borderRadius:'50%',
                    background:step.color, color:'#fff',
                    fontSize:11, fontWeight:800,
                    display:'flex', alignItems:'center', justifyContent:'center',
                    marginTop:-4,
                  }}>{i+1}</div>
                  <div style={{ fontSize:12, fontWeight:700, color:'var(--text)', textAlign:'center', lineHeight:1.3 }}>{step.label}</div>
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <div style={{ color:'var(--border)', fontSize:20, padding:'0 4px', marginBottom:40 }}>›</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features grid ─────────────────────────────────────── */}
      <section style={{ background:'var(--bg)', padding:'64px 40px' }}>
        <div style={{ maxWidth:960, margin:'0 auto' }}>
          <SectionHeader
            badge="Capabilities"
            title="What Makes DR. BLEEP Different"
            desc="Not just another chatbot — a purpose-built multi-agent system for biomedical engineers."
          />

          <div style={{
            display:'grid',
            gridTemplateColumns:'repeat(3, 1fr)',
            gap:16, marginTop:40,
          }}>
            {FEATURES.map(f => (
              <div key={f.title} style={{
                background:'#fff',
                border:'1px solid var(--border)',
                borderTop:`3px solid ${f.color}`,
                borderRadius:12, padding:'22px 20px',
                boxShadow:'0 2px 8px rgba(0,0,0,0.04)',
                transition:'box-shadow 0.15s, transform 0.15s',
              }}
                onMouseEnter={e => { e.currentTarget.style.boxShadow=`0 8px 24px ${f.color}18`; e.currentTarget.style.transform='translateY(-2px)' }}
                onMouseLeave={e => { e.currentTarget.style.boxShadow='0 2px 8px rgba(0,0,0,0.04)'; e.currentTarget.style.transform='translateY(0)' }}
              >
                <div style={{ fontSize:28, marginBottom:12 }}>{f.icon}</div>
                <div style={{ fontFamily:'Catamaran, sans-serif', fontWeight:800, fontSize:16, color:'var(--navy)', marginBottom:8 }}>{f.title}</div>
                <div style={{ fontSize:13, color:'var(--text-muted)', lineHeight:1.65 }}>{f.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Dataset banner ────────────────────────────────────── */}
      <section style={{
        background:'var(--bg-alt)',
        borderTop:'1px solid var(--border)',
        borderBottom:'1px solid var(--border)',
        padding:'48px 40px',
      }}>
        <div style={{ maxWidth:960, margin:'0 auto', display:'flex', alignItems:'center', gap:48, flexWrap:'wrap' }}>
          <div style={{ flex:1, minWidth:260 }}>
            <div style={{ fontSize:11, fontWeight:700, color:'var(--blue)', letterSpacing:'0.7px', textTransform:'uppercase', marginBottom:8 }}>Dataset</div>
            <h3 style={{ fontFamily:'Catamaran, sans-serif', fontWeight:800, fontSize:22, color:'var(--navy)', marginBottom:10 }}>
              Built on Real Industrial Data
            </h3>
            <p style={{ color:'var(--text-muted)', fontSize:13.5, lineHeight:1.7 }}>
              Trained on the <strong>AI4I 2020</strong> predictive maintenance dataset — 10,000 sensor readings
              transformed into hospital medical-equipment incident narratives mapped to real device types,
              hospital units, and failure classifications.
            </p>
          </div>
          <div style={{ display:'flex', gap:12, flexWrap:'wrap' }}>
            {[
              ['AI4I 2020',              '10k rows', '#4a9070'],
              ['Predictive Maintenance', '10k rows', '#7c3aed'],
              ['Failure Types',          'TWF · HDF · PWF · OSF · RNF', '#1a7a4a'],
              ['Device Types',           '12 categories', '#b45309'],
            ].map(([name, detail, color]) => (
              <div key={name} style={{
                background:'#fff', border:`1px solid ${color}28`,
                borderLeft:`3px solid ${color}`,
                borderRadius:8, padding:'12px 16px', minWidth:160,
              }}>
                <div style={{ fontSize:12.5, fontWeight:700, color:'var(--text)' }}>{name}</div>
                <div style={{ fontSize:11.5, color:'var(--text-muted)', marginTop:3 }}>{detail}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA footer ────────────────────────────────────────── */}
      <section style={{
        background:'var(--navy)',
        padding:'60px 40px',
        textAlign:'center',
      }}>
        <div style={{ maxWidth:560, margin:'0 auto' }}>
          <div style={{ fontFamily:'Catamaran, sans-serif', fontWeight:800, fontSize:28, color:'#fff', marginBottom:10 }}>
            Ready to hunt some gremlins?
          </div>
          <p style={{ color:'rgba(255,255,255,0.6)', fontSize:14, marginBottom:28, lineHeight:1.6 }}>
            Drop in your equipment issue and let DR. BLEEP's agents diagnose, analyse,
            and recommend — before your next flatline.
          </p>
          <button
            onClick={() => onNavigate('query')}
            style={{
              background:'var(--blue)', color:'#fff',
              border:'none', borderRadius:8,
              padding:'14px 36px', fontSize:15, fontWeight:800,
              fontFamily:'Catamaran, sans-serif',
              cursor:'pointer', letterSpacing:'-0.01em',
              boxShadow:'0 4px 20px rgba(74,144,112,0.4)',
              transition:'transform 0.15s, box-shadow 0.15s',
            }}
            onMouseEnter={e => { e.currentTarget.style.transform='translateY(-2px)'; e.currentTarget.style.boxShadow='0 8px 28px rgba(74,144,112,0.5)' }}
            onMouseLeave={e => { e.currentTarget.style.transform='translateY(0)'; e.currentTarget.style.boxShadow='0 4px 20px rgba(74,144,112,0.4)' }}
          >
            🩺 Start Diagnosing
          </button>
        </div>
      </section>

    </div>
  )
}

function SectionHeader({ badge, title, desc }) {
  return (
    <div style={{ textAlign:'center', maxWidth:580, margin:'0 auto' }}>
      <span style={{
        background:'var(--blue-light)', color:'var(--blue)',
        border:'1px solid var(--blue-mid)',
        fontSize:11, fontWeight:700, letterSpacing:'0.7px',
        textTransform:'uppercase', padding:'4px 14px', borderRadius:20,
      }}>{badge}</span>
      <h2 style={{
        fontFamily:'Catamaran, sans-serif', fontWeight:800,
        fontSize:28, color:'var(--navy)',
        marginTop:14, marginBottom:10, letterSpacing:'-0.02em',
      }}>{title}</h2>
      <p style={{ color:'var(--text-muted)', fontSize:14, lineHeight:1.65 }}>{desc}</p>
    </div>
  )
}
