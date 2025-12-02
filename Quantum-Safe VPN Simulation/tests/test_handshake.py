"""
Unit Tests for PQC Handshake Protocol
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vpn_core import PQCHandshake, HandshakeState


class TestPQCHandshake:
    """Test cases for PQC handshake protocol"""
    
    def test_initialization(self):
        """Test handshake initialization"""
        client = PQCHandshake("client-1", is_server=False)
        server = PQCHandshake("server-1", is_server=True)
        
        assert client.peer_id == "client-1"
        assert server.peer_id == "server-1"
        assert client.is_server is False
        assert server.is_server is True
        assert client.state == HandshakeState.INITIAL
    
    def test_client_hello_creation(self):
        """Test ClientHello creation"""
        client = PQCHandshake("client-1", is_server=False)
        client_hello = client.create_client_hello()
        
        assert client_hello.client_id == "client-1"
        assert len(client_hello.client_kyber_public_key) > 0
        assert len(client_hello.client_dilithium_public_key) > 0
        assert client.state == HandshakeState.CLIENT_HELLO_SENT
    
    def test_client_hello_serialization(self):
        """Test ClientHello serialization/deserialization"""
        client = PQCHandshake("client-1", is_server=False)
        client_hello1 = client.create_client_hello()
        
        # Serialize
        data = client_hello1.to_bytes()
        assert isinstance(data, bytes)
        
        # Deserialize
        client_hello2 = type(client_hello1).from_bytes(data)
        
        assert client_hello2.client_id == client_hello1.client_id
        assert client_hello2.client_kyber_public_key == client_hello1.client_kyber_public_key
        assert client_hello2.client_dilithium_public_key == client_hello1.client_dilithium_public_key
    
    def test_server_hello_processing(self):
        """Test server processing of ClientHello"""
        client = PQCHandshake("client-1", is_server=False)
        server = PQCHandshake("server-1", is_server=True)
        
        client_hello = client.create_client_hello()
        server_hello = server.process_client_hello(client_hello)
        
        assert server_hello.server_id == "server-1"
        assert len(server_hello.server_kyber_public_key) > 0
        assert len(server_hello.server_dilithium_public_key) > 0
        assert len(server_hello.server_kyber_ciphertext) > 0
        assert server.state == HandshakeState.SERVER_HELLO_SENT
    
    def test_complete_handshake(self):
        """Test complete handshake flow"""
        # Setup
        client = PQCHandshake("client-1", is_server=False)
        server = PQCHandshake("server-1", is_server=True)
        
        # ClientHello
        client_hello = client.create_client_hello()
        assert client.state == HandshakeState.CLIENT_HELLO_SENT
        
        # ServerHello
        server_hello = server.process_client_hello(client_hello)
        assert server.state == HandshakeState.SERVER_HELLO_SENT
        
        # ClientFinished
        client_finished, client_key = client.process_server_hello(server_hello)
        assert client.state == HandshakeState.CLIENT_FINISHED_SENT
        assert client.session_key is not None
        assert len(client_key) == 32
        
        # ServerFinished
        server_finished = server.process_client_finished(client_finished)
        assert server.state == HandshakeState.SERVER_FINISHED_SENT
        assert server.session_key is not None
        
        # Client verification
        client.process_server_finished(server_finished)
        assert client.state == HandshakeState.COMPLETED
    
    def test_session_keys_match(self):
        """Test that client and server derive matching session keys"""
        client = PQCHandshake("client-1", is_server=False)
        server = PQCHandshake("server-1", is_server=True)
        
        # Complete handshake
        client_hello = client.create_client_hello()
        server_hello = server.process_client_hello(client_hello)
        client_finished, _ = client.process_server_hello(server_hello)
        server_finished = server.process_client_finished(client_finished)
        client.process_server_finished(server_finished)
        
        # Session keys should match
        assert client.session_key == server.session_key
        assert len(client.session_key) == 32
    
    def test_handshake_metrics(self):
        """Test handshake metrics collection"""
        client = PQCHandshake("client-1", is_server=False)
        server = PQCHandshake("server-1", is_server=True)
        
        client_hello = client.create_client_hello()
        server_hello = server.process_client_hello(client_hello)
        client_finished, _ = client.process_server_hello(server_hello)
        server_finished = server.process_client_finished(client_finished)
        client.process_server_finished(server_finished)
        
        metrics = client.get_handshake_metrics()
        
        assert "peer_id" in metrics
        assert "total_messages" in metrics
        assert "total_handshake_bytes" in metrics
        assert metrics["total_handshake_bytes"] > 0
        assert metrics["session_key_established"] is True
    
    def test_invalid_signature_detection(self):
        """Test that tampered signatures are detected"""
        client = PQCHandshake("client-1", is_server=False)
        server = PQCHandshake("server-1", is_server=True)
        
        client_hello = client.create_client_hello()
        server_hello = server.process_client_hello(client_hello)
        client_finished, _ = client.process_server_hello(server_hello)
        
        # Tamper with signature
        tampered_signature = b"invalid_signature"
        
        # Should raise exception
        with pytest.raises(ValueError):
            server.process_client_finished(tampered_signature)


class TestHandshakeState:
    """Test handshake state machine"""
    
    def test_state_transitions(self):
        """Test correct state transitions"""
        client = PQCHandshake("client-1", is_server=False)
        
        assert client.state == HandshakeState.INITIAL
        
        client.create_client_hello()
        assert client.state == HandshakeState.CLIENT_HELLO_SENT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
