# 🛡️ NetSnares: Cloud-Native Network Forensics Sandbox

A custom-engineered DevSecOps pipeline and threat analysis sandbox. This project simulates multi-stage cyberattacks within an isolated, resource-constrained Docker environment, captures the raw network telemetry, and utilizes a custom Python/Pandas analytics engine to mathematically isolate both volumetric and rate-limited advanced persistent threats.

## 🏗️ Architecture & Tech Stack
* **Infrastructure:** Docker & Docker Compose (with strict `cgroups` resource limitations).
* **Threat Generation:** Bash, Nmap, cURL (simulating Layer 4 SYN Scans and Layer 7 Web Floods).
* **Data Engineering:** Python, Pandas (Vectorized temporal binning and heuristic classification).
* **Observability:** Grafana, Grafana Loki, API integration.

## 📂 Repository Structure
```text
CNS/
├── Makefile                       # Orchestrates the DevSecOps pipeline
├── docker-compose.yml             # Defines the isolated target network and attacker container
├── analyzer.py                    # The Pandas-driven forensic math engine
├── loki_shipper.py                # Timezone-aware API shipper for Grafana Loki
├── netsnares_dashboard.json       # Exported Dashboard-as-Code
└── traffic_generator/
    └── attack.sh                  # The multi-stage "Low and Slow" threat script
```

## Quickstart Guide

1. Spin up the Sandbox
Initialize the isolated Docker network and ensure the Loki/Grafana observability stack is running.

```
make environment
```

2. Execute the Threat Simulation
Inject and execute the custom attack script. This simulation executes a rate-limited, "Low and Slow" Layer 4 Reconnaissance scan, followed by a sustained Layer 7 HTTP GET flood. (Note: This takes roughly 1.5 to 2 minutes to complete).

```
make attack
```

Ensure your packet sniffer (e.g., tshark) is actively capturing traffic on the Docker bridge network during this time.

3. Run the Forensics Pipeline
Once the attack concludes and the PCAP is saved, execute the analytics pipeline. This will:

Parse the PCAP into a CSV.

Ingest the data into the Pandas engine (analyzer.py) for temporal binning.

Push the analyzed, timezone-corrected JSON payloads to Loki via API (loki_shipper.py).

```
make pipeline
```

4. 📊 Importing the Threat Dashboard (Grafana)
To view the final forensic telemetry, you do not need to build the visualizations manually. The dashboard configuration is saved as code in this repository.

Navigate to Grafana at http://localhost:3000 (Default credentials).

- Click the Dashboards menu on the left sidebar.
- Click the New dropdown button and select Import.
- Click Upload JSON file and select the netsnares_dashboard.json file located in the root of this directory.
- Select the Loki database from the dropdown and click Import.
- Set the Grafana time-picker to the window in which you ran make attack.

## 🧠 Key Engineering Decisions

Resource Constraints (OOM Prevention): The attacker container is hard-capped at 718MB of RAM using Docker Compose deploy.resources. The bash scripts utilize concurrency batching to prevent PID exhaustion and Out-Of-Memory (OOM) kernel panics during the Layer 7 flood. Total memory usage for the entire suitex will always be less than 4GB.

Temporal Binning over Packet Analysis: To catch rate-limited attacks designed to evade standard threshold alarms, the Python analyzer groups traffic into discrete time windows (1s frequency) using pd.Grouper. This allows the engine to calculate percentage-based signatures (e.g., > 40% SYN flags) rather than relying purely on volume.

Timezone-Aware Observability: The loki_shipper.py script enforces strict UTC timezone casting before calculating the 19-digit Unix nanosecond epoch required by the Loki API, preventing silent timezone-shift data loss in Grafana.
