#!/bin/bash
# Description: Executes a high-speed SYN scan against the SSH target to generate incomplete handshakes.

TARGET_IP="10.10.10.10"

echo "[*] Initiating structured cyberattack simulation..."
echo "[*] Target: $TARGET_IP"
echo "[*] Attack Type: Aggressive Nmap SYN Scan (Half-open connections)"

# -sS: TCP SYN scan (stealth)
# -p-: Scan all 65535 ports
# -T4: Aggressive timing template for faster execution
# --min-rate 5000: Force a high packet rate to create a distinct anomaly spike
nmap -sS -p- -T4 --min-rate 5000 $TARGET_IP

echo "[*] Attack simulation complete."