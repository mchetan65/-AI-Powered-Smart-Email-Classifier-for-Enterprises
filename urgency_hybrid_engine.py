import torch
import numpy as np
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from urgency_rules_engine import detect_urgency_rules, score_urgency_signals

# Configuration
MODEL_PATH = "./urgency_transformer_assets"
CONFIDENCE_THRESHOLD = 0.85

class HybridUrgencyClassifier:
    def __init__(self):
        print("Loading Hybrid Urgency Classifier...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Load ML components
        try:
            self.tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
            self.model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
            self.model.to(self.device)
            self.model.eval()
            print("ML Model loaded successfully.")
        except Exception as e:
            print(f"Error loading ML model: {e}")
            print("Ensure train_urgency_model.py has finished successfully.")
            self.model = None

        self.label_map = {0: "Low", 1: "Medium", 2: "High"}

    def predict(self, text):
        """
        Hybrid Prediction Logic:
        1. Critical Rule Override (High Urgency)
        2. High Confidence ML (>0.85)
        3. Fallback: Medium Rule or ML Best Guess
        """
        
        # Common Explanation Logic
        # We want XAI for all decisions to support the UI Heatmap
        # Using the label from the specific path as the target
        
        # Step 1: Rule-Based Check
        rule_result = detect_urgency_rules(text)
        
        # POLICY: Critical Rule Override
        if rule_result['label'] == "High":
             dynamic_signal = score_urgency_signals(text)
             highlights = self._explain_prediction(text, "High")
             if not highlights:
                 highlights = dynamic_signal.get("highlights", [])
             return {
                "final_label": "High",
                "source": "Rule (Critical Override)",
                "confidence": 1.0,
                "details": {
                    "rule_result": rule_result,
                    "dynamic_signal": dynamic_signal
                },
                "highlights": highlights
            }

        # Step 2: ML Prediction
        ml_result = self._get_ml_prediction(text)
        dynamic_result = self._dynamic_fallback_prediction(text, rule_result)
        highlights = self._explain_prediction(text, ml_result['label_name'])
        if not highlights:
            highlights = dynamic_result.get("highlights", [])

        # If model is unavailable, use dynamic rules instead of static "Low".
        if not self.model:
            return dynamic_result
        
        # POLICY: High Confidence ML
        if ml_result['confidence'] >= CONFIDENCE_THRESHOLD:
            return {
                "final_label": ml_result['label_name'],
                "source": "ML (High Confidence)",
                "confidence": ml_result['confidence'],
                "details": ml_result,
                "highlights": highlights
            }
            
        # Step 3: Low Confidence ML - Fallback Logic
        if ml_result['confidence'] < 0.70:
            return {
                "final_label": dynamic_result["final_label"],
                "source": "Dynamic Rules (Low ML Confidence)",
                "confidence": dynamic_result["confidence"],
                "details": {
                    "ml_result": ml_result,
                    "dynamic_result": dynamic_result["details"],
                    "rule_result": rule_result,
                },
                "highlights": dynamic_result["highlights"] or highlights,
            }
            
        # Default to ML's best guess
        return {
            "final_label": ml_result['label_name'],
            "source": "ML (Low Confidence)",
            "confidence": ml_result['confidence'],
            "details": ml_result,
            "highlights": highlights
        }

    def _get_ml_prediction(self, text):
        if not self.model:
            return {"label_idx": 0, "label_name": "Low", "confidence": 0.0}
            
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        conf, pred_idx = torch.max(probabilities, dim=1)
        return {
            "label_idx": pred_idx.item(),
            "label_name": self.label_map[pred_idx.item()],
            "confidence": conf.item()
        }

    def _dynamic_fallback_prediction(self, text, rule_result):
        signal = score_urgency_signals(text)
        final_label = signal["label"]

        # Keep medium safeguards from explicit rules.
        features = signal.get("features", {})
        low_signal_count = int(features.get("low_match_count", 0))
        dynamic_score = float(signal.get("score", 0.0))
        if (
            rule_result.get("label") == "Medium"
            and final_label == "Low"
            and low_signal_count == 0
            and dynamic_score >= 0.18
        ):
            final_label = "Medium"
            signal["reasons"].append("rule:medium_override")
            signal["confidence"] = max(signal["confidence"], 0.72)

        return {
            "final_label": final_label,
            "source": "Dynamic Rules (No ML Model)",
            "confidence": signal["confidence"],
            "details": {
                "rule_result": rule_result,
                "dynamic_signal": signal,
            },
            "highlights": signal.get("highlights", []),
        }

    def _explain_prediction(self, text, target_label):
        """
        Simple Perturbation-based Feature Importance (XAI).
        Masks each word and checks the drop in confidence for the target label.
        Returns: List[Dict] -> [{'word': 'broken', 'score': 0.45}, ...]
        """
        if not self.model:
            return []

        words = text.split()
        if len(words) < 2:
            return []

        # Base prediction confidence for the target label
        base_pred = self._get_ml_prediction(text)
        base_conf = base_pred['confidence']
        importance_scores = []

        for i in range(len(words)):
            # Create masked text
            masked_words = words[:i] + ["[MASK]"] + words[i+1:]
            masked_text = " ".join(masked_words)
            
            # Predict on masked text
            masked_pred = self._get_ml_prediction(masked_text)
            
            # If label changed, that's a HUGE signal. 
            if masked_pred['label_name'] != target_label:
                drop = base_conf  # Max drop if label flips
            else:
                drop = max(0, base_conf - masked_pred['confidence'])
            
            # Only keep positive contributions
            # Lowered threshold to ensure we catch even small signals
            if drop > 0.0001:
                importance_scores.append({"word": words[i], "score": float(drop)})

        # Sort by drop (descending)
        importance_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top words with scores
        return importance_scores[:10]

# Interactive Test
if __name__ == "__main__":
    classifier = HybridUrgencyClassifier()
    
    test_messages = [
        "System is down! Critical failure.",
        "Can you please help me with a small issue?",
        "I need a refund for my order #1234.",
        "Subscribe to our newsletter for free watches."
    ]
    
    print("\n--- Hybrid Inference Test ---\n")
    for msg in test_messages:
        print(f"Input: {msg}")
        result = classifier.predict(msg)
        print(f"Prediction: {result['final_label']} (Source: {result['source']})")
        print("-" * 30)
