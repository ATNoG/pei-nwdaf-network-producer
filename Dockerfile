FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    tar \
    build-essential \
    python3-dev \
    librdkafka-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# Copy dependency files
COPY requirements.txt ./
COPY main.py .
COPY data.tar.xz ./
COPY src/ ./src/

RUN tar -xJf data.tar.xz

# Install dependencies using uv
RUN uv pip install --system -r requirements.txt
CMD ["uv", "run", "main.py", "-f", "merged/latency_data.csv", "-i", "0.5", "-a", "http://data-ingestion:7000/receive"]
