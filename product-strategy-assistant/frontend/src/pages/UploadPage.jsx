import React, { useState, useCallback } from "react";
import axios from "axios";

const AGENTS = [
  { icon: "📊", name: "Data Analyst Agent", desc: "Parsing sales metrics & trends" },
  { icon: "💬", name: "Customer Feedback Agent", desc: "Sentiment & NLP analysis" },
  { icon: "🌐", name: "Market Research Agent", desc: "Identifying market opportunities" },
  { icon: "🔍", name: "SWOT Analysis Agent", desc: "Strengths, Weaknesses, Opportunities, Threats" },
  { icon: "⚡", name: "Feature Prioritization Agent", desc: "RICE & MoSCoW framework scoring" },
  { icon: "🎯", name: "Strategy Recommendation Agent", desc: "Generating executive roadmap" },
];

export default function UploadPage({ onAnalysisComplete, isAnalyzing, setIsAnalyzing }) {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [activeAgentIndex, setActiveAgentIndex] = useState(-1);
  const [completedAgents, setCompletedAgents] = useState([]);
  const [error, setError] = useState("");

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  }, []);

  const handleAnalyze = async () => {
    if (!file) { setError("Please upload a data file first."); return; }
    setError("");
    setIsAnalyzing(true);
    setCompletedAgents([]);
    setActiveAgentIndex(0);

    // Simulate agent progress while API call runs
    const interval = setInterval(() => {
      setActiveAgentIndex((prev) => {
        if (prev < AGENTS.length - 1) {
          setCompletedAgents((c) => [...c, prev]);
          return prev + 1;
        }
        return prev;
      });
    }, 4000);

    try {
      const form = new FormData();
      form.append("data_file", file);
      const { data } = await axios.post("/api/analysis/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 180000,
      });
      clearInterval(interval);
      setCompletedAgents(AGENTS.map((_, i) => i));
      setActiveAgentIndex(-1);
      setTimeout(() => onAnalysisComplete(data), 600);
    } catch (err) {
      clearInterval(interval);
      setError(err.response?.data?.detail || "Analysis failed. Is the backend running?");
      setIsAnalyzing(false);
      setActiveAgentIndex(-1);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Upload Business Data</h2>
        <p>Upload CSV files with sales data, customer reviews, or product analytics to begin analysis.</p>
      </div>

      {!isAnalyzing ? (
        <>
          <div
            className={`upload-zone ${dragActive ? "drag-active" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            onClick={() => document.getElementById("file-input").click()}
          >
            <div className="upload-icon">📂</div>
            <h3>{file ? file.name : "Drop your CSV file here"}</h3>
            <p>{file ? `${(file.size / 1024).toFixed(1)} KB · Click to change` : "Supports CSV, JSON · Sales data, reviews, analytics"}</p>
            <input
              id="file-input"
              type="file"
              accept=".csv,.json,.txt"
              style={{ display: "none" }}
              onChange={(e) => setFile(e.target.files[0])}
            />
          </div>

          {error && (
            <div style={{ marginTop: 16, padding: "12px 16px", background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 8, color: "var(--accent-danger)", fontSize: 14 }}>
              {error}
            </div>
          )}

          <div style={{ marginTop: 24, display: "flex", gap: 12, alignItems: "center" }}>
            <button className="btn btn-primary" onClick={handleAnalyze} disabled={!file}>
              ▶ Run Multi-Agent Analysis
            </button>
            {file && <span style={{ fontSize: 13, color: "var(--text-muted)" }}>6 agents will process your data (~30–60s)</span>}
          </div>

          <div style={{ marginTop: 40 }}>
            <p className="card-title">Agent Pipeline</p>
            <div className="agent-progress">
              {AGENTS.map((a, i) => (
                <div key={i} className="agent-step" style={{ opacity: 0.5 }}>
                  <span>{a.icon}</span>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 13, color: "var(--text-primary)" }}>{a.name}</div>
                    <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{a.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div>
          <div style={{ marginBottom: 24 }}>
            <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
              Analyzing <strong style={{ color: "var(--text-primary)" }}>{file?.name}</strong> — please wait while agents process your data…
            </p>
          </div>
          <div className="agent-progress">
            {AGENTS.map((a, i) => (
              <div
                key={i}
                className={`agent-step ${activeAgentIndex === i ? "active" : ""} ${completedAgents.includes(i) ? "done" : ""}`}
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                {completedAgents.includes(i) ? (
                  <span style={{ color: "var(--accent-3)", fontSize: 18 }}>✓</span>
                ) : activeAgentIndex === i ? (
                  <div className="spinner" />
                ) : (
                  <span style={{ width: 18, height: 18, display: "inline-block" }} />
                )}
                <div>
                  <div style={{ fontWeight: 600, fontSize: 13, color: activeAgentIndex === i ? "var(--accent)" : completedAgents.includes(i) ? "var(--accent-3)" : "var(--text-muted)" }}>
                    {a.icon} {a.name}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{a.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
