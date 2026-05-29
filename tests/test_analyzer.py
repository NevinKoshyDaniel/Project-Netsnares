import pytest
import pandas as pd
from unittest.mock import patch, mock_open
import json

# Import the function from your analyzer script
# Note: Ensure your analyzer.py has the analyze_traffic() function defined
from analyzer import analyze_traffic, JSON_OUTPUT

# --- FIXTURES (Mock Data Generators) ---

@pytest.fixture
def benign_traffic_data():
    """Simulates 40 normal background packets (below the 50 pkt/sec threshold)."""
    return pd.DataFrame({
        'frame.time_epoch': [1680000000.0] * 40,
        'tcp.flags': ['0x0010'] * 40, # Standard ACK packets
        'tcp.dstport': [443.0] * 40
    })

@pytest.fixture
def l4_syn_scan_data():
    """Simulates 100 packets where 90% are SYN requests (Flag 0x002)."""
    flags = ['0x0002'] * 90 + ['0x0010'] * 10
    return pd.DataFrame({
        'frame.time_epoch': [1680000001.0] * 100,
        'tcp.flags': flags,
        'tcp.dstport': [22.0] * 100
    })

@pytest.fixture
def l7_web_flood_data():
    """Simulates 100 packets where 100% target port 80, but handshakes are complete (ACKs)."""
    return pd.DataFrame({
        'frame.time_epoch': [1680000002.0] * 100,
        'tcp.flags': ['0x0010'] * 100, # ACKs, not SYNs
        'tcp.dstport': [80.0] * 100
    })


# --- TEST CASES ---

@patch('analyzer.pd.read_csv')
@patch('builtins.open', new_callable=mock_open)
def test_benign_baseline_detection(mock_file, mock_read_csv, benign_traffic_data):
    """Test that low-volume traffic is classified as BENIGN."""
    mock_read_csv.return_value = benign_traffic_data
    
    analyze_traffic()
    
    # Read the JSON that the script attempted to write
    written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
    timeline = json.loads(written_data)
    
    assert len(timeline) == 1
    assert timeline[0]["threat_assessment"] == "BENIGN_BASELINE"
    assert timeline[0]["total_packets"] == 40


@patch('analyzer.pd.read_csv')
@patch('builtins.open', new_callable=mock_open)
def test_l4_syn_scan_detection(mock_file, mock_read_csv, l4_syn_scan_data):
    """Test that high-volume, high-SYN traffic triggers L4 Critical Alert."""
    mock_read_csv.return_value = l4_syn_scan_data
    
    analyze_traffic()
    
    written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
    timeline = json.loads(written_data)
    
    assert len(timeline) == 1
    assert timeline[0]["threat_assessment"] == "CRITICAL_ATTACK_L4"
    assert timeline[0]["syn_ratio_percent"] == 90.0


@patch('analyzer.pd.read_csv')
@patch('builtins.open', new_callable=mock_open)
def test_l7_web_flood_detection(mock_file, mock_read_csv, l7_web_flood_data):
    """Test that high-volume port 80 traffic with low SYNs triggers L7 Critical Alert."""
    mock_read_csv.return_value = l7_web_flood_data
    
    analyze_traffic()
    
    written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
    timeline = json.loads(written_data)
    
    assert len(timeline) == 1
    assert timeline[0]["threat_assessment"] == "CRITICAL_ATTACK_L7"
    assert timeline[0]["web_ratio_percent"] == 100.0