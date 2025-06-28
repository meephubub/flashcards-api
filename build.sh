#!/bin/bash

# Update and install Chrome dependencies
apt-get update && apt-get install -y wget gnupg unzip fonts-liberation \
    libnss3 libxss1 libasound2 libatk-bridge2.0-0 libgtk-3-0 \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 xdg-utils

# Add Google Chrome repo
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'

# Install Chrome
apt-get update && apt-get install -y google-chrome-stable

# Install Python dependencies
pip install -r requirements.txt
