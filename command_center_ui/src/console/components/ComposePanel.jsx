import { useMemo, useState } from "react";

const SAMPLE_SIGNAL = {
  sender: "ops@northstar-logistics.com",
  subject: "Warehouse scanners down in Region 4",
  content:
    "Team, all hand scanners in Region 4 stopped syncing in the last 20 minutes. Outbound packing is halted and orders are now queueing. Need immediate support to restore flow.",
};

export default function ComposePanel({ draft, onDraftChange, onAnalyze, onClear, loading }) {
  const contentSize = useMemo(() => draft.content.trim().length, [draft.content]);

  const updateField = (field, value) => {
    onDraftChange((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <section className="panel panel-compose reveal-delay-1">
      <header className="panel-head">
        <p className="panel-kicker">Intake</p>
        <h2>Compose Signal</h2>
        <p className="panel-sub">Drop an incoming email and push it through the triage engine.</p>
      </header>

      <div className="field-stack">
        <label className="field-label" htmlFor="sender">Sender</label>
        <input
          id="sender"
          className="field-input"
          type="text"
          placeholder="name@company.com"
          value={draft.sender}
          onChange={(event) => updateField("sender", event.target.value)}
        />

        <label className="field-label" htmlFor="subject">Subject</label>
        <input
          id="subject"
          className="field-input"
          type="text"
          placeholder="Short context line"
          value={draft.subject}
          onChange={(event) => updateField("subject", event.target.value)}
        />

        <div className="content-row">
          <label className="field-label" htmlFor="content">Email Content</label>
          <span className={`char-meter ${contentSize > 400 ? "char-meter-hot" : ""}`}>{contentSize} chars</span>
        </div>
        <textarea
          id="content"
          className="field-textarea"
          placeholder="Paste complete email body"
          value={draft.content}
          onChange={(event) => updateField("content", event.target.value)}
        />
      </div>

      <footer className="compose-actions">
        <button
          type="button"
          className="ghost-btn"
          onClick={() => onDraftChange(SAMPLE_SIGNAL)}
          disabled={loading}
        >
          Load Example
        </button>
        <button type="button" className="ghost-btn" onClick={onClear} disabled={loading}>
          Reset
        </button>
        <button
          type="button"
          className="prime-btn"
          onClick={onAnalyze}
          disabled={loading || !draft.content.trim()}
        >
          {loading ? "Scanning..." : "Run Triage"}
        </button>
      </footer>
    </section>
  );
}
