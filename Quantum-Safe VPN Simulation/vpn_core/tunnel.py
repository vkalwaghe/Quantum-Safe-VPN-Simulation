"""
Encrypted Tunnel Implementation
PQC-based encrypted data transmission
"""

import os
import time
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
import struct

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend


@dataclass
class EncryptedPacket:
    """Represents an encrypted VPN packet"""
    packet_id: int
    iv: bytes
    ciphertext: bytes
    tag: bytes
    
    def to_bytes(self) -> bytes:
        """Serialize packet to bytes"""
        # Format: packet_id (4) | iv_len (1) | iv | tag_len (1) | tag | ciphertext_len (4) | ciphertext
        data = struct.pack('>I', self.packet_id)
        data += struct.pack('B', len(self.iv))
        data += self.iv
        data += struct.pack('B', len(self.tag))
        data += self.tag
        data += struct.pack('>I', len(self.ciphertext))
        data += self.ciphertext
        return data
    
    @staticmethod
    def from_bytes(data: bytes) -> 'EncryptedPacket':
        """Deserialize packet from bytes"""
        offset = 0
        packet_id = struct.unpack('>I', data[offset:offset+4])[0]
        offset += 4
        
        iv_len = struct.unpack('B', data[offset:offset+1])[0]
        offset += 1
        iv = data[offset:offset+iv_len]
        offset += iv_len
        
        tag_len = struct.unpack('B', data[offset:offset+1])[0]
        offset += 1
        tag = data[offset:offset+tag_len]
        offset += tag_len
        
        ciphertext_len = struct.unpack('>I', data[offset:offset+4])[0]
        offset += 4
        ciphertext = data[offset:offset+ciphertext_len]
        
        return EncryptedPacket(packet_id, iv, ciphertext, tag)


class EncryptedTunnel:
    """
    AES-256-GCM based encrypted tunnel for VPN communication.
    Uses session key derived from PQC key exchange.
    """

    def __init__(self, session_key: bytes, tunnel_id: str = "tunnel-0"):
        """
        Initialize encrypted tunnel.
        
        Args:
            session_key: 256-bit session key from PQC handshake
            tunnel_id: Identifier for this tunnel
        """
        if len(session_key) != 32:
            raise ValueError("Session key must be 256 bits (32 bytes)")
        
        self.session_key = session_key
        self.tunnel_id = tunnel_id
        
        # Derive separate keys for encryption and HMAC
        self.encryption_key = self._derive_key(b"encryption")
        self.iv_seed = self._derive_key(b"iv")
        
        # Packet tracking
        self.packet_counter = 0
        self.packets_sent = 0
        self.packets_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        
        # Performance metrics
        self.start_time = time.time()
        self.encryption_times = []
        self.decryption_times = []

    def _derive_key(self, context: bytes) -> bytes:
        """
        Derive a key from the session key using HKDF.
        
        Args:
            context: Context information for key derivation
            
        Returns:
            32-byte derived key
        """
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"vpn-tunnel",
            info=context,
            backend=default_backend()
        )
        return hkdf.derive(self.session_key)

    def _generate_iv(self) -> bytes:
        """
        Generate a unique IV for each encryption operation.
        Uses counter-based IV for determinism and uniqueness.
        
        Returns:
            12-byte IV for AES-GCM
        """
        # Combine counter and random component
        counter_bytes = struct.pack('>Q', self.packet_counter)
        random_bytes = os.urandom(4)
        iv = counter_bytes + random_bytes  # 12 bytes total
        self.packet_counter += 1
        return iv

    def encrypt(self, plaintext: bytes, additional_authenticated_data: bytes = b"") -> EncryptedPacket:
        """
        Encrypt data using AES-256-GCM.
        
        Args:
            plaintext: Data to encrypt
            additional_authenticated_data: Optional AAD for authentication
            
        Returns:
            EncryptedPacket with ciphertext and authentication tag
        """
        start_time = time.time()
        
        iv = self._generate_iv()
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        
        # Add AAD if provided
        if additional_authenticated_data:
            encryptor.authenticate_additional_data(additional_authenticated_data)
        
        # Encrypt
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        tag = encryptor.tag
        
        # Track metrics
        elapsed = time.time() - start_time
        self.encryption_times.append(elapsed)
        self.packets_sent += 1
        self.bytes_sent += len(plaintext)
        
        return EncryptedPacket(
            packet_id=self.packet_counter - 1,
            iv=iv,
            ciphertext=ciphertext,
            tag=tag
        )

    def decrypt(self, packet: EncryptedPacket, additional_authenticated_data: bytes = b"") -> bytes:
        """
        Decrypt data using AES-256-GCM.
        
        Args:
            packet: EncryptedPacket to decrypt
            additional_authenticated_data: Optional AAD for verification
            
        Returns:
            Decrypted plaintext
            
        Raises:
            cryptography.exceptions.InvalidTag if authentication fails
        """
        start_time = time.time()
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.GCM(packet.iv, packet.tag),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        
        # Add AAD if provided
        if additional_authenticated_data:
            decryptor.authenticate_additional_data(additional_authenticated_data)
        
        # Decrypt
        plaintext = decryptor.update(packet.ciphertext) + decryptor.finalize()
        
        # Track metrics
        elapsed = time.time() - start_time
        self.decryption_times.append(elapsed)
        self.packets_received += 1
        self.bytes_received += len(plaintext)
        
        return plaintext

    def get_tunnel_metrics(self) -> Dict[str, Any]:
        """
        Get tunnel performance metrics.
        
        Returns:
            Dictionary with encryption/decryption statistics
        """
        elapsed_time = time.time() - self.start_time
        
        avg_encryption_time = (
            sum(self.encryption_times) / len(self.encryption_times)
            if self.encryption_times else 0
        )
        avg_decryption_time = (
            sum(self.decryption_times) / len(self.decryption_times)
            if self.decryption_times else 0
        )
        
        return {
            "tunnel_id": self.tunnel_id,
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "avg_encryption_time_ms": avg_encryption_time * 1000,
            "avg_decryption_time_ms": avg_decryption_time * 1000,
            "total_encryption_time_ms": sum(self.encryption_times) * 1000,
            "total_decryption_time_ms": sum(self.decryption_times) * 1000,
            "elapsed_time_seconds": elapsed_time,
            "throughput_mbps": (self.bytes_sent + self.bytes_received) * 8 / (elapsed_time * 1e6) if elapsed_time > 0 else 0,
        }
