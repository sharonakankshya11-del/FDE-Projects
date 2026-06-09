import { useState, useRef } from 'react'
import { Send, AlertTriangle, Shield, Activity, ChevronDown, ChevronUp, Zap, MessageSquare, Cpu } from 'lucide-react'
import { queryAssistant } from '../utils/api'
import IncidentCard from './IncidentCard'
import HumanReviewPanel from './HumanReviewPanel'
import EvalMetricsPanel from './EvalMetricsPanel'
import RecommendationRenderer from './RecommendationRenderer'

const EQUIPMENT_TYPES = ['', 'MRI System', 'CT Scanner', 'Ventilator', 'Infusion Pump',
  'Patient Monitoring System', 'Defibrillator', 'Ultrasound Scanner', 'ECG Monitor',
  'Anaesthesia Machine', 'X-Ray Machine', 'Laboratory Analyser', 'Pulse Oximeter']

const HOSPITAL_UNITS = ['', 'ICU', 'ER', 'OR', 'Radiology', 'Ward A', 'Ward B', 'NICU', 'CCU']

const EXAMPLE_QUERIES = [
  'MRI machine heat dissipation failure in Radiology after recent maintenance',
  'Ventilator power failures recurring in ICU Unit 3',
  'Infusion pump alerts increasing in Ward B, tool wear above 180 minutes',
  'CT scanner overstress failures with high torque readings',
]

export default function ChatInterface() {
  const [query, setQuery] = useState('')
  const [equipmentType, setEquipmentType] = useState('')
  const [hospitalUnit, setHospitalUnit] = useState('')
  const [severity, setSeverity] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showIncidents, setShowIncidents] = useState(false)
  const [showMessages, setShowMessages] = useState(false)
  const textareaRef = useRef(null)

  const handleSubmit = async () => {
    if (!query.trim() || loading) return
    setLoading(true); setError(null); setResult(null)
    try {
      const res = await queryAssistant({
        query: query.trim(),
        equipment_type: equipmentType || undefined,
        hospital_unit: hospitalUnit || undefined,
        severity: severity || undefined,
      })
      setResult(res)
      setShowIncidents(true)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSubmit()
  }

  const handleReviewComplete = (reviewResult) => {
    setResult(prev => prev ? { ...prev, recommendation: reviewResult.final_response, awaiting_human_review: false } : prev)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>

      {/* Example query chips */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {EXAMPLE_QUERIES.map((q, i) => (
          <button key={i} onClick={() => setQuery(q)} style={{
            background: 'var(--blue-light)', border: '1px solid var(--blue-mid)',
            borderRadius: 20, padding: '5px 14px',
            color: 'var(--navy)', fontSize: 12, cursor: 'pointer',
            fontFamily: 'inherit', fontWeight: 600,
            transition: 'all 0.15s ease',
          }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--blue)'; e.currentTarget.style.color = '#fff' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'var(--blue-light)'; e.currentTarget.style.color = 'var(--navy)' }}
          >
            {q.length > 52 ? q.slice(0, 52) + '…' : q}
          </button>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        {[
          ['Equipment Type', equipmentType, setEquipmentType, EQUIPMENT_TYPES],
          ['Hospital Unit',  hospitalUnit,  setHospitalUnit,  HOSPITAL_UNITS],
        ].map(([label, val, setter, opts]) => (
          <select key={label} value={val} onChange={e => setter(e.target.value)} style={selectStyle}>
            <option value="">{label}</option>
            {opts.filter(Boolean).map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        ))}
        <select value={severity} onChange={e => setSeverity(e.target.value)} style={selectStyle}>
          <option value="">All Severities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Query input */}
      <div style={{ position: 'relative' }}>
        <textarea
          ref={textareaRef}
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe the equipment issue… (Ctrl+Enter to submit)"
          rows={3}
          style={{
            width: '100%', padding: '14px 58px 14px 16px',
            background: '#fff',
            border: '1px solid var(--border)',
            borderRadius: 8, color: 'var(--text)', fontSize: 14,
            resize: 'none', lineHeight: 1.6,
            transition: 'border-color 0.15s, box-shadow 0.15s',
            boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
          }}
          onFocus={e => { e.target.style.borderColor = 'var(--blue)'; e.target.style.boxShadow = '0 0 0 3px rgba(74,144,112,0.15)' }}
          onBlur={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.boxShadow = '0 1px 4px rgba(0,0,0,0.04)' }}
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !query.trim()}
          style={{
            position: 'absolute', right: 10, bottom: 10,
            background: loading || !query.trim() ? 'var(--bg-alt)' : 'var(--navy)',
            border: 'none', borderRadius: 7,
            padding: '9px 12px',
            cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
            transition: 'background 0.15s',
          }}
        >
          {loading
            ? <div style={{ width: 16, height: 16, border: '2px solid var(--blue-mid)', borderTopColor: 'var(--blue)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
            : <Send size={15} color={!query.trim() ? 'var(--text-light)' : '#fff'} />
          }
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div style={{
          background: 'var(--blue-light)', border: '1px solid var(--blue-mid)',
          borderRadius: 8, padding: '14px 18px',
          display: 'flex', alignItems: 'center', gap: 12,
        }}>
          <div style={{ display: 'flex', gap: 5 }}>
            {[0,1,2].map(i => (
              <div key={i} style={{
                width: 7, height: 7, borderRadius: '50%', background: 'var(--blue)',
                animation: `pulse-dot 1.2s ease-in-out ${i*0.2}s infinite`,
              }} />
            ))}
          </div>
          <span style={{ color: 'var(--navy)', fontSize: 13, fontWeight: 600 }}>
            Running multi-agent pipeline…
          </span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          background: 'var(--danger-bg)', border: '1px solid var(--danger-bd)',
          borderRadius: 8, padding: '12px 16px',
          display: 'flex', gap: 10, alignItems: 'flex-start',
        }}>
          <AlertTriangle size={15} color="var(--danger)" style={{ marginTop: 1, flexShrink: 0 }} />
          <span style={{ color: 'var(--danger)', fontSize: 13 }}>{error}</span>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', padding: '44px 20px', gap: 14,
          border: '2px dashed var(--border)',
          borderRadius: 12, background: 'var(--bg-alt)',
        }}>
          <div style={{
            width: 54, height: 54, borderRadius: 14,
            background: 'var(--blue-light)', border: '1px solid var(--blue-mid)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Cpu size={24} color="var(--blue)" strokeWidth={1.5} />
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ color: 'var(--text)', fontSize: 14, fontWeight: 600 }}>
              Enter a query above or pick an example
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 4 }}>
              The pipeline will retrieve incidents · detect anomalies · generate a recommendation
            </div>
          </div>
          <div style={{ display: 'flex', gap: 20, marginTop: 4 }}>
            {[['Retrieval','#4a9070'],['Analysis','#7c3aed'],['Maintenance','#0891b2'],['Recommendation','#1a7a4a']].map(([label, color]) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{ width: 7, height: 7, borderRadius: '50%', background: color }} />
                <span style={{ fontSize: 11.5, color: 'var(--text-muted)' }}>{label}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14, animation: 'fade-in 0.25s ease' }}>

          {/* Status badges */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <Badge
              label={`Confidence ${Math.round(result.confidence * 100)}%`}
              success={result.confidence > 0.75} warn={result.confidence > 0.5}
            />
            <Badge
              label={`Failure Risk ${Math.round(result.failure_probability * 100)}%`}
              danger={result.failure_probability > 0.7} warn={result.failure_probability > 0.4}
            />
            {result.escalation_triggered && <Badge label="⚠ ESCALATED" danger />}
            {result.fallback_triggered    && <Badge label="⚡ Fallback"  warn />}
          </div>

          {/* Warning */}
          {result.output_warning && (
            <div style={{ background: 'var(--warning-bg)', border: '1px solid var(--warning-bd)', borderRadius: 8, padding: '10px 14px' }}>
              <span style={{ color: 'var(--warning)', fontSize: 13 }}>{result.output_warning}</span>
            </div>
          )}

          {/* Escalation */}
          {result.escalation_triggered && result.escalation_reason && (
            <div style={{ background: 'var(--danger-bg)', border: '1px solid var(--danger-bd)', borderRadius: 8, padding: '10px 14px', display: 'flex', gap: 10 }}>
              <AlertTriangle size={14} color="var(--danger)" style={{ marginTop: 1, flexShrink: 0 }} />
              <span style={{ color: 'var(--danger)', fontSize: 13 }}>{result.escalation_reason}</span>
            </div>
          )}

          {/* Recommendation */}
          <div style={{
            background: '#fff', border: '1px solid var(--border)',
            borderLeft: '4px solid var(--navy)',
            borderRadius: 10, padding: 22,
            boxShadow: '0 2px 12px rgba(45,74,58,0.06)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
              <div style={{
                width: 32, height: 32, borderRadius: 8,
                background: 'var(--blue-light)', border: '1px solid var(--blue-mid)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Shield size={16} color="var(--blue)" />
              </div>
              <span style={{
                fontFamily: 'Catamaran, sans-serif',
                color: 'var(--navy)', fontWeight: 800, fontSize: 16,
              }}>
                Reliability Recommendation
              </span>
            </div>

            <RecommendationRenderer
              text={result.recommendation}
              confidence={result.confidence}
            />

            {result.citations?.length > 0 && (
              <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid var(--border-light)', display: 'flex', gap: 8 }}>
                <span style={{ color: 'var(--text-light)', fontSize: 12 }}>Citations:</span>
                <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>{result.citations.join(' · ')}</span>
              </div>
            )}
          </div>

          {result.awaiting_human_review && (
            <HumanReviewPanel sessionId={result.session_id} recommendation={result.recommendation} onReviewComplete={handleReviewComplete} />
          )}

          {result.correlation_summary && (
            <ReportCard
              icon="📈"
              title="Correlation Analysis"
              accent="#7c3aed"
              accentBg="#f5f0fe"
              subtitle="Statistical patterns detected across retrieved incidents"
            >
              <RecommendationRenderer text={result.correlation_summary} />
            </ReportCard>
          )}

          {result.maintenance_patterns && (
            <ReportCard
              icon="🔧"
              title="Maintenance Patterns"
              accent="#2d4a3a"
              accentBg="#edf5f0"
              subtitle="Recurring maintenance trends from historical data"
            >
              <RecommendationRenderer text={result.maintenance_patterns} />
            </ReportCard>
          )}

          {result.retrieved_incidents?.length > 0 && (
            <Collapsible
              label={`Retrieved Incidents (${result.retrieved_incidents.length})`}
              icon={<AlertTriangle size={14} color="var(--warning)" />}
              isOpen={showIncidents} onToggle={() => setShowIncidents(v => !v)}
            >
              {result.retrieved_incidents.map((inc, i) => <IncidentCard key={inc.id} incident={inc} rank={i + 1} />)}
            </Collapsible>
          )}

          {result.agent_messages?.length > 0 && (
            <ReportCard
              icon="🤖"
              title="Agent Pipeline Log"
              accent="#546e7a"
              accentBg="#f2f5f4"
              subtitle="Step-by-step execution trace across all agents"
              collapsible
              defaultCollapsed
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                {result.agent_messages.map((m, i) => {
                  const AGENT_META = {
                    supervisor:           { label: 'Supervisor',      color: '#2d4a3a', icon: '🧠' },
                    retrieval_agent:      { label: 'Retrieval',       color: '#4a7c9e', icon: '🔍' },
                    analysis_agent:       { label: 'Analysis',        color: '#7c3aed', icon: '📈' },
                    maintenance_agent:    { label: 'Maintenance',     color: '#4a9070', icon: '🔧' },
                    recommendation_agent: { label: 'Recommendation',  color: '#8a6214', icon: '✅' },
                    human:                { label: 'Human Review',    color: '#9a3232', icon: '👤' },
                  }
                  const meta = AGENT_META[m.role] || { label: m.role, color: 'var(--text-muted)', icon: '•' }
                  const isLast = i === result.agent_messages.length - 1
                  return (
                    <div key={i} style={{ display: 'flex', gap: 12, paddingBottom: isLast ? 0 : 12, position: 'relative' }}>
                      {/* Timeline line */}
                      {!isLast && (
                        <div style={{ position: 'absolute', left: 15, top: 28, bottom: 0, width: 1, background: 'var(--border)' }} />
                      )}
                      {/* Icon dot */}
                      <div style={{
                        width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
                        background: `${meta.color}18`, border: `1px solid ${meta.color}30`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 13, zIndex: 1,
                      }}>{meta.icon}</div>
                      <div style={{ flex: 1, paddingTop: 5 }}>
                        <span style={{
                          fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase',
                          letterSpacing: '0.5px', color: meta.color,
                        }}>{meta.label}</span>
                        <p style={{ fontSize: 12.5, color: 'var(--text-muted)', marginTop: 2, lineHeight: 1.55 }}>
                          {m.content}
                        </p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </ReportCard>
          )}

          {result.eval_scores && <EvalMetricsPanel scores={result.eval_scores} />}
        </div>
      )}
    </div>
  )
}

function ReportCard({ icon, title, subtitle, accent, accentBg, children, collapsible = false, defaultCollapsed = false }) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed)
  return (
    <div style={{
      background: '#fff',
      border: `1px solid ${accent}22`,
      borderLeft: `4px solid ${accent}`,
      borderRadius: 10,
      overflow: 'hidden',
      boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
    }}>
      <div
        onClick={collapsible ? () => setCollapsed(v => !v) : undefined}
        style={{
          background: accentBg,
          padding: '12px 18px',
          display: 'flex', alignItems: 'center', gap: 10,
          borderBottom: collapsed ? 'none' : `1px solid ${accent}18`,
          cursor: collapsible ? 'pointer' : 'default',
          userSelect: 'none',
        }}
      >
        <span style={{ fontSize: 16 }}>{icon}</span>
        <div style={{ flex: 1 }}>
          <div style={{
            fontFamily: 'Catamaran, sans-serif', fontWeight: 800,
            fontSize: 14, color: accent, textTransform: 'uppercase', letterSpacing: '0.02em',
          }}>{title}</div>
          {subtitle && !collapsed && (
            <div style={{ fontSize: 11.5, color: 'var(--text-light)', marginTop: 1 }}>{subtitle}</div>
          )}
        </div>
        {collapsible && (
          <span style={{ color: 'var(--text-light)', fontSize: 13 }}>{collapsed ? '▼' : '▲'}</span>
        )}
      </div>
      {!collapsed && (
        <div style={{ padding: '16px 18px' }}>{children}</div>
      )}
    </div>
  )
}

function Badge({ label, success, warn, danger }) {
  const color   = danger ? 'var(--danger)'  : warn ? 'var(--warning)'  : success ? 'var(--success)'  : 'var(--text-muted)'
  const bg      = danger ? 'var(--danger-bg)' : warn ? 'var(--warning-bg)' : success ? 'var(--success-bg)' : 'var(--bg-alt)'
  const border  = danger ? 'var(--danger-bd)' : warn ? 'var(--warning-bd)' : success ? 'var(--success-bd)' : 'var(--border)'
  return (
    <span style={{ background: bg, border: `1px solid ${border}`, color, borderRadius: 20, padding: '4px 13px', fontSize: 12, fontWeight: 700 }}>
      {label}
    </span>
  )
}

function Collapsible({ label, icon, children, isOpen: ctrl, onToggle, defaultOpen = false }) {
  const [internal, setInternal] = useState(defaultOpen)
  const open   = ctrl !== undefined ? ctrl : internal
  const toggle = onToggle || (() => setInternal(v => !v))
  return (
    <div style={{ border: '1px solid var(--border)', borderRadius: 9, overflow: 'hidden', background: '#fff', boxShadow: '0 1px 4px rgba(0,0,0,0.04)' }}>
      <button onClick={toggle} style={{
        width: '100%', background: open ? 'var(--bg-alt)' : '#fff',
        border: 'none', padding: '11px 16px', cursor: 'pointer',
        display: 'flex', alignItems: 'center', gap: 9,
        transition: 'background 0.12s', fontFamily: 'inherit',
      }}>
        {icon}
        <span style={{ color: 'var(--text)', fontSize: 13.5, fontWeight: 600, flex: 1, textAlign: 'left' }}>{label}</span>
        {open ? <ChevronUp size={14} color="var(--text-light)" /> : <ChevronDown size={14} color="var(--text-light)" />}
      </button>
      {open && (
        <div style={{ padding: '14px 16px', borderTop: '1px solid var(--border-light)' }}>
          {children}
        </div>
      )}
    </div>
  )
}

const selectStyle = {
  background: '#fff', border: '1px solid var(--border)',
  borderRadius: 7, padding: '7px 12px',
  color: 'var(--text)', fontSize: 13, cursor: 'pointer',
  boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
  transition: 'border-color 0.15s',
}
