"""
Kyber Key Exchange Implementation
Post-Quantum Cryptography for quantum-resistant key establishment
"""

import os
from typing import Tuple, Dict, Any
try:
    from liboqs.kex import KeyEncapsulation
except ImportError:
    KeyEncapsulation = None

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class KyberKeyExchange:
    """
    Implements Kyber algorithm for post-quantum key establishment.
    Kyber is NIST-approved PQC standard for key encapsulation mechanism.
    """

    def __init__(self, security_level: str = "512"):
        """
        Initialize Kyber with specified security level.
        
        Args:
            security_level: "512", "768", or "1024"
                - 512: ~96 bits of post-quantum security
                - 768: ~192 bits of post-quantum security
                - 1024: ~256 bits of post-quantum security
        """
        self.security_level = security_level
        self.algorithm = f"Kyber{security_level}"
        
        if KeyEncapsulation is None:
            raise ImportError("liboqs-python not installed. Install with: pip install liboqs-python")
        
        # Initialize the key encapsulation mechanism
        self.kem = KeyEncapsulation(self.algorithm)
        
        # Metrics
        self.public_key_size = None
        self.secret_key_size = None
        self.ciphertext_size = None
        self.shared_secret_size = None

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate a Kyber keypair (public_key, secret_key).
        
        Returns:
            Tuple of (public_key_bytes, secret_key_bytes)
        """
        public_key, secret_key = self.kem.generate_keypair()
        
        # Store sizes for performance metrics
        self.public_key_size = len(public_key)
        self.secret_key_size = len(secret_key)
        
        return public_key, secret_key

    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Encapsulate a shared secret using the public key.
        Called by client to establish shared secret with server.
        
        Args:
            public_key: Server's Kyber public key
            
        Returns:
            Tuple of (ciphertext, shared_secret)
        """
        ciphertext, shared_secret = self.kem.encap_secret(public_key)
        
        # Store sizes
        self.ciphertext_size = len(ciphertext)
        self.shared_secret_size = len(shared_secret)
        
        return ciphertext, shared_secret

    def decapsulate(self, secret_key: bytes, ciphertext: bytes) -> bytes:
        """
        Decapsulate the ciphertext using the secret key.
        Called by server to recover shared secret.
        
        Args:
            secret_key: Server's Kyber secret key
            ciphertext: Client's encapsulated secret
            
        Returns:
            Shared secret matching client's secret
        """
        shared_secret = self.kem.decap_secret(secret_key, ciphertext)
        self.shared_secret_size = len(shared_secret)
        return shared_secret

    def derive_session_key(self, shared_secret: bytes, context: bytes = b"") -> bytes:
        """
        Derive a session key from the shared secret using KDF.
        
        Args:
            shared_secret: Raw shared secret from encapsulation
            context: Optional context for key derivation
            
        Returns:
            Derived 256-bit session key
        """
        # Use HKDF to derive a properly sized session key
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit session key
            salt=b"kyber-vpn-session",
            info=context,
        )
        
        return hkdf.derive(shared_secret)

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get key exchange metrics for performance analysis.
        
        Returns:
            Dictionary with size and algorithm metrics
        """
        return {
            "algorithm": self.algorithm,
            "security_level": self.security_level,
            "public_key_size_bytes": self.public_key_size,
            "secret_key_size_bytes": self.secret_key_size,
            "ciphertext_size_bytes": self.ciphertext_size,
            "shared_secret_size_bytes": self.shared_secret_size,
        }

    @staticmethod
    def compare_with_classical():
        """
        Compare Kyber metrics with classical RSA/ECDH.
        
        Returns:
            Dictionary comparing key sizes and security levels
        """
        return {
            "kyber512_public_key_bytes": 800,
            "rsa2048_public_key_bytes": 294,
            "ecdh_p256_public_key_bytes": 65,
            "kyber512_ciphertext_bytes": 768,
            "rsa2048_encrypted_secret_bytes": 256,
            "note": "Kyber has larger ciphertexts but provides quantum resistance"
        }
