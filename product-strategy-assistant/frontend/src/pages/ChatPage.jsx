import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

const SUGGESTIONS = [
  "What are the top strategic priorities for next quarter?",
  "Which product categories have the highest growth potential?",
  "What customer complaints should we address first?",
  "Summarize the SWOT analysis in plain English",
  "What are the must-have features to build next?",
];

export default function ChatPage({ analysisData }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hello! I'm your AI Product Strategy Advisor. I've analyzed your business data and I'm ready to answer questions about your strategy, customers, market opportunities, and roadmap. What would you like to know?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text) => {
    const msg = text || input.trim();
    if (!msg || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: msg }]);
    setLoading(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const { data } = await axios.post("/api/chat/message", {
        message: msg,
        analysis_context: analysisData || {},
        history,
      });
      setMessages((m) => [...m, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "assistant", content: "Sorry, I couldn't reach the backend. Make sure the API server is running." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>AI Strategy Chat</h2>
        <p>Ask anything about your product strategy, market, customers, or roadmap.</p>
      </div>

      {!analysisData && (
        <div style={{ padding: "12px 16px", background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.2)", borderRadius: 8, marginBottom: 16, fontSize: 13, color: "var(--accent-warn)" }}>
          ⚠ No analysis data loaded. Upload data first for context-aware answers.
        </div>
      )}

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              {m.role === "assistant" ? (
                <ReactMarkdown>{m.content}</ReactMarkdown>
              ) : (
                m.content
              )}
            </div>
          ))}
          {loading && (
            <div className="message assistant" style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div className="spinner" /> Thinking…
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {messages.length === 1 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, paddingBottom: 12 }}>
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                className="btn btn-outline"
                style={{ fontSize: 12, padding: "6px 14px" }}
                onClick={() => send(s)}
              >
                {s}
              </button>
            ))}
          </div>
        )}

        <div className="chat-input-row">
          <textarea
            className="chat-input"
            rows={2}
            placeholder="Ask about strategy, market, features, roadmap…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
          />
          <button className="btn btn-primary" onClick={() => send()} disabled={!input.trim() || loading} style={{ alignSelf: "flex-end" }}>
            Send ▶
          </button>
        </div>
      </div>
    </div>
  );
}
