import re

# Defined Keyword Lists
# Critical = High Urgency (Immediate Action Required)
CRITICAL_KEYWORDS = [
    r"\bsystem\s+(?:is\s+)?down\b",
    r"\bcrash\b",
    r"\bsecurity breach\b",
    r"\bunable to login\b",
    r"\bdata loss\b",
    r"\bhacked\b",
    r"\bimmediate assistance\b",
    r"\bblocked\b",
    r"\bcritical failure\b",
    r"\bpayment failed\b",
    r"\bserver\s+(?:is\s+)?down\b"
]

# Medium = Medium Urgency (Needs Attention soon)
MEDIUM_KEYWORDS = [
    r"\bhelp\b",
    r"\bissue\b",
    r"\berror\b",
    r"\bbug\b",
    r"\bfail\b",
    r"\bnot working\b",
    r"\brequest\b",
    r"\bstatus\b",
    r"\bupdate\b",
    r"\bcheck\b",
    r"\bunable to\b"
]

# Additional weighted signals to avoid static fallback behavior when ML is unavailable.
HIGH_SIGNAL_TERMS = [
    "urgent",
    "asap",
    "immediately",
    "critical",
    "outage",
    "downtime",
    "production",
    "blocked",
    "cannot",
    "unable",
    "failed",
    "failure",
    "escalate",
    "breach",
    "deadline",
]

MEDIUM_SIGNAL_TERMS = [
    "help",
    "issue",
    "error",
    "problem",
    "request",
    "status",
    "update",
    "delay",
    "pending",
    "stuck",
    "investigate",
    "support",
    "follow up",
]

LOW_SIGNAL_TERMS = [
    "newsletter",
    "promotion",
    "offer",
    "discount",
    "thank you",
    "thanks",
    "fyi",
    "subscription",
    "announcement",
    "reminder",
]

TIME_PRESSURE_PATTERNS = [
    r"\bwithin\s+\d+\s*(?:min|mins|minute|minutes|hour|hours|hr|hrs|day|days)\b",
    r"\bby\s+eod\b",
    r"\bbefore\s+eod\b",
    r"\btoday\b",
    r"\bright\s+now\b",
    r"\basap\b",
    r"\bimmediately\b",
]

def detect_urgency_rules(text):
    """
    Analyzes text for urgency keywords.
    
    Returns:
        dict: {
            "label": "High" | "Medium" | "Low",
            "score": 0, 1, or 2 (mapped to Low, Medium, High),
            "reason": matched_keyword (str) or None,
            "rule_confidence": 1.0 (if match found) else 0.0
        }
    """
    text_lower = text.lower()
    
    # 1. Check for Critical Keywords (High Urgency)
    for pattern in CRITICAL_KEYWORDS:
        if re.search(pattern, text_lower):
            return {
                "label": "High",
                "score": 2,
                "reason": pattern.replace(r"\b", "").replace("\\", ""),
                "rule_confidence": 1.0
            }
            
    # 2. Check for Medium Keywords
    for pattern in MEDIUM_KEYWORDS:
        if re.search(pattern, text_lower):
            return {
                "label": "Medium",
                "score": 1,
                "reason": pattern.replace(r"\b", "").replace("\\", ""),
                "rule_confidence": 0.8  # Medium rules are less absolute than critical ones
            }
            
    # 3. Default to Low if no keywords found
    return {
        "label": "Low",
        "score": 0,
        "reason": None,
        "rule_confidence": 0.0
    }

def score_urgency_signals(text):
    """
    Dynamic urgency scoring for fallback and low-confidence scenarios.

    Returns:
        dict: {
            "label": "High" | "Medium" | "Low",
            "score": float 0..1,
            "confidence": float 0..1,
            "reasons": list[str],
            "highlights": list[{"word": str, "score": float}],
            "features": dict
        }
    """
    text = text or ""
    text_lower = text.lower()

    def _find_terms(terms):
        matches = []
        for term in terms:
            pattern = rf"\b{re.escape(term)}\b"
            if re.search(pattern, text_lower):
                matches.append(term)
        return matches

    high_matches = _find_terms(HIGH_SIGNAL_TERMS)
    medium_matches = _find_terms(MEDIUM_SIGNAL_TERMS)
    low_matches = _find_terms(LOW_SIGNAL_TERMS)

    time_matches = []
    for pattern in TIME_PRESSURE_PATTERNS:
        if re.search(pattern, text_lower):
            time_matches.append(pattern.replace(r"\b", "").replace("\\", ""))

    uppercase_tokens = re.findall(r"\b[A-Z]{3,}\b", text)
    exclamation_count = text.count("!")
    question_count = text.count("?")

    # Weighted score tuned to produce dynamic low/medium/high separation.
    score = 0.0
    score += min(len(high_matches), 5) * 0.18
    score += min(len(medium_matches), 5) * 0.09
    score += min(len(time_matches), 3) * 0.13
    score += min(exclamation_count, 4) * 0.04
    score += min(len(uppercase_tokens), 4) * 0.05
    score -= min(len(low_matches), 4) * 0.10
    score -= min(question_count, 3) * 0.01
    score = max(0.0, min(score, 1.0))

    if score >= 0.68:
        label = "High"
    elif score >= 0.30:
        label = "Medium"
    else:
        label = "Low"

    confidence = max(0.45, min(0.96, 0.50 + (score * 0.46)))

    reasons = []
    reasons.extend([f"high:{term}" for term in high_matches[:5]])
    reasons.extend([f"medium:{term}" for term in medium_matches[:5]])
    reasons.extend([f"time:{term}" for term in time_matches[:3]])
    reasons.extend([f"low:{term}" for term in low_matches[:3]])

    highlights = []
    for term in high_matches[:6]:
        highlights.append({"word": term, "score": 0.28})
    for term in medium_matches[:4]:
        highlights.append({"word": term, "score": 0.18})
    if exclamation_count > 0:
        highlights.append({"word": "!", "score": min(0.2, 0.05 * exclamation_count)})
    for token in uppercase_tokens[:3]:
        highlights.append({"word": token, "score": 0.14})

    # Merge duplicate highlight words by max score.
    merged = {}
    for item in highlights:
        token = item["word"]
        merged[token] = max(merged.get(token, 0.0), float(item["score"]))
    merged_highlights = [{"word": k, "score": v} for k, v in merged.items()]
    merged_highlights.sort(key=lambda x: x["score"], reverse=True)

    return {
        "label": label,
        "score": round(score, 4),
        "confidence": round(confidence, 4),
        "reasons": reasons,
        "highlights": merged_highlights[:10],
        "features": {
            "high_match_count": len(high_matches),
            "medium_match_count": len(medium_matches),
            "low_match_count": len(low_matches),
            "time_pressure_count": len(time_matches),
            "exclamation_count": exclamation_count,
            "uppercase_token_count": len(uppercase_tokens),
        }
    }

# Quick Test
if __name__ == "__main__":
    test_cases = [
        "The system is down and I cannot access the portal.",
        "I need help with my refund status.",
        "Just wanted to say thanks for the great service.",
        "There is a critical failure in the payments module."
    ]
    
    print("--- Rule Based Verification ---")
    for t in test_cases:
        print(f"Text: '{t}'\nResult: {detect_urgency_rules(t)}\n")
        print(f"Dynamic: {score_urgency_signals(t)}\n")
