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
COPY pyproject.toml ./
COPY uv.lock ./
COPY main_csv.py .
COPY data.tar.xz ./
COPY src/ ./src/

RUN tar -xJf data.tar.xz

# Install dependencies using uv
RUN uv sync --frozen --no-dev
CMD ["uv", "run", "main_csv.py", "-f", "merged/latency_data.csv", "-i", "0.5", "-s", "5", "-y", "network_trafic"]
