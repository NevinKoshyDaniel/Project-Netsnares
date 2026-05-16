import pandas as pd
import json
import logging

logging.basicConfig(level=logging.INFO, format='[*] %(message)s')

# ==========================================
# --- PIPELINE CONFIGURATION & TUNING ---
# ==========================================
CSV_PATH = "capture/parsed_telemetry.csv"
JSON_OUTPUT = "capture/forensic_timeline.json"

# Temporal Binning: '1s' for high-resolution, '5s' to catch "Low & Slow" attacks
TIME_BIN = '1s' 

# Heuristic Thresholds: Minimums required to trigger an alert
VOLUME_THRESHOLD = 30       # Lowered to 30 to catch rate-limited attacks
SYN_RATIO_THRESHOLD = 40    # % of traffic that must be SYN packets for L4 Alert
WEB_RATIO_THRESHOLD = 40    # % of traffic aimed at Port 80 for L7 Alert
# ==========================================


def analyze_traffic():
    logging.info(f"Ingesting telemetry from {CSV_PATH}...")
    
    try:
        # Stage 1: Data Ingestion (Vectorized load)
        df = pd.read_csv(CSV_PATH).dropna()
    except FileNotFoundError:
        logging.error("CSV not found. Did you run extract_telemetry.sh?")
        return

    # Sanitize and convert data types
    df['timestamp'] = pd.to_datetime(df['frame.time_epoch'], unit='s')
    df['tcp.flags'] = df['tcp.flags'].astype(str).str.strip('\"')
    df['tcp.dstport'] = pd.to_numeric(df['tcp.dstport'], errors='coerce').fillna(0)

    logging.info(f"Stage 2: Grouping data into {TIME_BIN} temporal windows...")
    time_bins = df.groupby(pd.Grouper(key='timestamp', freq=TIME_BIN))

    timeline = []
    
    for time_window, group in time_bins:
        if group.empty:
            continue
            
        total_packets = len(group)
        
        # Stage 3: Feature Extraction (Math)
        # Calculate SYN packets (Flag 0x002)
        syn_packets = len(group[group['tcp.flags'].str.endswith('2', na=False)])
        syn_ratio = (syn_packets / total_packets) * 100 if total_packets > 0 else 0
        
        # Calculate Web Traffic (Port 80)
        web_packets = len(group[group['tcp.dstport'] == 80.0])
        web_ratio = (web_packets / total_packets) * 100 if total_packets > 0 else 0

        # Stage 4: Heuristic Classification (Ruleset)
        if total_packets > VOLUME_THRESHOLD and syn_ratio > SYN_RATIO_THRESHOLD:
            threat_level = "CRITICAL_ATTACK_L4"
            activity = f"Layer 4: SYN Scan (> {SYN_RATIO_THRESHOLD}% SYN Ratio)"
            
        elif total_packets > VOLUME_THRESHOLD and web_ratio > WEB_RATIO_THRESHOLD and syn_ratio < (SYN_RATIO_THRESHOLD - 10):
            threat_level = "CRITICAL_ATTACK_L7"
            activity = f"Layer 7: Web Flood (> {WEB_RATIO_THRESHOLD}% Web Traffic)"
            
        else:
            threat_level = "BENIGN_BASELINE"
            activity = "Normal background noise"

        # Append to structured timeline payload
        timeline.append({
            "time": str(time_window),
            "total_packets": total_packets,
            "syn_packets": syn_packets,
            "web_packets": web_packets,
            "syn_ratio_percent": round(syn_ratio, 2),
            "web_ratio_percent": round(web_ratio, 2),
            "threat_assessment": threat_level,
            "activity_signature": activity
        })

    logging.info("Forensic analysis complete. Compiling JSON payload...")
    
    with open(JSON_OUTPUT, 'w') as f:
        json.dump(timeline, f, indent=4)
        
    logging.info(f"Exported graphical timeline to {JSON_OUTPUT}")
    
    # --- SPLIT TERMINAL SUMMARY ---
    print("\n--- FORENSIC TIMELINE SUMMARY ---")
    l4_attacks = [entry for entry in timeline if entry["threat_assessment"] == "CRITICAL_ATTACK_L4"]
    l7_attacks = [entry for entry in timeline if entry["threat_assessment"] == "CRITICAL_ATTACK_L7"]
    
    if l4_attacks or l7_attacks:
        if l4_attacks:
            print(f"[!] Detected {len(l4_attacks)} temporal windows of Layer 4 Reconnaissance.")
            print(f"    -> Commenced at: {l4_attacks[0]['time']}")
            print(f"    -> Peak Volume:  {max(entry['total_packets'] for entry in l4_attacks)} packets/window")
        if l7_attacks:
            print(f"[!] Detected {len(l7_attacks)} temporal windows of Layer 7 Exploitation.")
            print(f"    -> Commenced at: {l7_attacks[0]['time']}")
            print(f"    -> Peak Volume:  {max(entry['total_packets'] for entry in l7_attacks)} packets/window")
    else:
        print("[✓] No structured attacks detected in this dataset. Baseline normal.")

if __name__ == "__main__":
    analyze_traffic()