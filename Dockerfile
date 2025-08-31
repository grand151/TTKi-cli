FROM ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    x11vnc \
    xvfb \
    python3 \
    python3-pip \
    python3-venv \
    git \
    gcc \
    g++ \
    make \
    cmake \
    nodejs \
    npm \
    docker.io \
    sqlite3 \
    jq \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install numpy pandas matplotlib seaborn scikit-learn flask fastapi requests jupyter

# Create a non-root user
RUN useradd -m -s /bin/bash ubuntu
RUN echo "ubuntu:ubuntu" | chpasswd
RUN adduser ubuntu sudo

# Set up the development environment
USER ubuntu
WORKDIR /home/ubuntu
RUN mkdir dev_environment

# Expose the VNC port
EXPOSE 5900

# Start Xvfb and x11vnc
CMD ["sh", "-c", "Xvfb :1 -screen 0 1024x768x16 & x11vnc -display :1 -forever -nopw -create"]
