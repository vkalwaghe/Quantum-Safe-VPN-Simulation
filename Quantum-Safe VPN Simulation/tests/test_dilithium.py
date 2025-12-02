"""
Unit Tests for Dilithium Signature Module
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vpn_core import DilithiumSignature


class TestDilithiumSignature:
    """Test cases for Dilithium digital signatures"""
    
    @pytest.fixture
    def dilithium(self):
        """Create a Dilithium instance for testing"""
        return DilithiumSignature("2")
    
    def test_initialization(self, dilithium):
        """Test Dilithium initialization"""
        assert dilithium.security_level == "2"
        assert dilithium.algorithm == "Dilithium2"
    
    def test_keypair_generation(self, dilithium):
        """Test keypair generation"""
        public_key, secret_key = dilithium.generate_keypair()
        
        assert isinstance(public_key, bytes)
        assert isinstance(secret_key, bytes)
        assert len(public_key) > 0
        assert len(secret_key) > 0
    
    def test_signature_generation(self, dilithium):
        """Test signature generation"""
        public_key, secret_key = dilithium.generate_keypair()
        message = b"Test message"
        
        signature = dilithium.sign(message, secret_key)
        
        assert isinstance(signature, bytes)
        assert len(signature) > 0
        assert dilithium.signature_size == len(signature)
    
    def test_signature_verification(self, dilithium):
        """Test signature verification"""
        public_key, secret_key = dilithium.generate_keypair()
        message = b"Test message"
        
        signature = dilithium.sign(message, secret_key)
        is_valid = dilithium.verify(message, signature, public_key)
        
        assert is_valid is True
    
    def test_signature_verification_fails_on_tampering(self, dilithium):
        """Test that verification fails with tampered message"""
        public_key, secret_key = dilithium.generate_keypair()
        message = b"Test message"
        
        signature = dilithium.sign(message, secret_key)
        
        # Verify with original message
        assert dilithium.verify(message, signature, public_key) is True
        
        # Verify with tampered message
        tampered_message = b"Tampered message"
        assert dilithium.verify(tampered_message, signature, public_key) is False
    
    def test_signature_verification_fails_on_wrong_key(self, dilithium):
        """Test that verification fails with wrong public key"""
        public_key1, secret_key1 = dilithium.generate_keypair()
        public_key2, secret_key2 = dilithium.generate_keypair()
        message = b"Test message"
        
        signature = dilithium.sign(message, secret_key1)
        
        # Verify with correct public key
        assert dilithium.verify(message, signature, public_key1) is True
        
        # Verify with wrong public key
        assert dilithium.verify(message, signature, public_key2) is False
    
    def test_different_messages_different_signatures(self, dilithium):
        """Test that different messages produce different signatures"""
        public_key, secret_key = dilithium.generate_keypair()
        
        message1 = b"Message 1"
        message2 = b"Message 2"
        
        signature1 = dilithium.sign(message1, secret_key)
        signature2 = dilithium.sign(message2, secret_key)
        
        assert signature1 != signature2
    
    def test_metrics(self, dilithium):
        """Test metric collection"""
        dilithium.generate_keypair()
        dilithium.sign(b"test", dilithium.dilithium_secret)
        
        metrics = dilithium.get_metrics()
        
        assert "algorithm" in metrics
        assert metrics["algorithm"] == "Dilithium2"
        assert "public_key_size_bytes" in metrics
    
    def test_different_security_levels(self):
        """Test different Dilithium security levels"""
        for level in ["2", "3", "5"]:
            dilithium = DilithiumSignature(level)
            assert dilithium.security_level == level
            
            public_key, secret_key = dilithium.generate_keypair()
            assert len(public_key) > 0
            assert len(secret_key) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
