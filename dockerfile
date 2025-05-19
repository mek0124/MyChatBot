# Stage 1: Builder
FROM python:3.10-slim AS builder

# Set project metadata
ARG PROJECT_NAME=mychatbot
LABEL project=$PROJECT_NAME \
      maintainer="your@email.com" \
      version="1.0.0"

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

# Copy project metadata
ARG PROJECT_NAME=mychatbot
LABEL project=$PROJECT_NAME \
      maintainer="your@email.com" \
      version="1.0.0"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxkbcommon0 \
    libegl1 \
    libxcb1 \
    libx11-xcb1 \
    libx11-6 \
    libfontconfig1 \
    libdbus-1-3 \
    libxcb-cursor0 \
    libglx0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create directory for the database
RUN mkdir -p /app/backend

# Environment variables
ENV PYTHONPATH=/app
ENV QT_DEBUG_PLUGINS=1
ENV QT_X11_NO_MITSHM=1

# Run the application
CMD ["python", "main.py"]