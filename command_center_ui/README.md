# Signal Deck UI

This folder contains the redesigned frontend for the email classifier project.

## Stack

- React 19
- Vite 7
- Axios
- Custom CSS (no component framework)

## Run

```bash
npm install
npm run dev
```

The UI expects the backend at `http://127.0.0.1:7860` unless `VITE_API_URL` is set.

## New Source Layout

- `src/bootstrap.jsx`: App entry point
- `src/console/SignalDeck.jsx`: Top-level screen and state orchestration
- `src/console/components/`: Compose, decision, and run-log panels
- `src/console/api/triageClient.js`: Backend request client
- `src/console/theme.css`: Visual system and responsive styling
