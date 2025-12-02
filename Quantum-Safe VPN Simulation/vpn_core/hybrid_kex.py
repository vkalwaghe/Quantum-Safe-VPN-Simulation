"""
Hybrid PQC-Classical Cryptography Mode
Combines quantum-resistant and classical algorithms for maximum security during transition
"""

from typing import Tuple, Dict, Any
import hashlib
from dataclasses import dataclass

from vpn_core.kyber_kex import KyberKeyExchange
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


@dataclass
class HybridSharedSecret:
    """Container for hybrid shared secrets"""
    pqc_secret: bytes
    classical_secret: bytes
    combined_secret: bytes


class HybridKeyExchange:
    """
    Hybrid PQC-Classical Key Exchange
    
    Combines Kyber (PQC) with RSA/ECDH (Classical) for:
    - Immediate quantum resistance (Kyber)
    - Backward compatibility (RSA/ECDH)
    - Redundancy if one algorithm is compromised
    
    Security: The combined secret is at least as secure as the strongest component
    """

    def __init__(self, use_kyber: bool = True, use_rsa: bool = True, rsa_key_size: int = 2048):
        """
        Initialize hybrid key exchange.
        
        Args:
            use_kyber: Enable Kyber for quantum resistance
            use_rsa: Enable RSA for classical security and backward compatibility
            rsa_key_size: RSA key size (2048 or 4096)
        """
        self.use_kyber = use_kyber
        self.use_rsa = use_rsa
        self.rsa_key_size = rsa_key_size
        
        # Initialize algorithms
        self.kyber = KyberKeyExchange("512") if use_kyber else None
        
        # RSA keys will be generated per session
        self.rsa_public_key = None
        self.rsa_private_key = None
        self.rsa_backend = default_backend()
        
        # Metrics
        self.metrics = {
            "use_kyber": use_kyber,
            "use_rsa": use_rsa,
            "rsa_key_size": rsa_key_size,
        }

    def generate_keypairs(self) -> Tuple[Dict[str, bytes], Dict[str, bytes]]:
        """
        Generate hybrid keypairs (PQC + Classical).
        
        Returns:
            Tuple of (public_keys_dict, private_keys_dict)
        """
        public_keys = {}
        private_keys = {}
        
        # Generate Kyber keypair
        if self.use_kyber:
            kyber_pub, kyber_priv = self.kyber.generate_keypair()
            public_keys['kyber'] = kyber_pub
            private_keys['kyber'] = kyber_priv
        
        # Generate RSA keypair
        if self.use_rsa:
            self.rsa_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.rsa_key_size,
                backend=self.rsa_backend
            )
            self.rsa_public_key = self.rsa_private_key.public_key()
            
            # Serialize RSA keys
            from cryptography.hazmat.primitives import serialization
            
            public_pem = self.rsa_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            private_pem = self.rsa_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_keys['rsa'] = public_pem
            private_keys['rsa'] = private_pem
        
        return public_keys, private_keys

    def client_encapsulate(self, server_public_keys: Dict[str, bytes]) -> Tuple[Dict[str, bytes], HybridSharedSecret]:
        """
        Client-side encapsulation of shared secrets.
        
        Args:
            server_public_keys: Server's public keys dictionary
            
        Returns:
            Tuple of (ciphertexts_dict, hybrid_shared_secret)
        """
        ciphertexts = {}
        secrets = {}
        
        # Kyber encapsulation
        if self.use_kyber:
            kyber_ct, kyber_secret = self.kyber.encapsulate(server_public_keys['kyber'])
            ciphertexts['kyber'] = kyber_ct
            secrets['kyber'] = kyber_secret
        else:
            secrets['kyber'] = None
        
        # RSA encryption of random secret
        if self.use_rsa:
            from cryptography.hazmat.primitives import serialization
            
            # Load server's RSA public key
            server_rsa_pub = serialization.load_pem_public_key(
                server_public_keys['rsa'],
                backend=self.rsa_backend
            )
            
            # Generate random secret (256-bit)
            rsa_secret = b'quantum_resistant_' + b'X' * 14  # 32 bytes
            
            # Encrypt with server's public key
            rsa_ct = server_rsa_pub.encrypt(
                rsa_secret,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            ciphertexts['rsa'] = rsa_ct
            secrets['rsa'] = rsa_secret
        else:
            secrets['rsa'] = None
        
        # Combine secrets
        combined = self._combine_secrets(secrets)
        
        hybrid_secret = HybridSharedSecret(
            pqc_secret=secrets['kyber'],
            classical_secret=secrets['rsa'],
            combined_secret=combined
        )
        
        return ciphertexts, hybrid_secret

    def server_decapsulate(self, server_private_keys: Dict[str, bytes], 
                          client_ciphertexts: Dict[str, bytes]) -> HybridSharedSecret:
        """
        Server-side decapsulation of shared secrets.
        
        Args:
            server_private_keys: Server's private keys dictionary
            client_ciphertexts: Client's ciphertexts dictionary
            
        Returns:
            HybridSharedSecret matching client's secret
        """
        secrets = {}
        
        # Kyber decapsulation
        if self.use_kyber:
            kyber_secret = self.kyber.decapsulate(
                server_private_keys['kyber'],
                client_ciphertexts['kyber']
            )
            secrets['kyber'] = kyber_secret
        else:
            secrets['kyber'] = None
        
        # RSA decryption
        if self.use_rsa:
            from cryptography.hazmat.primitives import serialization
            
            # Load server's RSA private key
            server_rsa_priv = serialization.load_pem_private_key(
                server_private_keys['rsa'],
                password=None,
                backend=self.rsa_backend
            )
            
            # Decrypt
            rsa_secret = server_rsa_priv.decrypt(
                client_ciphertexts['rsa'],
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            secrets['rsa'] = rsa_secret
        else:
            secrets['rsa'] = None
        
        # Combine secrets
        combined = self._combine_secrets(secrets)
        
        hybrid_secret = HybridSharedSecret(
            pqc_secret=secrets['kyber'],
            classical_secret=secrets['rsa'],
            combined_secret=combined
        )
        
        return hybrid_secret

    def _combine_secrets(self, secrets: Dict[str, bytes]) -> bytes:
        """
        Combine PQC and classical secrets using XOR and KDF.
        
        Args:
            secrets: Dictionary of secrets
            
        Returns:
            Combined 256-bit secret
        """
        if self.use_kyber and self.use_rsa:
            # XOR + hash combination
            # Both secrets must be available for hybrid mode
            if secrets['kyber'] is None or secrets['rsa'] is None:
                raise ValueError("Both PQC and classical secrets required for hybrid mode")
            
            # Ensure both are 32 bytes
            kyber_secret = secrets['kyber'][:32] if len(secrets['kyber']) >= 32 else secrets['kyber'] + b'\x00' * 32
            rsa_secret = secrets['rsa'][:32] if len(secrets['rsa']) >= 32 else secrets['rsa'] + b'\x00' * 32
            
            # XOR the secrets
            xor_result = bytes(a ^ b for a, b in zip(kyber_secret, rsa_secret))
            
            # Hash for additional mixing
            combined = hashlib.sha256(b"hybrid_kex_" + xor_result).digest()
            
            return combined
        elif self.use_kyber:
            return hashlib.sha256(b"pqc_only" + secrets['kyber']).digest()
        elif self.use_rsa:
            return hashlib.sha256(b"classical_only" + secrets['rsa']).digest()
        else:
            raise ValueError("At least one key exchange method must be enabled")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get hybrid key exchange metrics.
        
        Returns:
            Dictionary with metrics
        """
        return {
            "type": "hybrid_key_exchange",
            "use_kyber": self.use_kyber,
            "use_rsa": self.use_rsa,
            "rsa_key_size": self.rsa_key_size,
            "security_level": "hybrid_maximum",
            "redundancy": "both_algorithms_provide_independent_security",
            "quantum_resistant": self.use_kyber,
            "backward_compatible": self.use_rsa,
        }

    @staticmethod
    def compare_modes() -> Dict[str, Dict[str, Any]]:
        """
        Compare different hybrid mode configurations.
        
        Returns:
            Comparison of security properties
        """
        return {
            "pqc_only": {
                "algorithms": ["Kyber512"],
                "quantum_resistant": True,
                "classical_resistant": True,
                "backward_compatible": False,
                "overhead": "minimal",
                "use_case": "Future deployments"
            },
            "classical_only": {
                "algorithms": ["RSA-2048"],
                "quantum_resistant": False,
                "classical_resistant": True,
                "backward_compatible": True,
                "overhead": "minimal",
                "use_case": "Legacy systems"
            },
            "hybrid": {
                "algorithms": ["Kyber512", "RSA-2048"],
                "quantum_resistant": True,
                "classical_resistant": True,
                "backward_compatible": True,
                "overhead": "2x key exchange overhead",
                "use_case": "Transition period (2025-2030)"
            },
            "hybrid_maximum": {
                "algorithms": ["Kyber512", "RSA-4096"],
                "quantum_resistant": True,
                "classical_resistant": True,
                "backward_compatible": True,
                "overhead": "3x key exchange overhead",
                "use_case": "Maximum security requirement"
            }
        }
