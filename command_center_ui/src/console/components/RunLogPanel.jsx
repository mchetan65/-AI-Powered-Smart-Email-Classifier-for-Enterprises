function shortText(value, limit = 62) {
  const text = value || "";
  return text.length > limit ? `${text.slice(0, limit)}...` : text;
}

export default function RunLogPanel({ runs, selectedId, onSelect }) {
  const highUrgency = runs.filter((item) => (item.urgency || "").toLowerCase() === "high").length;
  const avgConfidence = runs.length
    ? Math.round((runs.reduce((sum, item) => sum + Number(item.confidence || 0), 0) / runs.length) * 100)
    : 0;

  return (
    <section className="panel panel-log reveal-delay-3">
      <header className="panel-head">
        <p className="panel-kicker">Ops Feed</p>
        <h2>Run Ledger</h2>
        <p className="panel-sub">Recent decisions and throughput snapshots.</p>
      </header>

      <div className="metric-row">
        <article>
          <span>Total Runs</span>
          <strong>{runs.length}</strong>
        </article>
        <article>
          <span>High Urgency</span>
          <strong>{highUrgency}</strong>
        </article>
        <article>
          <span>Avg Confidence</span>
          <strong>{avgConfidence}%</strong>
        </article>
      </div>

      <ul className="run-list">
        {runs.length === 0 ? (
          <li className="run-empty">No runs captured yet.</li>
        ) : (
          runs.map((run) => (
            <li key={run.id}>
              <button
                type="button"
                className={run.id === selectedId ? "run-item is-selected" : "run-item"}
                onClick={() => onSelect(run.id)}
              >
                <div className="run-top">
                  <span>{run.timestamp}</span>
                  <span className={`dot dot-${(run.urgency || "low").toLowerCase()}`} />
                </div>
                <p>{shortText(run.subject || run.content)}</p>
              </button>
            </li>
          ))
        )}
      </ul>
    </section>
  );
}
