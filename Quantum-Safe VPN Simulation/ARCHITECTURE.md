# Quantum-Safe VPN Architecture

## Overview

The Quantum-Safe VPN Simulation implements a complete post-quantum cryptography (PQC) enabled VPN system designed for 6G-era cybersecurity. It replaces classical cryptographic algorithms with NIST-standardized quantum-resistant alternatives.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  (VPN Client/Server Applications, User Applications)     │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────┐
│                 Protocol Layer                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │     Handshake Protocol (PQC-Based)              │   │
│  │  • ClientHello / ServerHello messages            │   │
│  │  • Dilithium authentication                      │   │
│  │  • Kyber key exchange                            │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │     Tunnel Protocol (Data Transmission)          │   │
│  │  • Encrypted packet format                       │   │
│  │  • AES-256-GCM encryption                        │   │
│  │  • Per-packet authentication                     │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────┐
│              Cryptography Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐   │
│  │   Kyber      │  │  Dilithium   │  │   AES-256   │   │
│  │   (KEM)      │  │  (Signature) │  │    (AEAD)   │   │
│  └──────────────┘  └──────────────┘  └─────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────┐
│            Library Layer                                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  liboqs-python: NIST PQC algorithms              │   │
│  │  cryptography: Modern crypto operations          │   │
│  │  Python standard library                         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Module Architecture

### Core VPN Modules (`vpn_core/`)

#### 1. Kyber Key Exchange (`kyber_kex.py`)

**Purpose:** Post-quantum key encapsulation mechanism

**Key Components:**
- `KyberKeyExchange` class
  - Security levels: 512, 768, 1024 bits
  - Methods:
    - `generate_keypair()`: Generate public/secret keys
    - `encapsulate()`: Encapsulate shared secret (client-side)
    - `decapsulate()`: Decapsulate shared secret (server-side)
    - `derive_session_key()`: KDF for session key
  - Metrics: Key sizes, algorithm parameters

**Security Properties:**
- Lattice-based cryptography (module lattice problem)
- Indistinguishable from uniform random samples
- Resistant to known quantum attacks
- NIST SP 800-227 compliant

**Data Flow:**
```
Client                              Server
  │                                   │
  ├──────── get server_pk ──────────> │
  │                                   │
  ├─ encapsulate(server_pk) ─────────> │
  │   └─ ciphertext, shared_secret     │
  │                                   │
  │ <─ decapsulate(ciphertext) ───────┤
  │    └─ matched shared_secret        │
```

#### 2. Dilithium Digital Signatures (`dilithium_sig.py`)

**Purpose:** Post-quantum authentication and message integrity

**Key Components:**
- `DilithiumSignature` class
  - Security levels: 2, 3, 5
  - Methods:
    - `generate_keypair()`: Generate public/secret keys
    - `sign()`: Create digital signature
    - `verify()`: Verify digital signature
  - Metrics: Signature sizes, key sizes

**Security Properties:**
- Lattice-based cryptography (fiat-shamir with aborts)
- Deterministic signing (no randomness required)
- Proven security under hardness assumptions
- NIST SP 800-227 compliant

**Data Flow:**
```
Signer                              Verifier
  │                                   │
  ├──────── message, sk ─────────────> │
  │                                   │
  ├─ signature = sign(msg, sk) ──────> │
  │                                   │
  │ <─ verify(msg, sig, pk) ──────────┤
  │    └─ True/False                   │
```

#### 3. Handshake Protocol (`handshake.py`)

**Purpose:** Quantum-resistant authentication and key agreement

**Key Components:**
- `PQCHandshake` class: Manages handshake state machine
- `ClientHello`: Initial client message
- `ServerHello`: Server response with key encapsulation
- State machine: INITIAL → CLIENT_HELLO_SENT → SERVER_HELLO_SENT → ... → COMPLETED

**Handshake Flow (4-Phase):**

```
Phase 1: ClientHello
────────────────────
Client generates keypair (Kyber, Dilithium)
  └─> Sends public keys to Server

Phase 2: ServerHello
────────────────────
Server generates keypair (Kyber, Dilithium)
Server encapsulates shared secret with client's Kyber public key
  └─> Sends ciphertext + own public keys

Phase 3: ClientFinished
─────────────────────
Client decapsulates shared secret
Client signs server's Kyber public key with Dilithium
  └─> Sends signature to Server

Phase 4: ServerFinished
──────────────────────
Server verifies client's signature
Server signs client's Kyber public key with Dilithium
  └─> Sends signature to Client

Final: Both derive session key from shared secret
Session key = KDF(shared_secret || handshake_context)
```

**Message Sizes (512-bit Kyber, Level-2 Dilithium):**
- ClientHello: ~1900 bytes (Kyber PK: 800B + Dilithium PK: 1312B)
- ServerHello: ~3500 bytes (+ ciphertext: 768B)
- ClientFinished: ~2420 bytes (Dilithium signature)
- ServerFinished: ~2420 bytes (Dilithium signature)
- **Total: ~10,240 bytes**

#### 4. Encrypted Tunnel (`tunnel.py`)

**Purpose:** Secure data transmission with confidentiality and integrity

**Key Components:**
- `EncryptedTunnel` class
- `EncryptedPacket` class: Serialized packet format
- Encryption: AES-256-GCM
- Key derivation: HKDF for per-packet keys
- IV management: Counter + random component

**Encryption Operations:**

```
Encryption:
──────────
1. Generate unique IV (counter + random)
2. Derive encryption key from session key
3. AES-256-GCM(plaintext, key=derived_key, iv=IV)
4. Output: ciphertext || tag

Decryption:
──────────
1. Retrieve IV from packet
2. Derive encryption key from session key
3. AES-256-GCM.verify(tag)  // Authenticate first
4. AES-256-GCM.decrypt(ciphertext)
5. Output: plaintext or AUTHENTICATION_FAILURE
```

**Packet Format:**
```
Offset  | Size | Field          | Description
--------|------|----------------|----------------------------
0       | 4    | Packet ID      | Sequential packet counter
4       | 1    | IV Length      | Length of IV (typically 12)
5       | 12   | IV             | Initialization vector
17      | 1    | Tag Length     | Length of auth tag (16)
18      | 16   | Tag            | AES-GCM authentication tag
34      | 4    | Ciphertext Len | Length of ciphertext
38      | N    | Ciphertext     | Encrypted payload
```

### Performance Module (`performance/`)

#### Benchmark Suite (`benchmark.py`)

**Purpose:** Performance evaluation and comparison

**Components:**
- `PerformanceBenchmark` class
- `PerformanceResult` class: Benchmark result container

**Benchmarks:**
1. Kyber operations (KeyGen, Encap, Decap)
2. Dilithium operations (KeyGen, Sign, Verify)
3. Full handshake
4. Tunnel encryption/decryption
5. Comparison with classical algorithms

**Metrics:**
- Execution time (min, max, avg, std dev)
- Key/signature/ciphertext sizes
- Throughput (Mbps)
- Handshake latency

**Benchmark Results (Example - 512-bit Kyber, Level-2 Dilithium):**

| Operation | Time (ms) | Iterations |
|-----------|-----------|-----------|
| Kyber KeyGen | 1.2 | 10 |
| Kyber Encapsulate | 0.5 | 10 |
| Kyber Decapsulate | 0.6 | 10 |
| Dilithium KeyGen | 2.1 | 10 |
| Dilithium Sign | 1.4 | 10 |
| Dilithium Verify | 3.2 | 10 |
| AES-256-GCM (100KB) | 2.3 | 10 |
| Full Handshake | 8.5 | 5 |

## Data Flow Architecture

### Handshake Sequence

```
┌────────────┐                          ┌────────────┐
│   Client   │                          │   Server   │
└────────────┘                          └────────────┘
      │                                        │
      │ ─────── ClientHello (1.9KB) ────────> │
      │                                        │
      │  Generate Kyber           Generate    │
      │  Generate Dilithium       Kyber key   │
      │                           Encapsulate │
      │                                        │
      │ <────── ServerHello (3.5KB) ─────────│
      │  Extract Kyber PK    + Ciphertext     │
      │                                        │
      │  Decapsulate                           │
      │  Shared secret ──────────────────────> │
      │  Sign server PK                        │
      │                                        │
      │ ─────── ClientFinished (2.4KB) ─────>│
      │                                Verify │
      │                                Sign   │
      │ <────── ServerFinished (2.4KB) ──────│
      │                                Verify │
      │                                        │
      │ ══════════════════════════════════════│
      │    Tunnel Ready - Session Key Ready    │
      │ ══════════════════════════════════════│
```

### Tunnel Operation Sequence

```
Client Application          VPN Client Tunnel      VPN Server Tunnel       Server Application
        │                          │                        │                        │
        ├─ "Data to send" ───────> │                        │                        │
        │                          │                        │                        │
        │               Encrypt(data, session_key)          │                        │
        │                  ├─ Generate IV                   │                        │
        │                  ├─ AES-256-GCM                   │                        │
        │                  ├─ Generate Tag                  │                        │
        │                  │                                │                        │
        │                  ├──────[Encrypted Packet]───────>│                        │
        │                          │                        │                        │
        │                          │            Decrypt(packet, session_key)         │
        │                          │                  ├─ Verify Tag                 │
        │                          │                  ├─ AES-256-GCM                │
        │                          │                  ├─ Extract plaintext          │
        │                          │                        │                        │
        │                          │                        ├─────── "Data" ───────>│
        │                          │                        │                        │
```

## Security Model

### Threat Model

**Adversary Capabilities:**
- Can intercept all network traffic
- Can modify packets in transit
- Cannot break NIST standardized PQC algorithms
- Quantum computer available (future threat)

**Protected Against:**
1. **Passive eavesdropping:** All data encrypted with AES-256-GCM
2. **Man-in-the-middle:** Dilithium signatures authenticate peers
3. **Quantum attacks:** Kyber/Dilithium quantum-resistant
4. **Replay attacks:** Per-packet IV and counter mechanism
5. **Tampering:** AEAD provides integrity verification

### Security Properties

**Handshake:**
- Mutual authentication via Dilithium signatures
- Shared secret establishment via Kyber
- Forward secrecy (if ephemeral keys used)
- Identity authentication

**Tunnel:**
- **Confidentiality:** AES-256-GCM encryption
- **Integrity:** GCM authentication tag
- **Authenticity:** Derived from authenticated handshake
- **Non-repudiation:** Dilithium signatures

## Performance Characteristics

### Computational Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Kyber KeyGen | O(n²) | Polynomial multiplication |
| Kyber Encap/Decap | O(n²) | Polynomial + compression |
| Dilithium KeyGen | O(n²) | Matrix sampling |
| Dilithium Sign | O(n) | Rejection sampling (avg) |
| Dilithium Verify | O(n²) | Polynomial arithmetic |
| AES-256-GCM | O(n) | Linear in data size |

### Memory Usage

| Component | Memory |
|-----------|--------|
| Kyber512 | ~2.3 KB (keypairs) |
| Dilithium2 | ~4.4 KB (keypairs) |
| Session key | 32 bytes |
| Tunnel state | ~1 KB (IV seeds, counters) |

### Bandwidth

| Message | Size | Overhead |
|---------|------|----------|
| ClientHello | 1.9 KB | Initial handshake |
| ServerHello | 3.5 KB | Initial handshake |
| Data packet (100 bytes) | 116 bytes | 16% overhead (IV+tag) |
| Data packet (10 KB) | 10.032 KB | 0.3% overhead |

## 6G Integration

### 6G Requirements Met

✓ **Quantum-Resistance:** NIST-standardized PQC algorithms  
✓ **Performance:** Sub-10ms handshake, <3ms encryption per packet  
✓ **Scalability:** Stateless encryption, minimal per-connection memory  
✓ **Interoperability:** Standard algorithms, clear protocol definition  
✓ **Security Longevity:** 20+ year forward secrecy  

### 6G Deployment Scenarios

1. **Core Network Security**
   - PQC for backbone infrastructure
   - Hybrid PQC-classical for transition

2. **Edge-to-Edge Communication**
   - VPN tunnels between edge nodes
   - Quantum-resistant microgrid security

3. **IoT Device Protection**
   - Lightweight PQC variants (future)
   - Secure device-to-gateway tunneling

4. **Service Mesh**
   - PQC in service-to-service authentication
   - Zero-trust network architecture

## Extensibility

### Future Enhancements

1. **Additional PQC Algorithms**
   - SPHINCS+ for stateless signatures
   - BIKE/HQC for alternative KEMs
   - CRYSTALS-Kyber variants

2. **Protocol Extensions**
   - TLS 1.3 integration
   - IKEv2 PQC support
   - Custom protocol variants

3. **Performance Optimization**
   - Hardware acceleration (SIMD, GPU)
   - Hybrid PQC-classical modes
   - Caching and precomputation

4. **Network Features**
   - Multi-path routing
   - Congestion control
   - QoS guarantees

## References

1. **NIST PQC Standardization:** SP 800-227
2. **Kyber Specification:** Module-Lattice-Based KEM
3. **Dilithium Specification:** Lattice-Based Digital Signature
4. **6G Vision:** IEEE 6G Initiative, NIST 6G Research
5. **Cryptographic Standards:** FIPS 140-3, SP 800-175B

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Status:** Reference Architecture
