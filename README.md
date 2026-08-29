# Quantum-Safe VPN Simulation

## Overview

A post-quantum cryptography (PQC) enabled VPN prototype that replaces classical RSA/ECDH with NIST-approved quantum-resistant algorithms: **Kyber** for key exchange and **Dilithium** for digital signatures.

**Project Status:** 2025 | Python, Cryptography, Networking

## Features

✅ **Post-Quantum Key Exchange (Kyber)**
- NIST-approved KEM (Key Encapsulation Mechanism)
- Quantum-resistant key establishment
- Multiple security levels (512, 768, 1024 bits)

✅ **Post-Quantum Digital Signatures (Dilithium)**
- NIST-approved signature scheme
- Quantum-resistant authentication
- Multiple security levels (2, 3, 5)

✅ **PQC-Based VPN Handshake Protocol**
- Four-phase authentication and key agreement
- Client-server mutual authentication
- Session key derivation using HKDF

✅ **Encrypted Tunneling**
- AES-256-GCM encryption for data transmission
- Authenticated encryption with associated data (AEAD)
- Per-packet IV management with counter mode

✅ **Performance Evaluation**
- Comprehensive benchmarking suite
- Latency analysis for PQC operations
- Comparison with classical cryptography metrics
- 6G cybersecurity assessment

## Project Structure

```
Quantum-Safe VPN Simulation/
├── vpn_core/                    # Core VPN implementation
│   ├── __init__.py
│   ├── kyber_kex.py            # Kyber key exchange module
│   ├── dilithium_sig.py        # Dilithium signature module
│   ├── handshake.py            # PQC-based handshake protocol
│   └── tunnel.py               # Encrypted tunnel implementation
├── performance/                 # Performance evaluation
│   ├── __init__.py
│   └── benchmark.py            # Benchmarking suite
├── tests/                       # Unit tests
│   ├── __init__.py
│   ├── test_kyber.py
│   ├── test_dilithium.py
│   ├── test_handshake.py
│   └── test_tunnel.py
├── examples/                    # Example usage
│   ├── demo.py                 # Complete demo
│   ├── simple_handshake.py    # Simple handshake example
│   └── tunnel_example.py       # Tunnel usage example
├── requirements.txt             # Python dependencies
├── README.md                   # This file
└── ARCHITECTURE.md             # Detailed architecture
```

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. Clone/extract the project:
```bash
cd "Quantum-Safe VPN Simulation"
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Dependencies

- `liboqs-python==0.9.0` - NIST's Open Quantum Safe library
- `cryptography==41.0.7` - Modern cryptography library
- `pycryptodome==3.19.0` - Cryptographic algorithms
- `numpy==1.24.3` - Numerical computing
- `matplotlib==3.7.2` - Performance visualization
- `psutil==5.9.6` - System performance metrics

## Quick Start

### Run the Full Demo

```bash
python examples/demo.py
```

This demonstrates:
1. PQC-based VPN handshake
2. Encrypted tunnel communication
3. Performance benchmarks
4. Comparison with classical cryptography

### Python Usage

```python
from vpn_core import PQCHandshake, EncryptedTunnel

# Step 1: Handshake
client = PQCHandshake("client-1", is_server=False)
server = PQCHandshake("server-1", is_server=True)

# Exchange hello messages
client_hello = client.create_client_hello()
server_hello = server.process_client_hello(client_hello)

# Complete handshake
client_finished, session_key = client.process_server_hello(server_hello)
server_finished = server.process_client_finished(client_finished)
client.process_server_finished(server_finished)

# Step 2: Encrypted tunnel
tunnel = EncryptedTunnel(session_key)

# Encrypt data
message = b"Quantum-safe communication"
encrypted_packet = tunnel.encrypt(message)

# Decrypt data
decrypted = tunnel.decrypt(encrypted_packet)
assert decrypted == message
```

## Handshake Protocol

The PQC-based handshake follows a four-phase process:

```
Client                                      Server
  |                                          |
  +------------- ClientHello ----+          |
  |                               |          |
  |                         +--- (generates) ---+
  |                         |   Kyber secret   |
  |                         +---(encapsulates)-+
  |                               |          |
  | <------- ServerHello ---------+          |
  |   (Kyber ciphertext)                     |
  |                                          |
  +----- (decapsulates) -----+               |
  |  shared secret           |               |
  +----- (signs public key) -+               |
  |                               |          |
  | -------- ClientFinished ------+          |
  |   (Dilithium signature)       |          |
  |                         +--- (verifies) -+
  |                         +--- (signs) ----+
  |                               |          |
  | <------- ServerFinished ------+          |
  |   (Dilithium signature)                  |
  |                                          |
  +----- (verifies) -----+                   |
  |                      |                   |
  | ========== TUNNEL ESTABLISHED ===========|
  | (Session key: derived from shared secret)|
```

**Key Features:**
- Mutual authentication via Dilithium signatures
- Quantum-resistant shared secret via Kyber
- HKDF-based session key derivation
- Perfect forward secrecy (when combined with ephemeral keys)

## Encryption Tunnel

### Message Format

```
┌─────────┬──────┬─────┬───────┬─────┬──────┬────────────┐
│ Pkt ID  │ IV   │ Tag │ Ctext │ ...                      │
├─────────┼──────┼─────┼───────┼─────┼──────┼────────────┤
│ 4 bytes │ 12B  │ 16B │ N     │                           │
└─────────┴──────┴─────┴───────┴─────┴──────┴────────────┘

- IV: Initialized Vector (counter + random)
- Tag: AES-GCM authentication tag
- Ctext: AES-256 ciphertext
```

### Encryption/Decryption

All data transmitted through the tunnel is encrypted using:
- **Algorithm:** AES-256 in GCM mode
- **Key:** 256-bit session key from PQC handshake
- **Authentication:** AEAD with per-packet tags
- **Latency:** < 10ms per packet (benchmark dependent)

## Performance Analysis

### Benchmark Results

Run benchmarks with:
```bash
python examples/demo.py
```

Expected output includes:
- Kyber KeyGen: ~1-2 ms
- Kyber Encapsulate: ~0.5 ms
- Kyber Decapsulate: ~0.5 ms
- Dilithium KeyGen: ~2-3 ms
- Dilithium Sign: ~1-2 ms
- Dilithium Verify: ~3-4 ms
- AES-256-GCM (100KB): ~2-3 ms

### Key Size Comparison

| Algorithm | Classical | Quantum-Safe | Ratio |
|-----------|-----------|--------------|-------|
| Key Exchange | RSA 2048: 294B | Kyber512: 800B | 2.7x |
| Signature | RSA 2048: 256B | Dilithium2: 2420B | 9.5x |

**Tradeoff:** Larger keys/signatures for quantum resistance

## 6G Cybersecurity Implications

### Threats from Quantum Computing

1. **Store-Now-Decrypt-Later (SNDL) Attacks**
   - Adversaries record encrypted traffic today
   - Decrypt with future quantum computers
   - **Mitigation:** PQC provides forward secrecy against this threat

2. **Harvest Now, Decrypt Later (HNDL)**
   - Classical cryptography becomes obsolete
   - Historical data retroactively compromised
   - **Mitigation:** PQC provides immediate protection

3. **6G Requirements**
   - Higher data rates demand efficient PQC
   - Larger key sizes acceptable with proper infrastructure
   - Hybrid approaches combining PQC + classical

### PQC Advantages for 6G

✓ **Standardization**
- NIST approved (Kyber, Dilithium)
- Industry adoption path established

✓ **Security Longevity**
- Protects against future quantum threats
- 20+ year security horizon

✓ **Interoperability**
- Hybrid PQC-classical implementations
- Gradual migration path

✓ **Performance**
- Acceptable latency for 6G applications
- Comparable to current cryptography

### Deployment Strategy

```
Timeline          Strategy
─────────────────────────────────
2024-2025    → NIST standardization
2025-2026    → Hybrid PQC+RSA/ECDH
2026-2028    → PQC-primary deployments
2028-2030    → 6G PQC-native infrastructure
```

## API Reference

### KyberKeyExchange

```python
from vpn_core import KyberKeyExchange

kyber = KyberKeyExchange("512")  # "512", "768", or "1024"

# Generate keypair
public_key, secret_key = kyber.generate_keypair()

# Client: Encapsulate
ciphertext, shared_secret = kyber.encapsulate(server_public_key)

# Server: Decapsulate
shared_secret = kyber.decapsulate(secret_key, ciphertext)

# Derive session key
session_key = kyber.derive_session_key(shared_secret, context)
```

### DilithiumSignature

```python
from vpn_core import DilithiumSignature

dilithium = DilithiumSignature("2")  # "2", "3", or "5"

# Generate keypair
public_key, secret_key = dilithium.generate_keypair()

# Sign message
signature = dilithium.sign(message, secret_key)

# Verify signature
is_valid = dilithium.verify(message, signature, public_key)
```

### PQCHandshake

```python
from vpn_core import PQCHandshake

# Initialize
client = PQCHandshake("client-1", is_server=False)
server = PQCHandshake("server-1", is_server=True)

# Complete handshake (see protocol section)
# ...

# Metrics
metrics = client.get_handshake_metrics()
```

### EncryptedTunnel

```python
from vpn_core import EncryptedTunnel

tunnel = EncryptedTunnel(session_key)

# Encrypt
packet = tunnel.encrypt(plaintext)

# Decrypt
plaintext = tunnel.decrypt(packet)

# Get metrics
metrics = tunnel.get_tunnel_metrics()
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
pytest tests/ -v --cov=vpn_core --cov=performance
```

Individual test files:
```bash
pytest tests/test_kyber.py
pytest tests/test_dilithium.py
pytest tests/test_handshake.py
pytest tests/test_tunnel.py
```

## Troubleshooting

### ImportError: liboqs.kex not found

**Solution:** Install liboqs-python:
```bash
pip install liboqs-python==0.9.0
```

### Performance is slower than expected

- Check system resources (CPU, memory)
- Run benchmarks in release mode (no debugging)
- Kyber/Dilithium have inherent computational costs

### Handshake fails with "Invalid signature"

- Ensure keypairs are generated fresh for each session
- Verify message ordering in handshake protocol
- Check that both sides use compatible PQC parameters

## Advanced Topics

### Hybrid PQC-Classical

For maximum security during transition:
```python
# Use both Kyber and ECDH
# Final key = KDF(kyber_secret XOR ecdh_secret)
```

### Performance Optimization

- Use larger security parameters only when needed
- Implement async handshake for high-throughput scenarios
- Cache keypairs for session reuse (with caution)

### Custom Key Sizes

Edit `vpn_core/` modules to support different parameter sets:
```python
kyber = KyberKeyExchange("768")  # Higher security
dilithium = DilithiumSignature("5")  # Highest security
```

## References

1. **NIST Post-Quantum Cryptography Standardization**
   - https://csrc.nist.gov/projects/post-quantum-cryptography/

2. **Kyber: Key Encapsulation Mechanism**
   - Specification: https://csrc.nist.gov/publications/detail/sp/800-227/final

3. **Dilithium: Digital Signature**
   - Specification: https://csrc.nist.gov/publications/detail/sp/800-227/final

4. **liboqs: Open Quantum Safe Library**
   - https://github.com/open-quantum-safe/liboqs-python

5. **6G Cybersecurity**
   - NIST Special Publication 800-227 (PQC Migration Roadmap)
   - IEEE 6G Vision and Requirements

## Contributing

Contributions welcome! Areas for enhancement:
- Hybrid PQC-classical implementations
- Additional PQC algorithms (SPHINCS+)
- Network protocol extensions (TLS 1.3 integration)
- Performance optimizations
- 6G-specific features

## License

MIT License - See LICENSE file for details

## Authors

Quantum-Safe VPN Simulation Team
- Post-Quantum Cryptography Research
- VPN Protocol Development
- 6G Cybersecurity Analysis

## Citation

If you use this project in research, please cite:

```bibtex
@project{quantum_safe_vpn_2025,
  title={Quantum-Safe VPN Simulation: Post-Quantum Cryptography for 6G},
  author={VPN Research Team},
  year={2025},
  url={https://github.com/your-repo}
}
```

## Questions & Support

For issues, questions, or suggestions:
1. Check existing documentation
2. Review test cases for usage examples
3. Open an issue with detailed information
4. Include system information and error logs

---

**Last Updated:** December 2025
**Status:** Active Development
**Python Version:** 3.8+
