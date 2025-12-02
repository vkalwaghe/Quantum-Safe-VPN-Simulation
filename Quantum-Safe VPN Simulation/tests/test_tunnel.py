"""
Unit Tests for Encrypted Tunnel Module
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vpn_core import EncryptedTunnel, EncryptedPacket


class TestEncryptedTunnel:
    """Test cases for encrypted tunnel"""
    
    @pytest.fixture
    def session_key(self):
        """Create a session key for testing"""
        return b'0123456789ABCDEF0123456789ABCDEF'  # 32 bytes
    
    @pytest.fixture
    def tunnel(self, session_key):
        """Create a tunnel instance for testing"""
        return EncryptedTunnel(session_key, tunnel_id="test-tunnel")
    
    def test_initialization(self, session_key):
        """Test tunnel initialization"""
        tunnel = EncryptedTunnel(session_key, tunnel_id="test-tunnel-1")
        
        assert tunnel.session_key == session_key
        assert tunnel.tunnel_id == "test-tunnel-1"
        assert tunnel.packet_counter == 0
        assert tunnel.packets_sent == 0
        assert tunnel.packets_received == 0
    
    def test_invalid_session_key(self):
        """Test that invalid session key is rejected"""
        with pytest.raises(ValueError):
            EncryptedTunnel(b'short_key')
    
    def test_encryption_decryption(self, tunnel):
        """Test basic encryption and decryption"""
        plaintext = b"Test message"
        
        encrypted_packet = tunnel.encrypt(plaintext)
        decrypted = tunnel.decrypt(encrypted_packet)
        
        assert decrypted == plaintext
    
    def test_multiple_messages(self, tunnel):
        """Test encrypting and decrypting multiple messages"""
        messages = [
            b"First message",
            b"Second message",
            b"Third message",
            b"X" * 1000,
        ]
        
        for message in messages:
            encrypted = tunnel.encrypt(message)
            decrypted = tunnel.decrypt(encrypted)
            assert decrypted == message
    
    def test_unique_ivs(self, tunnel):
        """Test that each encryption uses a unique IV"""
        message = b"Test message"
        
        packet1 = tunnel.encrypt(message)
        packet2 = tunnel.encrypt(message)
        
        # IVs should be different
        assert packet1.iv != packet2.iv
        
        # But messages decrypt to the same plaintext
        assert tunnel.decrypt(packet1) == message
        assert tunnel.decrypt(packet2) == message
    
    def test_packet_counter(self, tunnel):
        """Test packet ID counter"""
        message = b"Test"
        
        packet1 = tunnel.encrypt(message)
        packet2 = tunnel.encrypt(message)
        packet3 = tunnel.encrypt(message)
        
        assert packet1.packet_id == 0
        assert packet2.packet_id == 1
        assert packet3.packet_id == 2
    
    def test_packet_serialization(self, tunnel):
        """Test packet serialization and deserialization"""
        message = b"Test message"
        
        packet1 = tunnel.encrypt(message)
        
        # Serialize
        data = packet1.to_bytes()
        assert isinstance(data, bytes)
        
        # Deserialize
        packet2 = EncryptedPacket.from_bytes(data)
        
        assert packet2.packet_id == packet1.packet_id
        assert packet2.iv == packet1.iv
        assert packet2.ciphertext == packet1.ciphertext
        assert packet2.tag == packet1.tag
        
        # Should decrypt to same plaintext
        decrypted = tunnel.decrypt(packet2)
        assert decrypted == message
    
    def test_aead_with_additional_data(self, tunnel):
        """Test AEAD with additional authenticated data"""
        message = b"Secret message"
        aad = b"Header information"
        
        packet = tunnel.encrypt(message, aad)
        decrypted = tunnel.decrypt(packet, aad)
        
        assert decrypted == message
    
    def test_authentication_failure_on_tampering(self, tunnel):
        """Test that tampering is detected"""
        message = b"Test message"
        
        packet = tunnel.encrypt(message)
        
        # Tamper with ciphertext
        tampered_packet = EncryptedPacket(
            packet_id=packet.packet_id,
            iv=packet.iv,
            ciphertext=bytes([packet.ciphertext[0] ^ 1]) + packet.ciphertext[1:],
            tag=packet.tag
        )
        
        # Decryption should fail
        with pytest.raises(Exception):
            tunnel.decrypt(tampered_packet)
    
    def test_metrics_tracking(self, tunnel):
        """Test metrics tracking"""
        message1 = b"Message 1"
        message2 = b"X" * 1000
        
        tunnel.encrypt(message1)
        tunnel.encrypt(message2)
        tunnel.decrypt(tunnel.encrypt(message1))
        tunnel.decrypt(tunnel.encrypt(message2))
        
        metrics = tunnel.get_tunnel_metrics()
        
        assert metrics["packets_sent"] == 4
        assert metrics["packets_received"] == 2
        assert metrics["bytes_sent"] == len(message1) + len(message2) + len(message1) + len(message2)
        assert metrics["avg_encryption_time_ms"] > 0
        assert metrics["avg_decryption_time_ms"] > 0
    
    def test_large_message(self, tunnel):
        """Test encryption of large messages"""
        large_message = b"X" * (1024 * 1024)  # 1MB
        
        packet = tunnel.encrypt(large_message)
        decrypted = tunnel.decrypt(packet)
        
        assert decrypted == large_message
    
    def test_different_session_keys(self, session_key):
        """Test that different session keys produce different ciphertexts"""
        tunnel1 = EncryptedTunnel(session_key, tunnel_id="tunnel-1")
        tunnel2 = EncryptedTunnel(b'different_key_' + session_key[14:], tunnel_id="tunnel-2")
        
        message = b"Same message"
        
        packet1 = tunnel1.encrypt(message)
        packet2 = tunnel2.encrypt(message)
        
        # Ciphertexts should be different
        assert packet1.ciphertext != packet2.ciphertext
        
        # But each should decrypt with its own key
        assert tunnel1.decrypt(packet1) == message
        assert tunnel2.decrypt(packet2) == message
    
    def test_throughput_calculation(self, tunnel):
        """Test throughput metric calculation"""
        # Encrypt 100KB of data
        message = b"X" * (100 * 1024)
        
        for _ in range(5):
            tunnel.encrypt(message)
        
        metrics = tunnel.get_tunnel_metrics()
        
        assert metrics["throughput_mbps"] > 0
        assert "elapsed_time_seconds" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
