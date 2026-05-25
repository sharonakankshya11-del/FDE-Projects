import { useEffect, useState } from "react";
import analyticsService from "../services/analyticsService";

// ─── colour palette per category ────────────────────────────────────────────
const CAT_COLORS = {
  Fiction:      "#6366f1",
  Technology:   "#0ea5e9",
  Science:      "#10b981",
  History:      "#f59e0b",
  Biography:    "#ec4899",
  "Self-Help":  "#8b5cf6",
  Mystery:      "#ef4444",
  "Non-Fiction":"#14b8a6",
};
const colorFor = (cat) => CAT_COLORS[cat] ?? "#94a3b8";

// ─── tiny helpers ────────────────────────────────────────────────────────────
const fmt = (iso) =>
  iso ? new Date(iso).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "—";

const fmtDT = (iso) =>
  iso
    ? new Date(iso).toLocaleString("en-IN", {
        day: "2-digit", month: "short", year: "numeric",
        hour: "2-digit", minute: "2-digit",
      })
    : "Not run yet";

export default function Analytics() {
  const [summary,   setSummary]   = useState(null);
  const [mostBorrowed, setMostBorrowed] = useState([]);
  const [catStats, setCatStats]   = useState([]);
  const [trends,   setTrends]     = useState([]);
  const [overdue,  setOverdue]    = useState([]);
  const [etl,      setEtl]        = useState(null);
  const [loading,  setLoading]    = useState(true);
  const [error,    setError]      = useState("");

  useEffect(() => {
    Promise.all([
      analyticsService.getSummary(),
      analyticsService.getMostBorrowed(10),
      analyticsService.getCategoryStats(),
      analyticsService.getMonthlyTrends(),
      analyticsService.getOverdue(),
      analyticsService.getEtlStatus(),
    ])
      .then(([s, mb, cs, t, od, etlS]) => {
        setSummary(s.data);
        setMostBorrowed(mb.data);
        setCatStats(cs.data);
        // only show last 12 months
        const last12 = t.data.slice(-12);
        setTrends(last12);
        setOverdue(od.data);
        setEtl(etlS.data);
      })
      .catch(() => setError("Failed to load analytics data."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="analytics-loading">⏳ Loading analytics…</div>;
  if (error)   return <div className="alert alert-error">{error}</div>;

  const maxBorrow = Math.max(...mostBorrowed.map((b) => b.borrow_count), 1);
  const maxCat    = Math.max(...catStats.map((c) => c.borrow_count), 1);
  const maxTrend  = Math.max(...trends.flatMap((t) => [t.borrow_count, t.return_count]), 1);

  return (
    <div className="analytics-page">

      {/* ── ETL Status Banner ──────────────────────────────────── */}
      {etl && (
        <div className={`etl-banner ${etl.status === "success" ? "etl-success" : "etl-pending"}`}>
          <span className="etl-icon">{etl.status === "success" ? "✅" : "⚠️"}</span>
          <div className="etl-info">
            <strong>ETL Pipeline</strong>
            {etl.last_run
              ? ` — Last run: ${fmtDT(etl.last_run)}  |
                  Books: ${etl.books_loaded}  •
                  Borrowers: ${etl.borrowers_loaded}  •
                  Transactions: ${etl.transactions_loaded}  |
                  Duration: ${etl.duration_seconds}s`
              : " — Pipeline has not been run yet. Run: python run_etl.py"}
          </div>
        </div>
      )}

      <h1 className="page-title">📊 Analytics Dashboard</h1>

      {/* ── Summary KPI Cards ──────────────────────────────────── */}
      {summary && (
        <div className="kpi-grid">
          <div className="kpi-card kpi-blue">
            <div className="kpi-value">{summary.total_transactions}</div>
            <div className="kpi-label">Total Transactions</div>
          </div>
          <div className="kpi-card kpi-green">
            <div className="kpi-value">{summary.active_borrows}</div>
            <div className="kpi-label">Active Borrows</div>
          </div>
          <div className="kpi-card kpi-red">
            <div className="kpi-value">{summary.overdue_count}</div>
            <div className="kpi-label">Overdue Books</div>
          </div>
          <div className="kpi-card kpi-purple">
            <div className="kpi-value">{summary.returned_count}</div>
            <div className="kpi-label">Returned</div>
          </div>
          <div className="kpi-card kpi-orange">
            <div className="kpi-value">{summary.avg_borrow_duration_days}d</div>
            <div className="kpi-label">Avg Borrow Duration</div>
          </div>
          <div className="kpi-card kpi-teal">
            <div className="kpi-value" style={{ fontSize: "1.1rem" }}>
              {summary.most_popular_category}
            </div>
            <div className="kpi-label">Top Category</div>
          </div>
        </div>
      )}

      {/* ── Row: Most Borrowed  +  Category Distribution ───────── */}
      <div className="analytics-row">

        {/* Most Borrowed Books */}
        <div className="chart-card">
          <h2 className="chart-title">📚 Top 10 Most Borrowed Books</h2>
          <div className="hbar-list">
            {mostBorrowed.map((b, i) => (
              <div key={b.book_id} className="hbar-row">
                <div className="hbar-rank">#{i + 1}</div>
                <div className="hbar-info">
                  <div className="hbar-label" title={b.title}>{b.title}</div>
                  <div className="hbar-meta">{b.author} · <span style={{ color: colorFor(b.category) }}>{b.category}</span></div>
                  <div className="hbar-track">
                    <div
                      className="hbar-fill"
                      style={{
                        width: `${(b.borrow_count / maxBorrow) * 100}%`,
                        background: colorFor(b.category),
                      }}
                    />
                  </div>
                </div>
                <div className="hbar-count">{b.borrow_count}</div>
              </div>
            ))}
            {mostBorrowed.length === 0 && <p className="no-data">No data yet.</p>}
          </div>
        </div>

        {/* Category Distribution */}
        <div className="chart-card">
          <h2 className="chart-title">🏷️ Category-wise Borrowing</h2>
          <div className="hbar-list">
            {catStats.map((c) => (
              <div key={c.category} className="hbar-row">
                <div
                  className="cat-dot"
                  style={{ background: colorFor(c.category) }}
                />
                <div className="hbar-info">
                  <div className="hbar-label">{c.category}</div>
                  <div className="hbar-meta">{c.unique_books} unique books</div>
                  <div className="hbar-track">
                    <div
                      className="hbar-fill"
                      style={{
                        width: `${(c.borrow_count / maxCat) * 100}%`,
                        background: colorFor(c.category),
                      }}
                    />
                  </div>
                </div>
                <div className="hbar-count">{c.borrow_count}</div>
              </div>
            ))}
            {catStats.length === 0 && <p className="no-data">No data yet.</p>}
          </div>

          {/* Mini legend (donut-style colour swatches) */}
          <div className="cat-legend">
            {catStats.map((c) => (
              <span key={c.category} className="cat-swatch">
                <span style={{ background: colorFor(c.category) }} />
                {c.category}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ── Monthly Borrowing Trends (bar chart) ─────────────────── */}
      <div className="chart-card chart-full">
        <h2 className="chart-title">📅 Monthly Borrowing Trends (last 12 months)</h2>
        {trends.length > 0 ? (
          <div className="vbar-chart">
            {trends.map((t) => (
              <div key={t.month} className="vbar-group">
                <div className="vbar-bars">
                  {/* Borrow bar */}
                  <div className="vbar-wrapper" title={`Borrows: ${t.borrow_count}`}>
                    <div
                      className="vbar borrow-bar"
                      style={{ height: `${(t.borrow_count / maxTrend) * 140}px` }}
                    />
                  </div>
                  {/* Return bar */}
                  <div className="vbar-wrapper" title={`Returns: ${t.return_count}`}>
                    <div
                      className="vbar return-bar"
                      style={{ height: `${(t.return_count / maxTrend) * 140}px` }}
                    />
                  </div>
                </div>
                <div className="vbar-counts">
                  <span className="bc">{t.borrow_count}</span>
                  <span className="rc">{t.return_count}</span>
                </div>
                <div className="vbar-label">{t.month.slice(5)}/{t.month.slice(0, 4)}</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-data">No trend data yet.</p>
        )}
        <div className="vbar-legend">
          <span><span className="legend-dot" style={{ background: "#6366f1" }} />Borrows</span>
          <span><span className="legend-dot" style={{ background: "#10b981" }} />Returns</span>
        </div>
      </div>

      {/* ── Overdue Transactions Table ────────────────────────────── */}
      <div className="chart-card chart-full">
        <h2 className="chart-title">
          ⚠️ Overdue Transactions
          <span className="overdue-badge">{overdue.length}</span>
        </h2>
        {overdue.length > 0 ? (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#TXN</th>
                  <th>Book Title</th>
                  <th>Borrower</th>
                  <th>Borrow Date</th>
                  <th>Days Overdue</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {overdue.map((o) => (
                  <tr key={o.transaction_id} className="overdue-row">
                    <td>{o.transaction_id}</td>
                    <td>{o.book_title}</td>
                    <td>{o.borrower_name}</td>
                    <td>{fmt(o.borrow_date)}</td>
                    <td>
                      <span
                        className="days-badge"
                        style={{
                          background: o.days_overdue > 30 ? "#fca5a5" : "#fed7aa",
                          color: o.days_overdue > 30 ? "#991b1b" : "#92400e",
                        }}
                      >
                        {o.days_overdue} days
                      </span>
                    </td>
                    <td><span className="badge badge-overdue">Overdue</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-overdue">
            <span className="no-overdue-icon">✅</span>
            <p>No overdue transactions — great job!</p>
          </div>
        )}
      </div>

    </div>
  );
}
