import React from "react";

const NAV_ITEMS = [
  { id: "upload", icon: "⬆", label: "Upload Data", requiresData: false },
  { id: "dashboard", icon: "◉", label: "Dashboard", requiresData: true },
  { id: "chat", icon: "◎", label: "AI Chat", requiresData: true },
  { id: "report", icon: "▤", label: "Report", requiresData: true },
];

export default function Sidebar({ activePage, onNavigate, hasData }) {
  return (
    <nav className="sidebar">
      <div className="sidebar-logo">
        <h1>Product Strategy Assistant</h1>
        <p>Multi-Agent AI System</p>
      </div>

      {NAV_ITEMS.map((item) => (
        <div
          key={item.id}
          className={[
            "nav-item",
            activePage === item.id ? "active" : "",
            item.requiresData && !hasData ? "disabled" : "",
          ].join(" ")}
          onClick={() => !item.requiresData || hasData ? onNavigate(item.id) : null}
        >
          <span className="nav-icon">{item.icon}</span>
          {item.label}
          {item.requiresData && !hasData && (
            <span style={{ marginLeft: "auto", fontSize: 10, color: "var(--text-muted)" }}>locked</span>
          )}
        </div>
      ))}

      <div className="sidebar-footer">
        6 agents · Claude AI<br />
        v1.0.0
      </div>
    </nav>
  );
}
