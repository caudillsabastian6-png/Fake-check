#!/bin/bash
# Tailscale + SSH setup — run once at first boot, owner at the machine.
# No token, key, or login URL is stored here. Tailscale will print a login
# URL; the owner opens it and approves it. That approval is the secret step.
set -e
echo "Installing Tailscale (Debian repo, official installer)..."
curl -fsSL https://tailscale.com/install.sh | sh
echo "Enabling SSH server (local + Tailscale SSH)..."
sudo systemctl enable --now ssh || true
echo "Now run, as owner:"
echo "  sudo tailscale up --ssh"
echo "Then approve the login URL it prints. Do NOT paste that URL or any"
echo "auth key into this pack or into chat."
echo "After login, verify from another machine:"
echo "  tailscale status"
echo "  ssh <user>@<tailscale-ip> 'echo SSH_OK'"
echo "Firewall note: keep SSH reachable only via Tailscale. Do not open"
echo "port 22 to the public internet on the home router for this box."
