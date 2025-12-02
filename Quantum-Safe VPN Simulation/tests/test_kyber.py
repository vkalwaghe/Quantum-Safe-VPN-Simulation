"""
Unit Tests for Kyber Key Exchange Module
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vpn_core import KyberKeyExchange


class TestKyberKeyExchange:
    """Test cases for Kyber key exchange"""
    
    @pytest.fixture
    def kyber(self):
        """Create a Kyber instance for testing"""
        return KyberKeyExchange("512")
    
    def test_initialization(self, kyber):
        """Test Kyber initialization"""
        assert kyber.security_level == "512"
        assert kyber.algorithm == "Kyber512"
    
    def test_keypair_generation(self, kyber):
        """Test keypair generation"""
        public_key, secret_key = kyber.generate_keypair()
        
        assert isinstance(public_key, bytes)
        assert isinstance(secret_key, bytes)
        assert len(public_key) > 0
        assert len(secret_key) > 0
        assert kyber.public_key_size == len(public_key)
        assert kyber.secret_key_size == len(secret_key)
    
    def test_multiple_keypair_generation(self, kyber):
        """Test that multiple keypair generations produce different keys"""
        pk1, sk1 = kyber.generate_keypair()
        pk2, sk2 = kyber.generate_keypair()
        
        # Keys should be different
        assert pk1 != pk2
        assert sk1 != sk2
    
    def test_encapsulation_decapsulation(self, kyber):
        """Test encapsulation and decapsulation"""
        # Server side
        server_public, server_secret = kyber.generate_keypair()
        
        # Client side
        client_kyber = KyberKeyExchange("512")
        ciphertext, client_shared = client_kyber.encapsulate(server_public)
        
        # Server side decapsulation
        server_shared = kyber.decapsulate(server_secret, ciphertext)
        
        # Shared secrets should match
        assert client_shared == server_shared
        assert len(client_shared) == len(server_shared)
    
    def test_session_key_derivation(self, kyber):
        """Test session key derivation"""
        shared_secret = b"test_shared_secret_" + b"0" * 32
        
        session_key1 = kyber.derive_session_key(shared_secret, b"context1")
        session_key2 = kyber.derive_session_key(shared_secret, b"context1")
        session_key3 = kyber.derive_session_key(shared_secret, b"context2")
        
        # Same context should produce same key
        assert session_key1 == session_key2
        
        # Different context should produce different key
        assert session_key1 != session_key3
        
        # Session key should be 32 bytes (256-bit)
        assert len(session_key1) == 32
    
    def test_metrics(self, kyber):
        """Test metric collection"""
        kyber.generate_keypair()
        metrics = kyber.get_metrics()
        
        assert "algorithm" in metrics
        assert metrics["algorithm"] == "Kyber512"
        assert "public_key_size_bytes" in metrics
        assert metrics["public_key_size_bytes"] > 0
    
    def test_different_security_levels(self):
        """Test different Kyber security levels"""
        for level in ["512", "768", "1024"]:
            kyber = KyberKeyExchange(level)
            assert kyber.security_level == level
            
            public_key, secret_key = kyber.generate_keypair()
            assert len(public_key) > 0
            assert len(secret_key) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
