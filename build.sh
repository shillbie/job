#!/bin/bash

# Update package lists
sudo apt-get update

# Install required dependencies
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-setuptools \
    build-essential \
    git \
    openjdk-11-jdk \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    wget \
    liblzma-dev \
    python3-openssl \
    unzip

# Install Buildozer
pip3 install --upgrade pip
pip3 install buildozer
pip3 install cython==0.29.33

# Create buildozer config if it doesn't exist
if [ ! -f ~/.buildozer/config.ini ]; then
    mkdir -p ~/.buildozer
    echo "[buildozer]" > ~/.buildozer/config.ini
    echo "log_level = 2" >> ~/.buildozer/config.ini
    echo "warn_on_root = 1" >> ~/.buildozer/config.ini
fi

# Run buildozer
buildozer -v android debug

# Copy APK to artifacts directory
mkdir -p ~/artifacts
cp bin/*.apk* ~/artifacts/ 2>/dev/null || true
