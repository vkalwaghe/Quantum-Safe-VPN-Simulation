"""
Network VPN Example
Demonstrates real socket-based VPN server and client
"""

import sys
import time
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vpn_core.network import VPNServer, VPNClient


def run_server(host: str = "127.0.0.1", port: int = 8443):
    """Run VPN server"""
    server = VPNServer(host, port, max_clients=5)
    
    print(f"\n[Server] Starting VPN Server on {host}:{port}...")
    server.start()


def run_client_test(server_host: str = "127.0.0.1", server_port: int = 8443):
    """Run VPN client test"""
    time.sleep(1)  # Wait for server to start
    
    client = VPNClient(server_host, server_port, client_id="test-client-1")
    
    print(f"\n[Client] Connecting to VPN server...")
    if not client.connect():
        print("[Client] Connection failed!")
        return
    
    print("[Client] Connected successfully!")
    
    # Send test messages
    test_messages = [
        b"Hello from VPN client!",
        b"Quantum-safe communication.",
        b"Testing encrypted tunnel.",
    ]
    
    for msg in test_messages:
        print(f"\n[Client] Sending: {msg.decode()}")
        if client.send_data(msg):
            response = client.receive_data(timeout=5)
            if response:
                print(f"[Client] Received: {response.decode()}")
            else:
                print("[Client] No response received")
    
    time.sleep(1)
    client.disconnect()
    print("[Client] Disconnected")


def main():
    """Main demo function"""
    print("=" * 80)
    print("  Quantum-Safe VPN Network Demo")
    print("  Real Socket-Based Server and Client")
    print("=" * 80)
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Run client
    try:
        run_client_test()
    except KeyboardInterrupt:
        print("\n[Demo] Interrupted by user")
    except Exception as e:
        print(f"\n[Demo] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
