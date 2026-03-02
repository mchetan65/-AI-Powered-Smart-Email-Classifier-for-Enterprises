import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import SignalDeck from "./console/SignalDeck.jsx";
import "./console/theme.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <SignalDeck />
  </StrictMode>
);
