import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from 'recharts'
import { CheckCircle, XCircle } from 'lucide-react'

const LABELS = {
  AnswerRelevancyMetric:     'Answer Relevancy',
  FaithfulnessMetric:        'Faithfulness',
  ContextualPrecisionMetric: 'Context Precision',
  ContextualRecallMetric:    'Context Recall',
  ContextualRelevancyMetric: 'Context Relevancy',
  AnswerCorrectnessMetric:   'Answer Correctness',
  Tone: 'Tone', Accuracy: 'Accuracy', Conciseness: 'Conciseness',
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: 8, padding: '10px 14px', boxShadow: '0 4px 16px rgba(0,0,0,0.1)', fontSize: 12 }}>
      <div style={{ color: 'var(--navy)', fontWeight: 700, marginBottom: 4 }}>{d?.metric}</div>
      <div style={{ color: 'var(--blue)' }}>Score: <strong>{d?.score}%</strong></div>
      <div style={{ color: 'var(--text-light)' }}>Threshold: {d?.threshold}%</div>
    </div>
  )
}

export default function EvalMetricsPanel({ scores }) {
  if (!scores) return null

  const data = Object.entries(scores).map(([key, val]) => ({
    metric:    LABELS[key] || key,
    score:     val?.score     ? Math.round(val.score * 100)     : 0,
    threshold: val?.threshold ? Math.round(val.threshold * 100) : 70,
    passed:    val?.passed,
  }))

  const passCount = data.filter(m => m.passed).length
  const avgScore  = Math.round(data.reduce((s, m) => s + m.score, 0) / data.length)

  return (
    <div style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: 12, padding: 22, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div>
          <div style={{ fontFamily: 'Catamaran, sans-serif', fontSize: 16, fontWeight: 800, color: 'var(--navy)' }}>Evaluation Metrics</div>
          <div style={{ fontSize: 11.5, color: 'var(--text-light)', marginTop: 1 }}>DeepEval · Claude Judge</div>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <div style={{ background: 'var(--success-bg)', border: '1px solid var(--success-bd)', borderRadius: 8, padding: '8px 16px', textAlign: 'center' }}>
            <div style={{ fontSize: 22, fontWeight: 800, color: 'var(--success)', fontFamily: 'Catamaran, sans-serif' }}>{passCount}/{data.length}</div>
            <div style={{ fontSize: 10.5, color: 'var(--text-muted)', marginTop: 1 }}>Passed</div>
          </div>
          <div style={{ background: 'var(--blue-light)', border: '1px solid var(--blue-mid)', borderRadius: 8, padding: '8px 16px', textAlign: 'center' }}>
            <div style={{ fontSize: 22, fontWeight: 800, color: 'var(--blue)', fontFamily: 'Catamaran, sans-serif' }}>{avgScore}%</div>
            <div style={{ fontSize: 10.5, color: 'var(--text-muted)', marginTop: 1 }}>Avg Score</div>
          </div>
        </div>
      </div>

      {/* Metric cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(148px,1fr))', gap: 8, marginBottom: 20 }}>
        {data.map(m => (
          <div key={m.metric} style={{
            background: m.passed ? 'var(--success-bg)' : 'var(--danger-bg)',
            border: `1px solid ${m.passed ? 'var(--success-bd)' : 'var(--danger-bd)'}`,
            borderRadius: 8, padding: '10px 12px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 5 }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, lineHeight: 1.3, maxWidth: '80%' }}>{m.metric}</div>
              {m.passed ? <CheckCircle size={12} color="var(--success)" /> : <XCircle size={12} color="var(--danger)" />}
            </div>
            <div style={{ fontSize: 24, fontWeight: 800, color: m.passed ? 'var(--success)' : 'var(--danger)', lineHeight: 1, fontFamily: 'Catamaran, sans-serif' }}>
              {m.score}%
            </div>
            {/* Progress bar */}
            <div style={{ height: 3, background: 'rgba(0,0,0,0.08)', borderRadius: 2, marginTop: 7 }}>
              <div style={{ height: '100%', width: `${m.score}%`, background: m.passed ? 'var(--success)' : 'var(--danger)', borderRadius: 2, transition: 'width 0.6s ease' }} />
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-light)', marginTop: 5 }}>threshold {m.threshold}%</div>
          </div>
        ))}
      </div>

      {/* Radar chart */}
      <div style={{ background: 'var(--bg-alt)', border: '1px solid var(--border)', borderRadius: 10, padding: '12px 4px' }}>
        <div style={{ color: 'var(--text-light)', fontSize: 10, fontWeight: 700, textAlign: 'center', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4 }}>
          Score Radar
        </div>
        <ResponsiveContainer width="100%" height={230}>
          <RadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
            <PolarGrid stroke="var(--border)" />
            <PolarAngleAxis dataKey="metric" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
            <Tooltip content={<CustomTooltip />} />
            <Radar name="Threshold" dataKey="threshold" stroke="var(--border)" fill="none" strokeDasharray="4 3" />
            <Radar name="Score" dataKey="score" stroke="var(--blue)" fill="var(--blue)" fillOpacity={0.12} strokeWidth={1.5} dot={{ fill: 'var(--blue)', r: 3 }} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
