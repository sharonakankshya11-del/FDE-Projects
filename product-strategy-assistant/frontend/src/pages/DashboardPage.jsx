import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Cell,
} from "recharts";

const COLORS = ["#00d4ff", "#7c3aed", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

export default function DashboardPage({ data, onNavigate }) {
  if (!data) return null;
  const da = data.data_analysis || {};
  const cf = data.customer_feedback || {};
  const mr = data.market_research || {};
  const sw = data.swot_analysis || {};
  const fp = data.feature_prioritization || {};
  const sr = data.strategy_recommendation || {};

  // Build chart data
  const regionData = Object.entries(da.revenue_by_region || {}).map(([k, v]) => ({ name: k, revenue: typeof v === "number" ? v : parseFloat(v) || 0 }));
  const categoryData = Object.entries(da.revenue_by_category || {}).map(([k, v]) => ({ name: k, revenue: typeof v === "number" ? v : parseFloat(v) || 0 }));
  const topProducts = (da.top_products || []).slice(0, 6);

  const swotRadar = [
    { metric: "Strengths", value: (sw.strengths || []).length * 20 },
    { metric: "Opportunities", value: (sw.opportunities || []).length * 20 },
    { metric: "Weaknesses", value: 100 - (sw.weaknesses || []).length * 15 },
    { metric: "Threats", value: 100 - (sw.threats || []).length * 15 },
    { metric: "NPS", value: Math.max(0, ((cf.nps_estimate || 0) + 100) / 2) },
    { metric: "Opp. Score", value: sr.opportunity_score || 50 },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h2>Strategy Dashboard</h2>
          <p>Synthesized insights from 6 AI agents · {data.agents_completed || 6} agents completed</p>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn btn-outline" onClick={() => onNavigate("chat")}>💬 Ask AI</button>
          <button className="btn btn-primary" onClick={() => onNavigate("report")}>📄 Generate Report</button>
        </div>
      </div>

      {/* Metric strip */}
      <div className="metric-grid">
        <MetricCard label="Opportunity Score" value={`${sr.opportunity_score || "—"}`} sub="out of 100" />
        <MetricCard label="NPS Estimate" value={cf.nps_estimate != null ? cf.nps_estimate : "—"} sub="net promoter score" color={cf.nps_estimate > 30 ? "var(--accent-3)" : cf.nps_estimate > 0 ? "var(--accent-warn)" : "var(--accent-danger)"} />
        <MetricCard label="Sentiment" value={cf.sentiment_score != null ? `${cf.sentiment_score}/10` : "—"} sub={cf.overall_sentiment || ""} />
        <MetricCard label="Risk Level" value={sr.risk_level || "—"} sub="strategy risk" color={sr.risk_level === "low" ? "var(--accent-3)" : sr.risk_level === "high" ? "var(--accent-danger)" : "var(--accent-warn)"} />
        <MetricCard label="Avg Rating" value={da.avg_customer_rating ? `${Number(da.avg_customer_rating).toFixed(1)}★` : "—"} sub="customer rating" />
        <MetricCard label="Must-Have Features" value={(fp.must_have || []).length} sub="high priority" color="var(--accent)" />
      </div>

      {/* Executive Summary */}
      {sr.executive_summary && (
        <div className="card" style={{ marginBottom: 20, borderLeft: "3px solid var(--accent)" }}>
          <p className="card-title">Executive Summary</p>
          <p style={{ color: "var(--text-secondary)", fontSize: 14, lineHeight: 1.8 }}>{sr.executive_summary}</p>
        </div>
      )}

      {/* Charts row */}
      {(regionData.length > 0 || categoryData.length > 0) && (
        <div className="grid-2" style={{ marginBottom: 20 }}>
          {regionData.length > 0 && (
            <div className="card">
              <p className="card-title">Revenue by Region</p>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={regionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2d45" />
                  <XAxis dataKey="name" tick={{ fill: "#8fa3bf", fontSize: 11 }} />
                  <YAxis tick={{ fill: "#8fa3bf", fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e2d45", borderRadius: 8, color: "#f0f6ff" }} />
                  <Bar dataKey="revenue" radius={[4, 4, 0, 0]}>
                    {regionData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          {categoryData.length > 0 && (
            <div className="card">
              <p className="card-title">Revenue by Category</p>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={categoryData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2d45" />
                  <XAxis type="number" tick={{ fill: "#8fa3bf", fontSize: 11 }} />
                  <YAxis dataKey="name" type="category" tick={{ fill: "#8fa3bf", fontSize: 11 }} width={100} />
                  <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1e2d45", borderRadius: 8, color: "#f0f6ff" }} />
                  <Bar dataKey="revenue" radius={[0, 4, 4, 0]}>
                    {categoryData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      <div className="grid-2" style={{ marginBottom: 20 }}>
        {/* SWOT */}
        <div className="card">
          <p className="card-title">SWOT Analysis</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            <SwotQuad title="Strengths" items={sw.strengths || []} color="var(--accent-3)" bg="rgba(16,185,129,0.06)" />
            <SwotQuad title="Weaknesses" items={sw.weaknesses || []} color="var(--accent-danger)" bg="rgba(239,68,68,0.06)" />
            <SwotQuad title="Opportunities" items={sw.opportunities || []} color="var(--accent)" bg="rgba(0,212,255,0.06)" />
            <SwotQuad title="Threats" items={sw.threats || []} color="var(--accent-warn)" bg="rgba(245,158,11,0.06)" />
          </div>
        </div>

        {/* Strategy Radar */}
        <div className="card">
          <p className="card-title">Strategic Health Radar</p>
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={swotRadar}>
              <PolarGrid stroke="#1e2d45" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: "#8fa3bf", fontSize: 11 }} />
              <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
              <Radar dataKey="value" stroke="#00d4ff" fill="#00d4ff" fillOpacity={0.15} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 20 }}>
        {/* Features */}
        <div className="card">
          <p className="card-title">Feature Prioritization (MoSCoW)</p>
          {(fp.must_have || []).slice(0, 3).map((f, i) => (
            <FeatureRow key={i} tag="Must Have" tagClass="tag-green" feature={f.feature || f} score={f.impact_score} />
          ))}
          {(fp.should_have || []).slice(0, 2).map((f, i) => (
            <FeatureRow key={i} tag="Should Have" tagClass="tag-blue" feature={f.feature || f} score={f.impact_score} />
          ))}
          {(fp.could_have || []).slice(0, 2).map((f, i) => (
            <FeatureRow key={i} tag="Could Have" tagClass="tag-yellow" feature={f.feature || f} score={f.impact_score} />
          ))}
        </div>

        {/* Customer Insights */}
        <div className="card">
          <p className="card-title">Customer Insights</p>
          {cf.top_praises?.length > 0 && (
            <>
              <p style={{ fontSize: 11, color: "var(--accent-3)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>Top Praises</p>
              <ul className="insight-list">
                {cf.top_praises.slice(0, 3).map((p, i) => <li key={i}>{p}</li>)}
              </ul>
            </>
          )}
          {cf.top_complaints?.length > 0 && (
            <>
              <p style={{ fontSize: 11, color: "var(--accent-danger)", textTransform: "uppercase", letterSpacing: "0.08em", margin: "14px 0 6px" }}>Top Complaints</p>
              <ul className="insight-list">
                {cf.top_complaints.slice(0, 3).map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </>
          )}
        </div>
      </div>

      {/* Roadmap */}
      {(sr.roadmap_q1 || sr.roadmap_q2) && (
        <div className="card" style={{ marginBottom: 20 }}>
          <p className="card-title">12-Month Product Roadmap</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
            {["roadmap_q1", "roadmap_q2", "roadmap_q3", "roadmap_q4"].map((q, qi) => (
              <div key={q} style={{ background: "var(--bg-secondary)", borderRadius: 8, padding: 14 }}>
                <p style={{ fontSize: 11, fontWeight: 700, color: COLORS[qi], textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>Q{qi + 1}</p>
                <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 6 }}>
                  {(sr[q] || []).map((item, i) => (
                    <li key={i} style={{ fontSize: 12, color: "var(--text-secondary)", display: "flex", gap: 6 }}>
                      <span style={{ color: COLORS[qi] }}>›</span> {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* KPIs */}
      {sr.kpis?.length > 0 && (
        <div className="card">
          <p className="card-title">KPIs & Success Metrics</p>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                {["Metric", "Target", "Timeline"].map((h) => (
                  <th key={h} style={{ textAlign: "left", padding: "8px 12px", fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", borderBottom: "1px solid var(--border)" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sr.kpis.map((k, i) => (
                <tr key={i}>
                  <td style={{ padding: "10px 12px", fontSize: 13, color: "var(--text-primary)", borderBottom: "1px solid var(--border)" }}>{k.metric}</td>
                  <td style={{ padding: "10px 12px", fontSize: 13, color: "var(--accent)", borderBottom: "1px solid var(--border)" }}>{k.target}</td>
                  <td style={{ padding: "10px 12px", fontSize: 13, color: "var(--text-secondary)", borderBottom: "1px solid var(--border)" }}>{k.timeline}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value, sub, color }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value" style={color ? { color } : {}}>{value}</div>
      <div className="metric-sub">{sub}</div>
    </div>
  );
}

function SwotQuad({ title, items, color, bg }) {
  return (
    <div style={{ background: bg, borderRadius: 8, padding: 12 }}>
      <p style={{ fontSize: 11, fontWeight: 700, color, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>{title}</p>
      <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 4 }}>
        {(items || []).slice(0, 3).map((item, i) => (
          <li key={i} style={{ fontSize: 12, color: "var(--text-secondary)", display: "flex", gap: 5 }}>
            <span style={{ color }}>›</span> {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function FeatureRow({ tag, tagClass, feature, score }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
      <span className={`tag ${tagClass}`} style={{ flexShrink: 0, fontSize: 11 }}>{tag}</span>
      <span style={{ fontSize: 13, color: "var(--text-secondary)", flex: 1 }}>{feature}</span>
      {score && <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{score}/10</span>}
    </div>
  );
}
