import { useMemo, useState } from "react";
import ComposePanel from "./components/ComposePanel.jsx";
import DecisionPanel from "./components/DecisionPanel.jsx";
import RunLogPanel from "./components/RunLogPanel.jsx";
import { requestTriage } from "./api/triageClient.js";

const STORAGE_KEY = "signal_deck_runs_v2";

function readStoredRuns() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export default function SignalDeck() {
  const [draft, setDraft] = useState({ subject: "", sender: "", content: "" });
  const [runs, setRuns] = useState(readStoredRuns);
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const activeRun = useMemo(() => {
    if (!runs.length) {
      return null;
    }
    if (!selectedId) {
      return runs[0];
    }
    return runs.find((item) => item.id === selectedId) || runs[0];
  }, [runs, selectedId]);

  const persistRuns = (nextRuns) => {
    setRuns(nextRuns);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextRuns));
  };

  const handleAnalyze = async () => {
    if (!draft.content.trim()) {
      setError("Email content is required.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const result = await requestTriage({
        subject: draft.subject,
        sender: draft.sender,
        content: draft.content,
      });

      const run = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        ...draft,
        ...result,
      };

      const nextRuns = [run, ...runs].slice(0, 40);
      persistRuns(nextRuns);
      setSelectedId(run.id);
    } catch (requestError) {
      setError("Triage request failed. Confirm backend service is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setDraft({ subject: "", sender: "", content: "" });
    setError("");
  };

  const highLoad = useMemo(
    () => runs.filter((entry) => (entry.urgency || "").toLowerCase() === "high").length,
    [runs]
  );

  return (
    <div className="deck-shell">
      <div className="orb orb-a" />
      <div className="orb orb-b" />

      <header className="topbar reveal-delay-1">
        <div>
          <p className="eyebrow">Signal Deck</p>
          <h1>Enterprise Triage Console</h1>
          <p className="subhead">A redesigned command center for email urgency and category intelligence.</p>
        </div>
        <aside className="status-stack">
          <span>
            High Urgency Queue <strong>{highLoad}</strong>
          </span>
          <span>
            Saved Decisions <strong>{runs.length}</strong>
          </span>
        </aside>
      </header>

      <main className="deck-grid">
        <ComposePanel
          draft={draft}
          onDraftChange={setDraft}
          onAnalyze={handleAnalyze}
          onClear={handleClear}
          loading={loading}
        />
        <DecisionPanel run={activeRun} loading={loading} error={error} />
        <RunLogPanel runs={runs} selectedId={activeRun?.id || null} onSelect={setSelectedId} />
      </main>
    </div>
  );
}
