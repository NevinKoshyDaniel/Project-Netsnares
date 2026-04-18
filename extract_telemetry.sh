#!/bin/bash
# Description: Parses raw PCAP binary into a lightweight, Pandas-ready CSV.

INPUT_PCAP="capture/sandbox_traffic.pcap"
OUTPUT_CSV="capture/parsed_telemetry.csv"

echo "[*] Initializing telemetry extraction..."
echo "[*] Reading: $INPUT_PCAP"

# -r: Read file
# -Y: Display filter (Only grab TCP traffic, ignore ARP/ICMP noise)
# -T fields: Output specific fields instead of full packet summaries
# -E options: Format as a CSV with a header row
# -e: The specific packet properties to extract
tshark -r $INPUT_PCAP -Y "tcp" -T fields \
  -E header=y \
  -E separator=, \
  -E quote=d \
  -e frame.time_epoch \
  -e ip.src \
  -e ip.dst \
  -e tcp.srcport \
  -e tcp.dstport \
  -e tcp.flags \
  > $OUTPUT_CSV

echo "[*] Extraction complete. Formatted telemetry saved to: $OUTPUT_CSV"