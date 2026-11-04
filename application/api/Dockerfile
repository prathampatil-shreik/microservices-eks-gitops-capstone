# ── Stage 1: dependency builder ───────────────────────────────────────────────
# We install dependencies in a separate stage so the final image only contains
# what is needed to run the application (not build tools).
FROM python:3.12-slim AS builder

WORKDIR /build

# Install dependencies first — Docker caches this layer until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.12-slim

# Create a non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source code
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini .

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check — Docker will mark the container unhealthy if this fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')"

# Start the API server
# --host 0.0.0.0 makes it reachable from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
