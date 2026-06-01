import React, { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

export default function ReportPage({ analysisData }) {
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [filename, setFilename] = useState("");

  const generate = async () => {
    if (!analysisData) return;
    setLoading(true);
    setReport("");
    try {
      const { data } = await axios.post("/api/report/generate-markdown", {
        analysis: analysisData,
      });
      setReport(data.report);
      setFilename(data.filename);
    } catch (err) {
      setReport("**Error:** Could not generate report. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const download = () => {
    const blob = new Blob([report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename || "strategy-report.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h2>Executive Report</h2>
          <p>Generate a comprehensive strategy report from all agent analyses.</p>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          {report && (
            <button className="btn btn-outline" onClick={download}>⬇ Download .md</button>
          )}
          <button className="btn btn-primary" onClick={generate} disabled={loading || !analysisData}>
            {loading ? "Generating…" : "✦ Generate Report"}
          </button>
        </div>
      </div>

      {!analysisData && (
        <div style={{ padding: "12px 16px", background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.2)", borderRadius: 8, fontSize: 13, color: "var(--accent-warn)" }}>
          ⚠ Run an analysis first before generating a report.
        </div>
      )}

      {loading && (
        <div style={{ display: "flex", alignItems: "center", gap: 12, padding: 24, color: "var(--text-secondary)", fontSize: 14 }}>
          <div className="spinner" /> Compiling executive report from all agent outputs…
        </div>
      )}

      {report && (
        <div className="card report-body" style={{ maxWidth: 900 }}>
          <ReactMarkdown>{report}</ReactMarkdown>
        </div>
      )}

      {!report && !loading && analysisData && (
        <div style={{ textAlign: "center", padding: "80px 40px", color: "var(--text-muted)" }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📋</div>
          <p style={{ fontSize: 16, color: "var(--text-secondary)" }}>Click "Generate Report" to create your executive strategy document</p>
        </div>
      )}
    </div>
  );
}
