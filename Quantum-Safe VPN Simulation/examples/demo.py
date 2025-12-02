"""
Quantum-Safe VPN Simulation - Main Demo
Demonstrates PQC-based VPN handshake and encrypted communication
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vpn_core import PQCHandshake, EncryptedTunnel
from performance.benchmark import PerformanceBenchmark


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def demo_pqc_handshake():
    """Demonstrate PQC-based VPN handshake"""
    print_header("PQC-Based VPN Handshake Demo")
    
    print("\n[*] Initializing VPN endpoints...")
    client = PQCHandshake("client-vpn-001", is_server=False)
    server = PQCHandshake("server-vpn-001", is_server=True)
    
    print(f"    Client ID: {client.peer_id}")
    print(f"    Server ID: {server.peer_id}")
    
    # Step 1: Client Hello
    print("\n[STEP 1] Client sends ClientHello with public keys...")
    client_hello = client.create_client_hello()
    print(f"    Kyber Public Key: {len(client_hello.client_kyber_public_key)} bytes")
    print(f"    Dilithium Public Key: {len(client_hello.client_dilithium_public_key)} bytes")
    print(f"    Timestamp: {client_hello.timestamp}")
    
    # Step 2: Server Hello
    print("\n[STEP 2] Server responds with ServerHello...")
    server_hello = server.process_client_hello(client_hello)
    print(f"    Kyber Public Key: {len(server_hello.server_kyber_public_key)} bytes")
    print(f"    Dilithium Public Key: {len(server_hello.server_dilithium_public_key)} bytes")
    print(f"    Encapsulated Secret (Ciphertext): {len(server_hello.server_kyber_ciphertext)} bytes")
    
    # Step 3: Client Finished
    print("\n[STEP 3] Client sends ClientFinished...")
    client_finished_sig, client_session_key = client.process_server_hello(server_hello)
    print(f"    Signature: {len(client_finished_sig)} bytes")
    print(f"    Session Key: {len(client_session_key)} bytes (256-bit)")
    print(f"    Session Key (hex): {client_session_key.hex()[:32]}...")
    
    # Step 4: Server Finished
    print("\n[STEP 4] Server sends ServerFinished...")
    server_finished_sig = server.process_client_finished(client_finished_sig)
    print(f"    Signature: {len(server_finished_sig)} bytes")
    print(f"    Session Key: {len(server.session_key)} bytes (256-bit)")
    
    # Step 5: Client Verification
    print("\n[STEP 5] Client verifies ServerFinished...")
    client.process_server_finished(server_finished_sig)
    print("    ✓ Handshake completed successfully!")
    
    # Print handshake metrics
    print("\n[HANDSHAKE METRICS]")
    client_metrics = client.get_handshake_metrics()
    print(json.dumps(client_metrics, indent=2, default=str))
    
    return client.session_key


def demo_encrypted_tunnel(session_key: bytes):
    """Demonstrate encrypted tunnel communication"""
    print_header("Encrypted Tunnel Demo")
    
    print("\n[*] Creating encrypted tunnel with AES-256-GCM...")
    tunnel = EncryptedTunnel(session_key, tunnel_id="vpn-tunnel-001")
    
    # Test messages
    test_messages = [
        b"Hello from VPN client!",
        b"This is encrypted tunnel communication.",
        b"Quantum-resistant encryption in action.",
        b"X" * 1000,  # Large message
    ]
    
    print("\n[*] Encrypting and decrypting test messages...")
    
    for i, message in enumerate(test_messages):
        print(f"\n[Message {i+1}] Original: {message[:50]}{'...' if len(message) > 50 else ''}")
        print(f"            Size: {len(message)} bytes")
        
        # Encrypt
        encrypted_packet = tunnel.encrypt(message)
        print(f"            Encrypted: {len(encrypted_packet.to_bytes())} bytes")
        print(f"            IV: {len(encrypted_packet.iv)} bytes")
        print(f"            Tag: {len(encrypted_packet.tag)} bytes")
        
        # Decrypt
        decrypted = tunnel.decrypt(encrypted_packet)
        assert decrypted == message, "Decryption failed!"
        print(f"            Decrypted: ✓ Verified")
    
    # Print tunnel metrics
    print("\n[TUNNEL METRICS]")
    tunnel_metrics = tunnel.get_tunnel_metrics()
    print(json.dumps(tunnel_metrics, indent=2))


def demo_performance_benchmarks():
    """Demonstrate performance benchmarking"""
    print_header("Performance Benchmark Demo")
    
    benchmark = PerformanceBenchmark()
    
    print("\n[*] Running Kyber benchmarks...")
    print("[1] Kyber Key Generation")
    kyber_keygen = benchmark.benchmark_kyber_keygen(iterations=5)
    print(f"    Average: {kyber_keygen.avg_time_ms:.2f} ms")
    print(f"    Min: {kyber_keygen.min_time_ms:.2f} ms, Max: {kyber_keygen.max_time_ms:.2f} ms")
    
    print("[2] Kyber Encapsulation")
    kyber_encap = benchmark.benchmark_kyber_encapsulation(iterations=5)
    print(f"    Average: {kyber_encap.avg_time_ms:.2f} ms")
    
    print("[3] Kyber Decapsulation")
    kyber_decap = benchmark.benchmark_kyber_decapsulation(iterations=5)
    print(f"    Average: {kyber_decap.avg_time_ms:.2f} ms")
    
    print("\n[*] Running Dilithium benchmarks...")
    print("[4] Dilithium Key Generation")
    dil_keygen = benchmark.benchmark_dilithium_keygen(iterations=5)
    print(f"    Average: {dil_keygen.avg_time_ms:.2f} ms")
    
    print("[5] Dilithium Signing")
    dil_sign = benchmark.benchmark_dilithium_sign(iterations=10)
    print(f"    Average: {dil_sign.avg_time_ms:.2f} ms")
    
    print("[6] Dilithium Verification")
    dil_verify = benchmark.benchmark_dilithium_verify(iterations=10)
    print(f"    Average: {dil_verify.avg_time_ms:.2f} ms")
    
    print("\n[*] Running tunnel benchmarks...")
    print("[7] AES-256-GCM Encryption (100KB)")
    tunnel_encrypt = benchmark.benchmark_tunnel_encryption(data_size_kb=100, iterations=5)
    print(f"    Average: {tunnel_encrypt.avg_time_ms:.2f} ms")
    
    print("\n[*] Running full handshake benchmark...")
    print("[8] Full PQC VPN Handshake")
    handshake_bench = benchmark.benchmark_full_handshake(iterations=3)
    print(f"    Average: {handshake_bench['avg_time_ms']:.2f} ms")
    print(f"    Min: {handshake_bench['min_time_ms']:.2f} ms, Max: {handshake_bench['max_time_ms']:.2f} ms")
    
    print("\n[BENCHMARK COMPARISON REPORT]")
    comparison = benchmark.generate_comparison_report()
    
    print("\nKyber vs Classical Key Exchange:")
    for key, value in comparison['pqc_kyber'].items():
        print(f"  {key}: {value}")
    
    print("\nDilithium vs Classical Signatures:")
    for key, value in comparison['pqc_dilithium'].items():
        print(f"  {key}: {value}")
    
    print("\n6G Cybersecurity Implications:")
    for implication in comparison['conclusions']['6g_implications']:
        print(f"  • {implication}")


def main():
    """Main demo function"""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█  Quantum-Safe VPN Simulation - Post-Quantum Cryptography Demo" + " " * 10 + "█")
    print("█  Python | Cryptography | Networking | 2025" + " " * 28 + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    try:
        # Run handshake demo
        session_key = demo_pqc_handshake()
        
        # Run tunnel demo
        demo_encrypted_tunnel(session_key)
        
        # Run performance benchmarks
        demo_performance_benchmarks()
        
        print_header("Demo Completed Successfully!")
        print("\n[✓] PQC-based VPN handshake established")
        print("[✓] Encrypted tunnel communication verified")
        print("[✓] Performance benchmarks completed")
        print("\n[Summary]")
        print("  This simulation demonstrates:")
        print("  1. Kyber-based quantum-resistant key exchange")
        print("  2. Dilithium-based quantum-resistant authentication")
        print("  3. AES-256-GCM encrypted data tunneling")
        print("  4. Performance evaluation against classical cryptography")
        print("  5. Application to 6G-era cybersecurity")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
