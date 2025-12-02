"""
Encrypted Tunnel Example
Demonstrates secure data transmission through PQC-based tunnel
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vpn_core import EncryptedTunnel


def main():
    print("=== Encrypted Tunnel Example ===\n")
    
    # Create a session key (normally from handshake)
    session_key = b'0123456789ABCDEF0123456789ABCDEF'  # 32 bytes (256-bit)
    
    print("1. Creating encrypted tunnel...")
    tunnel = EncryptedTunnel(session_key, tunnel_id="example-tunnel-1")
    print("   ✓ Tunnel created\n")
    
    # Test messages
    messages = [
        b"Hello, secure world!",
        b"This is an encrypted message.",
        b"Quantum-resistant encryption.",
        b"X" * 1024,  # 1KB message
    ]
    
    print("2. Encrypting and decrypting messages...\n")
    
    for i, message in enumerate(messages):
        print(f"Message {i+1}:")
        print(f"  Original: {message[:30]}{'...' if len(message) > 30 else ''}")
        print(f"  Size: {len(message)} bytes")
        
        # Encrypt
        encrypted = tunnel.encrypt(message)
        print(f"  Encrypted: {len(encrypted.to_bytes())} bytes")
        
        # Decrypt
        decrypted = tunnel.decrypt(encrypted)
        
        # Verify
        if decrypted == message:
            print(f"  Status: ✓ Verified\n")
        else:
            print(f"  Status: ✗ Failed\n")
            return 1
    
    # Show metrics
    print("3. Tunnel Performance Metrics:")
    metrics = tunnel.get_tunnel_metrics()
    print(f"   Packets sent: {metrics['packets_sent']}")
    print(f"   Packets received: {metrics['packets_received']}")
    print(f"   Bytes sent: {metrics['bytes_sent']}")
    print(f"   Avg encryption time: {metrics['avg_encryption_time_ms']:.2f} ms")
    print(f"   Avg decryption time: {metrics['avg_decryption_time_ms']:.2f} ms")
    print(f"   Throughput: {metrics['throughput_mbps']:.2f} Mbps\n")
    
    print("✓ All tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
