# Dockerfile for Backend-Only Deployment (Hugging Face Spaces)
FROM python:3.9-slim
WORKDIR /app
# 1. Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 2. Copy Code & Models
# Note: We exclude the 'command_center_ui' folder to avoid build errors
COPY orchestration_api/ ./orchestration_api/
COPY urgency_transformer_assets/ ./urgency_transformer_assets/
COPY category_transformer_assets/ ./category_transformer_assets/
COPY urgency_hybrid_engine.py .
COPY urgency_rules_engine.py .
# 3. Expose Port
EXPOSE 7860
# 4. Run FastAPI
CMD ["uvicorn", "orchestration_api.api_server:app", "--host", "0.0.0.0", "--port", "7860"]
