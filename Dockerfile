# Base image with Python
FROM python:3.11-slim

# Install Chrome dependencies
RUN apt-get update && apt-get install -y wget gnupg unzip fonts-liberation \
    libnss3 libxss1 libasound2 libatk-bridge2.0-0 libgtk-3-0 \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 xdg-utils

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && apt-get install -y google-chrome-stable

# Set working dir
WORKDIR /app

# Copy your code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for g4f
ENV BROWSER_EXECUTABLE_PATH="/usr/bin/google-chrome"

# Run the API
CMD ["python", "-m", "g4f.api"]
