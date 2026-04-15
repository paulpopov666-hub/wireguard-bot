FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install amneziawg-tools
RUN curl -fsSL https://pkg.amnezia.org/public/amnezia-wg/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/amnezia-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/amnezia-archive-keyring.gpg] https://pkg.amnezia.org/public/amnezia-wg/ubuntu/ jammy main" > /etc/apt/sources.list.d/amnezia.list \
    && apt-get update \
    && apt-get install -y amneziawg-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 51820/udp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Run the bot
CMD ["poetry", "run", "python", "app.py"]
