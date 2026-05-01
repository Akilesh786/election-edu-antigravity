# ─────────────────────────────────────────────────────────────────────────────
# Dockerfile — Election Education Hub (Streamlit on Cloud Run)
# ─────────────────────────────────────────────────────────────────────────────

# Use the official slim Python 3.11 image for a small, secure build
FROM python:3.11-slim

# ── System-level setup ────────────────────────────────────────────────────────
# Set environment variables so Python writes directly to stdout/stderr
# (important for Cloud Run log capture) and doesn't create .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user for security (Cloud Run best practice)
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies ───────────────────────────────────────────────
# Copy requirements first so Docker can cache this layer independently
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application source ───────────────────────────────────────────────────
COPY election_guide.py  .
COPY streamlit_app.py   .

# Switch to non-root user
USER appuser

# ── Streamlit configuration ───────────────────────────────────────────────────
# Cloud Run injects PORT (default 8080). Streamlit must listen on that port.
# --server.address 0.0.0.0  → accept connections from any interface
# --server.headless true     → disable the browser-launch prompt
# --server.enableCORS false  → Cloud Run handles TLS termination
# --server.enableXsrfProtection false → avoids redirect loops behind GCP LB
EXPOSE 8080

CMD ["python", "-m", "streamlit", "run", "streamlit_app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]
