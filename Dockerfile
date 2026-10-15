FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

ENV HOST=0.0.0.0
ENV PORT=8000
ENV FALKORDB_HOST=falkordb
ENV FALKORDB_PORT=6379

CMD ["python", "run.py"]
