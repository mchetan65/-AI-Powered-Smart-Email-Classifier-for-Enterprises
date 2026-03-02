function Badge({ label, tone }) {
  return <span className={`badge badge-${tone}`}>{label}</span>;
}

function formatConfidence(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

export default function DecisionPanel({ run, loading, error }) {
  if (loading) {
    return (
      <section className="panel panel-decision reveal-delay-2">
        <div className="loading-wrap">
          <div className="scan-line" />
          <p>Running model and rule checks...</p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="panel panel-decision reveal-delay-2">
        <div className="empty-wrap">
          <h3>Connection Issue</h3>
          <p>{error}</p>
          <p>Confirm backend server at http://127.0.0.1:7860.</p>
        </div>
      </section>
    );
  }

  if (!run) {
    return (
      <section className="panel panel-decision reveal-delay-2">
        <div className="empty-wrap">
          <h3>No Decision Yet</h3>
          <p>Submit one signal from the left panel to populate this decision board.</p>
        </div>
      </section>
    );
  }

  const urgencyTone = run.urgency?.toLowerCase() === "high" ? "high" : run.urgency?.toLowerCase() === "medium" ? "medium" : "low";
  const confidencePct = Math.max(0, Math.min(100, Math.round((run.confidence || 0) * 100)));
  const highlights = Array.isArray(run.xai_highlights) ? run.xai_highlights.slice(0, 8) : [];

  return (
    <section className="panel panel-decision reveal-delay-2">
      <header className="panel-head">
        <p className="panel-kicker">Decision</p>
        <h2>Signal Verdict</h2>
        <p className="panel-sub">Combined rule + ML evaluation with confidence trace.</p>
      </header>

      <div className="verdict-grid">
        <div className="verdict-card">
          <span className="label">Urgency</span>
          <Badge label={run.urgency || "Unknown"} tone={urgencyTone} />
        </div>
        <div className="verdict-card">
          <span className="label">Category</span>
          <strong>{run.category || "Unknown"}</strong>
        </div>
        <div className="verdict-card">
          <span className="label">Confidence</span>
          <strong>{formatConfidence(run.confidence)}</strong>
        </div>
      </div>

      <div className="confidence-track" role="presentation">
        <div className="confidence-fill" style={{ width: `${confidencePct}%` }} />
      </div>

      <div className="source-box">
        <span className="label">Source Path</span>
        <p>{run.source || "Unknown"}</p>
      </div>

      <div className="highlight-box">
        <div className="highlight-head">
          <span className="label">Top Influence Tokens</span>
          <span>{highlights.length}</span>
        </div>

        {highlights.length === 0 ? (
          <p className="dim-copy">No token level explanation was returned for this run.</p>
        ) : (
          <ul className="token-list">
            {highlights.map((item, index) => {
              const score = Number(item.score || 0);
              const width = Math.max(6, Math.min(100, Math.round(score * 180)));
              return (
                <li key={`${item.word}-${index}`}>
                  <span>{item.word}</span>
                  <div className="token-meter">
                    <div style={{ width: `${width}%` }} />
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </section>
  );
}
