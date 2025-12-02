"""
Dilithium Digital Signature Implementation
Post-Quantum Cryptography for quantum-resistant authentication
"""

from typing import Tuple, Dict, Any
try:
    from liboqs.sig import Signature
except ImportError:
    Signature = None


class DilithiumSignature:
    """
    Implements Dilithium algorithm for post-quantum digital signatures.
    Dilithium is NIST-approved PQC standard for digital signatures.
    """

    def __init__(self, security_level: str = "2"):
        """
        Initialize Dilithium with specified security level.
        
        Args:
            security_level: "2", "3", or "5"
                - 2: ~128 bits of post-quantum security
                - 3: ~192 bits of post-quantum security
                - 5: ~256 bits of post-quantum security
        """
        self.security_level = security_level
        self.algorithm = f"Dilithium{security_level}"
        
        if Signature is None:
            raise ImportError("liboqs-python not installed. Install with: pip install liboqs-python")
        
        # Initialize the signature scheme
        self.sig = Signature(self.algorithm)
        
        # Metrics
        self.public_key_size = None
        self.secret_key_size = None
        self.signature_size = None

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate a Dilithium keypair (public_key, secret_key).
        
        Returns:
            Tuple of (public_key_bytes, secret_key_bytes)
        """
        public_key, secret_key = self.sig.generate_keypair()
        
        # Store sizes for performance metrics
        self.public_key_size = len(public_key)
        self.secret_key_size = len(secret_key)
        
        return public_key, secret_key

    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        """
        Create a digital signature for a message.
        
        Args:
            message: Data to sign
            secret_key: Dilithium secret key
            
        Returns:
            Digital signature bytes
        """
        signature = self.sig.sign(message, secret_key)
        self.signature_size = len(signature)
        return signature

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Verify a digital signature.
        
        Args:
            message: Original signed data
            signature: Signature to verify
            public_key: Dilithium public key
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            self.sig.verify(message, signature, public_key)
            return True
        except Exception:
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get signature metrics for performance analysis.
        
        Returns:
            Dictionary with size and algorithm metrics
        """
        return {
            "algorithm": self.algorithm,
            "security_level": self.security_level,
            "public_key_size_bytes": self.public_key_size,
            "secret_key_size_bytes": self.secret_key_size,
            "signature_size_bytes": self.signature_size,
        }

    @staticmethod
    def compare_with_classical():
        """
        Compare Dilithium metrics with classical RSA/ECDSA.
        
        Returns:
            Dictionary comparing signature sizes and security levels
        """
        return {
            "dilithium2_public_key_bytes": 1312,
            "rsa2048_public_key_bytes": 294,
            "ecdsa_p256_public_key_bytes": 91,
            "dilithium2_signature_bytes": 2420,
            "rsa2048_signature_bytes": 256,
            "ecdsa_p256_signature_bytes": 71,
            "note": "Dilithium signatures are larger but quantum-resistant"
        }
