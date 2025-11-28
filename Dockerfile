FROM python:3.12-slim

# Create app user and working directory
ENV PYTHONDONTWRITEBYTECODE=1 \
		PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt

# Install python deps (no build deps required for these packages)
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Create a non-root user and give ownership of the app dir
RUN useradd --create-home appuser \
		&& chown -R appuser:appuser /app

USER appuser

# Expose application port
EXPOSE 8000

# Healthcheck uses Python's stdlib to query the running app
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
	CMD python -c "import urllib.request, sys; \
resp = urllib.request.urlopen('http://127.0.0.1:8000/health'); \
sys.exit(0 if resp.getcode()==200 else 1)" || exit 1

# Start the app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
