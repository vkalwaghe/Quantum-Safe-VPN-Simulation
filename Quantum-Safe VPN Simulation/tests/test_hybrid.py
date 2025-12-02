"""
Unit Tests for Hybrid Key Exchange Module
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vpn_core.hybrid_kex import HybridKeyExchange, HybridSharedSecret


class TestHybridKeyExchange:
    """Test cases for hybrid key exchange"""
    
    def test_hybrid_pqc_rsa(self):
        """Test full hybrid mode (Kyber + RSA)"""
        # Server setup
        server = HybridKeyExchange(use_kyber=True, use_rsa=True, rsa_key_size=2048)
        server_public, server_private = server.generate_keypairs()
        
        assert 'kyber' in server_public
        assert 'rsa' in server_public
        
        # Client encapsulation
        client = HybridKeyExchange(use_kyber=True, use_rsa=True, rsa_key_size=2048)
        ciphertexts, client_secret = client.client_encapsulate(server_public)
        
        assert 'kyber' in ciphertexts
        assert 'rsa' in ciphertexts
        assert isinstance(client_secret, HybridSharedSecret)
        assert client_secret.combined_secret is not None
        
        # Server decapsulation
        server_secret = server.server_decapsulate(server_private, ciphertexts)
        
        # Verify
        assert client_secret.combined_secret == server_secret.combined_secret
        assert len(client_secret.combined_secret) == 32  # 256-bit
    
    def test_pqc_only_mode(self):
        """Test PQC-only mode (Kyber only)"""
        server = HybridKeyExchange(use_kyber=True, use_rsa=False)
        server_public, server_private = server.generate_keypairs()
        
        assert 'kyber' in server_public
        assert 'rsa' not in server_public
        
        client = HybridKeyExchange(use_kyber=True, use_rsa=False)
        ciphertexts, client_secret = client.client_encapsulate(server_public)
        
        server_secret = server.server_decapsulate(server_private, ciphertexts)
        
        assert client_secret.combined_secret == server_secret.combined_secret
    
    def test_classical_only_mode(self):
        """Test classical-only mode (RSA only)"""
        server = HybridKeyExchange(use_kyber=False, use_rsa=True, rsa_key_size=2048)
        server_public, server_private = server.generate_keypairs()
        
        assert 'kyber' not in server_public
        assert 'rsa' in server_public
        
        client = HybridKeyExchange(use_kyber=False, use_rsa=True, rsa_key_size=2048)
        ciphertexts, client_secret = client.client_encapsulate(server_public)
        
        server_secret = server.server_decapsulate(server_private, ciphertexts)
        
        assert client_secret.combined_secret == server_secret.combined_secret
    
    def test_metrics(self):
        """Test metrics collection"""
        hybrid = HybridKeyExchange(use_kyber=True, use_rsa=True, rsa_key_size=2048)
        
        metrics = hybrid.get_metrics()
        
        assert metrics['use_kyber'] is True
        assert metrics['use_rsa'] is True
        assert metrics['rsa_key_size'] == 2048
        assert metrics['quantum_resistant'] is True
        assert metrics['backward_compatible'] is True
    
    def test_compare_modes(self):
        """Test mode comparison"""
        comparison = HybridKeyExchange.compare_modes()
        
        assert 'pqc_only' in comparison
        assert 'classical_only' in comparison
        assert 'hybrid' in comparison
        
        assert comparison['pqc_only']['quantum_resistant'] is True
        assert comparison['classical_only']['quantum_resistant'] is False
        assert comparison['hybrid']['quantum_resistant'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
