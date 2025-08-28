FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
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
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Buildozer and dependencies
RUN pip3 install --upgrade pip && \
    pip3 install buildozer cython==0.29.33 virtualenv

# Set up Android SDK
ENV ANDROID_HOME /opt/android-sdk
ENV PATH "${PATH}:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools"

# Create Android SDK directory and install command line tools
RUN mkdir -p ${ANDROID_HOME}/cmdline-tools/latest && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip -O /tmp/cmdline-tools.zip && \
    unzip -q /tmp/cmdline-tools.zip -d /tmp/ && \
    mv /tmp/cmdline-tools/* ${ANDROID_HOME}/cmdline-tools/latest/ && \
    rm -f /tmp/cmdline-tools.zip && \
    yes | ${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_HOME} --licenses && \
    ${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_HOME} "platform-tools" "platforms;android-33" "build-tools;33.0.0"

# Set up working directory
WORKDIR /app

# Copy application files
COPY . .

# Set up Buildozer
RUN mkdir -p /root/.buildozer
RUN echo "[buildozer]" > /root/.buildozer/config.ini && \
    echo "log_level = 2" >> /root/.buildozer/config.ini && \
    echo "warn_on_root = 1" >> /root/.buildozer/config.ini

# Build command
CMD ["buildozer", "-v", "android", "debug"]
