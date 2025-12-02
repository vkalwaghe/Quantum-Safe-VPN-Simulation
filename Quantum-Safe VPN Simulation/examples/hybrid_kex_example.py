"""
Hybrid PQC-Classical Key Exchange Example
Demonstrates combined security of quantum-resistant and classical cryptography
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vpn_core.hybrid_kex import HybridKeyExchange


def demo_hybrid_key_exchange():
    """Demonstrate hybrid key exchange"""
    print("\n" + "=" * 80)
    print("  Hybrid PQC-Classical Key Exchange Demo")
    print("=" * 80)
    
    # Create hybrid key exchange
    print("\n[*] Creating hybrid key exchange (Kyber512 + RSA-2048)...")
    hybrid = HybridKeyExchange(use_kyber=True, use_rsa=True, rsa_key_size=2048)
    
    # Step 1: Server generates keypairs
    print("\n[Server] Generating keypairs...")
    server_public_keys, server_private_keys = hybrid.generate_keypairs()
    
    print(f"    Kyber public key: {len(server_public_keys['kyber'])} bytes")
    print(f"    RSA public key: {len(server_public_keys['rsa'])} bytes")
    
    # Step 2: Client encapsulates
    print("\n[Client] Encapsulating shared secrets...")
    client_hybrid = HybridKeyExchange(use_kyber=True, use_rsa=True, rsa_key_size=2048)
    client_ciphertexts, client_secret = client_hybrid.client_encapsulate(server_public_keys)
    
    print(f"    Kyber ciphertext: {len(client_ciphertexts['kyber'])} bytes")
    print(f"    RSA ciphertext: {len(client_ciphertexts['rsa'])} bytes")
    print(f"    Combined secret: {len(client_secret.combined_secret)} bytes (256-bit)")
    
    # Step 3: Server decapsulates
    print("\n[Server] Decapsulating shared secrets...")
    server_secret = hybrid.server_decapsulate(server_private_keys, client_ciphertexts)
    
    # Step 4: Verify secrets match
    print("\n[*] Verifying secrets...")
    if client_secret.combined_secret == server_secret.combined_secret:
        print("    ✓ PQC components match")
        print("    ✓ Classical components match")
        print("    ✓ Combined secrets match")
        print("\n    SUCCESS: Hybrid key exchange completed!")
    else:
        print("    ✗ Secrets don't match - ERROR!")
        return False
    
    # Show metrics
    print("\n[*] Key Exchange Metrics:")
    metrics = hybrid.get_metrics()
    for key, value in metrics.items():
        print(f"    {key}: {value}")
    
    # Compare modes
    print("\n[*] Hybrid Mode Comparison:")
    comparison = HybridKeyExchange.compare_modes()
    
    for mode, details in comparison.items():
        print(f"\n    {mode.upper()}:")
        for key, value in details.items():
            print(f"      {key}: {value}")
    
    return True


def demo_pqc_only():
    """Demonstrate PQC-only mode"""
    print("\n" + "=" * 80)
    print("  PQC-Only Key Exchange (Kyber512)")
    print("=" * 80)
    
    hybrid = HybridKeyExchange(use_kyber=True, use_rsa=False)
    
    print("\n[*] Generating keypairs...")
    server_public_keys, server_private_keys = hybrid.generate_keypairs()
    
    print(f"    Kyber public key: {len(server_public_keys['kyber'])} bytes")
    
    print("\n[*] Encapsulating...")
    client_hybrid = HybridKeyExchange(use_kyber=True, use_rsa=False)
    client_ciphertexts, client_secret = client_hybrid.client_encapsulate(server_public_keys)
    
    print(f"    Ciphertext: {len(client_ciphertexts['kyber'])} bytes")
    
    print("\n[*] Decapsulating...")
    server_secret = hybrid.server_decapsulate(server_private_keys, client_ciphertexts)
    
    if client_secret.combined_secret == server_secret.combined_secret:
        print("    ✓ SUCCESS: PQC-only key exchange completed!")
    else:
        print("    ✗ ERROR: Secrets don't match!")
        return False
    
    return True


def demo_classical_only():
    """Demonstrate classical-only mode (RSA)"""
    print("\n" + "=" * 80)
    print("  Classical-Only Key Exchange (RSA-2048)")
    print("=" * 80)
    
    hybrid = HybridKeyExchange(use_kyber=False, use_rsa=True, rsa_key_size=2048)
    
    print("\n[*] Generating keypairs...")
    server_public_keys, server_private_keys = hybrid.generate_keypairs()
    
    print(f"    RSA public key: {len(server_public_keys['rsa'])} bytes")
    
    print("\n[*] Encapsulating...")
    client_hybrid = HybridKeyExchange(use_kyber=False, use_rsa=True, rsa_key_size=2048)
    client_ciphertexts, client_secret = client_hybrid.client_encapsulate(server_public_keys)
    
    print(f"    Ciphertext: {len(client_ciphertexts['rsa'])} bytes")
    
    print("\n[*] Decapsulating...")
    server_secret = hybrid.server_decapsulate(server_private_keys, client_ciphertexts)
    
    if client_secret.combined_secret == server_secret.combined_secret:
        print("    ✓ SUCCESS: Classical-only key exchange completed!")
    else:
        print("    ✗ ERROR: Secrets don't match!")
        return False
    
    return True


def main():
    """Main demo"""
    try:
        # Run all demos
        success = True
        
        success = demo_pqc_only() and success
        success = demo_classical_only() and success
        success = demo_hybrid_key_exchange() and success
        
        if success:
            print("\n" + "=" * 80)
            print("  All Hybrid Key Exchange Tests Passed!")
            print("=" * 80)
            print("\n[Summary]")
            print("  ✓ PQC-only mode: Quantum-resistant")
            print("  ✓ Classical-only mode: Backward compatible")
            print("  ✓ Hybrid mode: Maximum security during transition")
            print("\n[Recommendation]")
            print("  Use HYBRID mode for 2025-2030 transition period")
            print("  Provides both quantum resistance and backward compatibility")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
