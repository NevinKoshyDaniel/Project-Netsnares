.PHONY: setup up down attack pipeline clean

environment:
	@echo "[*] Spinning up NetSnares DMZ..."
	docker-compose up -d --build

teardown:
	@echo "[*] Tearing down infrastructure..."
	docker-compose down -v

attack:
	@echo "[*] Executing multi-layer threat from custom attacker image..."
	docker exec -it netsnares_attacker /attack.sh

pipeline:
	@echo "[*] Running forensic extraction and analytics..."
	chmod +x extract_telemetry.sh
	./extract_telemetry.sh
	python3 analyzer.py
	python3 loki_shipper.py

clean:
	@echo "[*] Cleaning up old forensic artifacts..."
	rm -f capture/sandbox_traffic.pcap capture/parsed_telemetry.csv capture/forensic_timeline.json