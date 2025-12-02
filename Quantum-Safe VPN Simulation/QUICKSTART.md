# Quick Start Guide

## 5-Minute Setup & Run

### Step 1: Install Dependencies (2 minutes)

```bash
cd "Quantum-Safe VPN Simulation"
pip install -r requirements.txt
```

Expected output:
```
Successfully installed liboqs-python cryptography pycryptodome ...
```

### Step 2: Run the Demo (2 minutes)

```bash
python examples/demo.py
```

Expected output:
```
================================================================================
  Quantum-Safe VPN Simulation - Post-Quantum Cryptography Demo
  Python | Cryptography | Networking | 2025
================================================================================

[*] Initializing VPN endpoints...
    Client ID: client-vpn-001
    Server ID: server-vpn-001

[STEP 1] Client sends ClientHello with public keys...
    Kyber Public Key: 800 bytes
    Dilithium Public Key: 1312 bytes
    Timestamp: 1733155200.123456

[STEP 2] Server responds with ServerHello...
    Kyber Public Key: 800 bytes
    Dilithium Public Key: 1312 bytes
    Encapsulated Secret (Ciphertext): 768 bytes

[STEP 3] Client sends ClientFinished...
    Signature: 2420 bytes
    Session Key: 32 bytes (256-bit)
    Session Key (hex): 0123456789abcdef0123456789abcdef...

[STEP 4] Server sends ServerFinished...
    Signature: 2420 bytes
    Session Key: 32 bytes (256-bit)

[STEP 5] Client verifies ServerFinished...
    ✓ Handshake completed successfully!

[HANDSHAKE METRICS]
{
  "peer_id": "client-vpn-001",
  "is_server": false,
  "state": "COMPLETED",
  "total_messages": 4,
  "total_handshake_bytes": 10240,
  ...
}

[*] Creating encrypted tunnel with AES-256-GCM...

[*] Encrypting and decrypting test messages...

[Message 1] Original: Hello from VPN client!
            Size: 22 bytes
            Encrypted: 60 bytes
            IV: 12 bytes
            Tag: 16 bytes
            Decrypted: ✓ Verified

...

[*] Running Kyber benchmarks...
[1] Kyber Key Generation
    Average: 1.23 ms
    Min: 1.15 ms, Max: 1.45 ms

...

✓ Demo Completed Successfully!
```

### Step 3: Run Tests (1 minute - optional)

```bash
pytest tests/ -v
```

Expected output:
```
================================ test session starts =================================
collected 42 items

tests/test_kyber.py::TestKyberKeyExchange::test_initialization PASSED      [ 2%]
tests/test_kyber.py::TestKyberKeyExchange::test_keypair_generation PASSED  [ 5%]
...
================================ 42 passed in 3.45s ==================================
```

---

## What You Just Ran

### ✅ Handshake Phase
```
Client  ──────→  Server: "Here are my public keys"
Client  ←──────  Server: "Here are mine + encrypted secret"
Client  ──────→  Server: "I verified everything, here's my signature"
Client  ←──────  Server: "Handshake complete, here's my signature"
```

### ✅ Encryption Phase
```
Message: "Quantum-resistant encryption in action."
    │
    ├─→ [Encrypt with AES-256-GCM]
    │   ├─ Generate unique IV
    │   ├─ Encrypt payload
    │   └─ Generate authentication tag
    │
    ├─→ [Send encrypted packet]
    │
    ├─→ [Receive encrypted packet]
    │   ├─ Verify authentication tag
    │   ├─ Decrypt payload
    │   └─ Extract original message
    │
    └─→ Original message recovered: ✓
```

### ✅ Performance Benchmarks
- Kyber operations: ~1-2 ms
- Dilithium operations: ~2-4 ms
- Full handshake: ~8-10 ms
- Encryption (100KB): ~2-3 ms

---

## Key Concepts

### 🔐 Post-Quantum Cryptography
- **Kyber:** Quantum-resistant key exchange (lattice-based)
- **Dilithium:** Quantum-resistant digital signatures (lattice-based)
- **AES-256-GCM:** Modern authenticated encryption

### 🤝 Handshake Protocol
1. Client sends its public keys (Kyber + Dilithium)
2. Server responds with its keys + encapsulated secret
3. Client signs server's key and sends signature
4. Server signs client's key and sends signature
5. Both derive shared session key from secret

### 🔒 Encrypted Tunnel
- Uses 256-bit session key from handshake
- Each packet has unique IV and authentication tag
- Prevents tampering and unauthorized access

---

## Project Structure

```
vpn_core/              Core VPN implementation
  ├── kyber_kex.py    Quantum-resistant key exchange
  ├── dilithium_sig.py Quantum-resistant signatures
  ├── handshake.py     VPN handshake protocol
  └── tunnel.py        Encrypted data tunnel

performance/           Performance evaluation
  └── benchmark.py     Benchmarking suite

tests/                 Unit tests (42 tests)
  ├── test_kyber.py
  ├── test_dilithium.py
  ├── test_handshake.py
  └── test_tunnel.py

examples/              Ready-to-run examples
  ├── demo.py         Full demonstration
  ├── simple_handshake.py  Minimal example
  └── tunnel_example.py    Tunnel usage
```

---

## Common Commands

### Run Full Demo
```bash
python examples/demo.py
```

### Run Simple Handshake Example
```bash
python examples/simple_handshake.py
```

### Run Tunnel Example
```bash
python examples/tunnel_example.py
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_handshake.py -v
```

### Run Tests with Coverage
```bash
pytest tests/ --cov=vpn_core --cov=performance
```

---

## Troubleshooting

### Error: "ImportError: No module named 'liboqs'"
**Solution:** Install liboqs-python:
```bash
pip install liboqs-python==0.9.0
```

### Error: "ModuleNotFoundError: No module named 'vpn_core'"
**Solution:** Make sure you're in the correct directory:
```bash
cd "Quantum-Safe VPN Simulation"
python examples/demo.py
```

### Tests failing with crypto errors
**Solution:** Reinstall cryptography package:
```bash
pip install --upgrade cryptography==41.0.7
```

---

## Next Steps

1. **Read Documentation**
   - `README.md` - Complete user guide
   - `ARCHITECTURE.md` - Technical details
   - `PROJECT_SUMMARY.md` - Project overview

2. **Explore Examples**
   - `examples/simple_handshake.py` - Minimal 50-line example
   - `examples/tunnel_example.py` - Encryption example
   - `examples/demo.py` - Full-featured demo

3. **Review Code**
   - Study `vpn_core/handshake.py` for protocol flow
   - Check `vpn_core/tunnel.py` for encryption details
   - See `performance/benchmark.py` for metrics

4. **Run Tests**
   - Understand implementation with `pytest tests/ -v`
   - Verify correctness with test cases
   - Check edge cases and error handling

5. **Extend Project**
   - Add TLS 1.3 integration
   - Implement hybrid PQC-classical mode
   - Optimize with hardware acceleration
   - Deploy to real network

---

## Key Takeaways

✅ **Quantum-Safe:** NIST-approved PQC algorithms protect against quantum attacks  
✅ **Tested:** 42 comprehensive unit tests ensure reliability  
✅ **Documented:** Complete API and architecture documentation  
✅ **Efficient:** Sub-10ms handshake, multi-Mbps throughput  
✅ **Secure:** Mutual authentication + data encryption + integrity verification  
✅ **6G Ready:** Designed for next-generation network requirements  

---

## Support

For issues or questions:
1. Check `README.md` FAQ section
2. Review test files for usage examples
3. Check ARCHITECTURE.md for technical details
4. Examine example code in `examples/` directory

---

**Enjoy exploring quantum-safe VPN technology!** 🚀

Last updated: December 2, 2025
