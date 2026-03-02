import axios from "axios";

const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

export async function requestTriage(payload) {
  const url = `${API_BASE}/api/classify`;
  const response = await axios.post(url, payload, {
    timeout: 20000,
    headers: { "Content-Type": "application/json" },
  });
  return response.data;
}
