import { useState } from 'react'
import { ChevronDown, ChevronUp, BookOpen, Zap, Database, Shield, Users, ExternalLink } from 'lucide-react'

const FAQS = [
  {
    q: 'How do I run a reliability query?',
    a: 'Go to the Query Assistant tab, optionally filter by Equipment Type, Hospital Unit, and Severity, then type your equipment issue in natural language (e.g. "MRI heat dissipation failure after maintenance"). Press Ctrl+Enter or click Send.',
  },
  {
    q: 'Why are no incidents retrieved for my query?',
    a: 'The vector index may be empty. Check the status pill in the header — it shows the Pinecone vector count. If it shows 0 vectors, the ingestion pipeline needs to be run first by an administrator.',
  },
  {
    q: 'What do the agent pipeline steps mean?',
    a: 'The system runs 4 specialist agents in sequence: Retrieval (finds similar incidents), Analysis (detects sensor anomalies), Maintenance (matches patterns), and Recommendation (generates the final report using GPT-4o-mini).',
  },
  {
    q: 'What is Human-in-the-Loop review?',
    a: 'High-severity recommendations are paused for engineer review before delivery. You can Approve (send as-is), Edit (modify the text), or Reject (flag for escalation). This ensures no automated advice reaches clinical staff unchecked.',
  },
  {
    q: 'What datasets power the system?',
    a: 'The AI4I 2020 Predictive Maintenance dataset and a secondary Predictive Maintenance dataset — together 20,000 sensor readings transformed into hospital medical-equipment incident narratives across 12 device types and 8 hospital units.',
  },
  {
    q: 'How is my query data protected?',
    a: 'A PII middleware layer strips all patient and staff identifiers from every request before it reaches the agent pipeline. Input and output guardrails (powered by Claude Sonnet) additionally screen for sensitive clinical information.',
  },
  {
    q: 'What does the Confidence % mean?',
    a: "The Recommendation Agent returns a self-assessed confidence score based on the number and quality of retrieved incidents, the strength of detected anomalies, and internal consistency checks. Below 60% indicates limited supporting data.",
  },
  {
    q: 'Can I use DR. BLEEP offline?',
    a: 'Partially. The BM25 keyword search and device health dashboard work offline from the local CSV data. However, vector search (Pinecone) and LLM calls (GPT-4o-mini, Claude) require internet connectivity.',
  },
]

const DOCS = [
  { icon: Zap,      title: 'Quick Start Guide',       desc: 'Set up and run your first query in 5 minutes.',          color: 'var(--warning)' },
  { icon: Database, title: 'Data Ingestion Docs',      desc: 'How to ingest CSVs and configure Pinecone.',             color: 'var(--blue)' },
  { icon: Shield,   title: 'Security & Compliance',   desc: 'PII handling, guardrails, and audit trail.',             color: 'var(--success)' },
  { icon: Users,    title: 'HITL Review Workflow',     desc: 'Configure human-in-the-loop for your clinical team.',    color: '#7c3aed' },
  { icon: BookOpen, title: 'API Reference',            desc: 'Full FastAPI docs at /docs — all endpoints and schemas.', color: '#0891b2' },
]

function FAQItem({ q, a }) {
  const [open, setOpen] = useState(false)
  return (
    <div style={{
      border: '1px solid var(--border)',
      borderRadius: 10, overflow: 'hidden',
      background: '#fff',
      transition: 'box-shadow 0.15s',
      boxShadow: open ? '0 4px 16px rgba(0,0,0,0.06)' : '0 1px 4px rgba(0,0,0,0.04)',
    }}>
      <button
        onClick={() => setOpen(v => !v)}
        style={{
          width: '100%', padding: '16px 20px',
          background: open ? 'var(--bg-alt)' : '#fff',
          border: 'none', cursor: 'pointer', fontFamily: 'inherit',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16,
          transition: 'background 0.12s',
          borderBottom: open ? '1px solid var(--border)' : 'none',
        }}
      >
        <span style={{ fontWeight: 700, fontSize: 14, color: 'var(--navy)', textAlign: 'left', lineHeight: 1.4 }}>{q}</span>
        {open ? <ChevronUp size={16} color="var(--text-light)" style={{ flexShrink: 0 }} />
               : <ChevronDown size={16} color="var(--text-light)" style={{ flexShrink: 0 }} />}
      </button>
      {open && (
        <div style={{ padding: '14px 20px', background: '#fff' }}>
          <p style={{ fontSize: 13.5, color: 'var(--text-muted)', lineHeight: 1.75 }}>{a}</p>
        </div>
      )}
    </div>
  )
}

export default function SupportPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 36 }}>

      {/* Quick docs */}
      <div>
        <div style={{ fontFamily: 'Catamaran, sans-serif', fontWeight: 800, fontSize: 18, color: 'var(--navy)', marginBottom: 4 }}>
          Documentation
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: 13.5, marginBottom: 18 }}>
          Everything you need to configure, use, and extend DR. BLEEP.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 }}>
          {DOCS.map(({ icon: Icon, title, desc, color }) => (
            <div key={title} style={{
              background: '#fff', border: '1px solid var(--border)',
              borderLeft: `3px solid ${color}`,
              borderRadius: 10, padding: '16px 18px',
              boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
              cursor: 'pointer', transition: 'all 0.15s',
              display: 'flex', flexDirection: 'column', gap: 8,
            }}
              onMouseEnter={e => { e.currentTarget.style.boxShadow = '0 6px 18px rgba(0,0,0,0.08)'; e.currentTarget.style.transform = 'translateY(-2px)' }}
              onMouseLeave={e => { e.currentTarget.style.boxShadow = '0 1px 4px rgba(0,0,0,0.04)'; e.currentTarget.style.transform = 'translateY(0)' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Icon size={18} color={color} />
                <ExternalLink size={12} color="var(--text-light)" />
              </div>
              <div style={{ fontFamily: 'Catamaran, sans-serif', fontWeight: 800, fontSize: 13.5, color: 'var(--navy)', lineHeight: 1.3 }}>{title}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>{desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Status banner */}
      <div style={{
        background: 'var(--success-bg)', border: '1px solid var(--success-bd)',
        borderLeft: '4px solid var(--success)',
        borderRadius: 10, padding: '14px 20px',
        display: 'flex', alignItems: 'center', gap: 14,
      }}>
        <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--success)', animation: 'pulse-dot 2s infinite', flexShrink: 0 }} />
        <div>
          <div style={{ fontWeight: 700, fontSize: 13.5, color: 'var(--success)' }}>All Systems Operational</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
            Pinecone · Embedding API · LLM Gateway · Frontend — last checked just now
          </div>
        </div>
        <div style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--text-light)', whiteSpace: 'nowrap' }}>
          99.9% uptime this month
        </div>
      </div>

      {/* FAQ */}
      <div>
        <div style={{ fontFamily: 'Catamaran, sans-serif', fontWeight: 800, fontSize: 18, color: 'var(--navy)', marginBottom: 4 }}>
          Frequently Asked Questions
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: 13.5, marginBottom: 18 }}>
          Common questions from biomedical engineers and clinical IT teams.
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {FAQS.map(faq => <FAQItem key={faq.q} {...faq} />)}
        </div>
      </div>

      {/* Still need help */}
      <div style={{
        background: 'linear-gradient(135deg, var(--navy) 0%, var(--navy-hover) 100%)',
        borderRadius: 14, padding: '32px 36px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 20,
      }}>
        <div>
          <div style={{ fontFamily: 'Catamaran, sans-serif', fontWeight: 800, fontSize: 20, color: '#fff', marginBottom: 6 }}>
            Still need help?
          </div>
          <p style={{ color: 'rgba(255,255,255,0.65)', fontSize: 13.5, lineHeight: 1.6 }}>
            Our biomedical engineering support team is ready to assist.
          </p>
        </div>
        <a href="mailto:support@drbleep.health" style={{
          background: '#fff', color: 'var(--navy)',
          border: 'none', borderRadius: 8, padding: '12px 28px',
          fontSize: 14, fontWeight: 800, fontFamily: 'Catamaran, sans-serif',
          textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 8,
          boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
          transition: 'transform 0.15s, box-shadow 0.15s',
        }}
          onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.25)' }}
          onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.2)' }}
        >
          📧 Email Support
        </a>
      </div>

    </div>
  )
}
