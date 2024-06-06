#!/bin/bash

# Get the Tailscale API key from the command line arguments
AUTH_KEY=$1

# Check if the API key is provided
if [ -z "$AUTH_KEY" ]; then
  echo "Error: No Tailscale API key provided."
  exit 1
fi

# Install Tailscale
echo "Installing Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh

# Start Tailscale in userspace networking mode
echo "Starting Tailscale in userspace networking mode..."
tailscaled --tun=userspace-networking --socks5-server=localhost:1055 --outbound-http-proxy-listen=localhost:1055 &

# Wait for a few seconds to ensure tailscaled starts properly
sleep 5

# Connect Tailscale using the provided API key
echo "Connecting Tailscale..."
tailscale up --authkey=$AUTH_KEY
tailscale up --ssh

echo "Tailscale setup completed successfully."
