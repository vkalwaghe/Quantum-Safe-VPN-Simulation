"""
Simple Handshake Example
Minimal example of PQC-based VPN handshake
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vpn_core import PQCHandshake


def main():
    print("=== Simple PQC Handshake Example ===\n")
    
    # Create client and server
    print("1. Creating client and server instances...")
    client = PQCHandshake("client", is_server=False)
    server = PQCHandshake("server", is_server=True)
    print("   ✓ Client and server created\n")
    
    # Step 1: ClientHello
    print("2. Client sends ClientHello...")
    client_hello = client.create_client_hello()
    print(f"   ✓ ClientHello: {len(client_hello.to_bytes())} bytes\n")
    
    # Step 2: ServerHello
    print("3. Server processes ClientHello and sends ServerHello...")
    server_hello = server.process_client_hello(client_hello)
    print(f"   ✓ ServerHello: {len(server_hello.to_bytes())} bytes\n")
    
    # Step 3: ClientFinished
    print("4. Client processes ServerHello and sends ClientFinished...")
    client_finished, client_key = client.process_server_hello(server_hello)
    print(f"   ✓ ClientFinished: {len(client_finished)} bytes")
    print(f"   ✓ Session Key: {client_key.hex()[:32]}...\n")
    
    # Step 4: ServerFinished
    print("5. Server processes ClientFinished and sends ServerFinished...")
    server_finished = server.process_client_finished(client_finished)
    print(f"   ✓ ServerFinished: {len(server_finished)} bytes\n")
    
    # Step 5: Verification
    print("6. Client verifies ServerFinished...")
    client.process_server_finished(server_finished)
    print("   ✓ Handshake completed!\n")
    
    # Show keys match
    if client.session_key == server.session_key:
        print("✓ SUCCESS: Session keys match!")
        print(f"  Session Key: {client.session_key.hex()}\n")
    else:
        print("✗ ERROR: Session keys don't match!")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
