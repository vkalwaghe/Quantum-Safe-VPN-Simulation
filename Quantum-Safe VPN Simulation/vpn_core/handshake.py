"""
PQC-Based VPN Handshake Protocol
Implements quantum-resistant authentication and key exchange
"""

import os
import time
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json

from vpn_core.kyber_kex import KyberKeyExchange
from vpn_core.dilithium_sig import DilithiumSignature


class HandshakeState(Enum):
    """Handshake protocol states"""
    INITIAL = 0
    CLIENT_HELLO_SENT = 1
    SERVER_HELLO_SENT = 2
    CLIENT_FINISHED_SENT = 3
    SERVER_FINISHED_SENT = 4
    COMPLETED = 5


@dataclass
class ClientHello:
    """Client hello message in handshake"""
    client_id: str
    client_kyber_public_key: bytes
    client_dilithium_public_key: bytes
    timestamp: float
    
    def to_bytes(self) -> bytes:
        """Serialize to bytes for transmission"""
        data = {
            'client_id': self.client_id,
            'client_kyber_public_key': self.client_kyber_public_key.hex(),
            'client_dilithium_public_key': self.client_dilithium_public_key.hex(),
            'timestamp': self.timestamp,
        }
        return json.dumps(data).encode()
    
    @staticmethod
    def from_bytes(data: bytes) -> 'ClientHello':
        """Deserialize from bytes"""
        obj = json.loads(data.decode())
        return ClientHello(
            client_id=obj['client_id'],
            client_kyber_public_key=bytes.fromhex(obj['client_kyber_public_key']),
            client_dilithium_public_key=bytes.fromhex(obj['client_dilithium_public_key']),
            timestamp=obj['timestamp'],
        )


@dataclass
class ServerHello:
    """Server hello message in handshake"""
    server_id: str
    server_kyber_public_key: bytes
    server_dilithium_public_key: bytes
    server_kyber_ciphertext: bytes
    timestamp: float
    
    def to_bytes(self) -> bytes:
        """Serialize to bytes for transmission"""
        data = {
            'server_id': self.server_id,
            'server_kyber_public_key': self.server_kyber_public_key.hex(),
            'server_dilithium_public_key': self.server_dilithium_public_key.hex(),
            'server_kyber_ciphertext': self.server_kyber_ciphertext.hex(),
            'timestamp': self.timestamp,
        }
        return json.dumps(data).encode()
    
    @staticmethod
    def from_bytes(data: bytes) -> 'ServerHello':
        """Deserialize from bytes"""
        obj = json.loads(data.decode())
        return ServerHello(
            server_id=obj['server_id'],
            server_kyber_public_key=bytes.fromhex(obj['server_kyber_public_key']),
            server_dilithium_public_key=bytes.fromhex(obj['server_dilithium_public_key']),
            server_kyber_ciphertext=bytes.fromhex(obj['server_kyber_ciphertext']),
            timestamp=obj['timestamp'],
        )


class PQCHandshake:
    """
    Post-Quantum Cryptography-based VPN Handshake Protocol
    
    Flow:
    1. Client sends public keys (Kyber, Dilithium) -> ClientHello
    2. Server responds with public keys + encapsulated secret -> ServerHello
    3. Client sends signature + derived session key indicator -> ClientFinished
    4. Server sends signature confirmation -> ServerFinished
    5. Both parties derive final session key from shared secrets
    """

    def __init__(self, peer_id: str, is_server: bool = False):
        """
        Initialize handshake protocol.
        
        Args:
            peer_id: Identifier for this peer
            is_server: True if this is server, False if client
        """
        self.peer_id = peer_id
        self.is_server = is_server
        self.state = HandshakeState.INITIAL
        
        # Initialize PQC algorithms
        self.kyber = KyberKeyExchange("512")
        self.dilithium = DilithiumSignature("2")
        
        # Generate keypairs
        self.kyber_public, self.kyber_secret = self.kyber.generate_keypair()
        self.dilithium_public, self.dilithium_secret = self.dilithium.generate_keypair()
        
        # Handshake state variables
        self.peer_kyber_public: Optional[bytes] = None
        self.peer_dilithium_public: Optional[bytes] = None
        self.shared_secret: Optional[bytes] = None
        self.session_key: Optional[bytes] = None
        self.handshake_hash: Optional[bytes] = None
        
        # Metrics
        self.start_time = time.time()
        self.messages_exchanged = []

    def create_client_hello(self) -> ClientHello:
        """
        Create ClientHello message.
        
        Returns:
            ClientHello message
        """
        hello = ClientHello(
            client_id=self.peer_id,
            client_kyber_public_key=self.kyber_public,
            client_dilithium_public_key=self.dilithium_public,
            timestamp=time.time(),
        )
        
        self.state = HandshakeState.CLIENT_HELLO_SENT
        self.messages_exchanged.append(('CLIENT_HELLO', len(hello.to_bytes())))
        
        return hello

    def process_client_hello(self, hello: ClientHello) -> 'ServerHello':
        """
        Process ClientHello and create ServerHello response.
        
        Args:
            hello: ClientHello message from client
            
        Returns:
            ServerHello response message
        """
        self.peer_kyber_public = hello.client_kyber_public_key
        self.peer_dilithium_public = hello.client_dilithium_public_key
        
        # Generate ciphertext for shared secret
        ciphertext, shared_secret = self.kyber.encapsulate(self.peer_kyber_public)
        self.shared_secret = shared_secret
        
        server_hello = ServerHello(
            server_id=self.peer_id,
            server_kyber_public_key=self.kyber_public,
            server_dilithium_public_key=self.dilithium_public,
            server_kyber_ciphertext=ciphertext,
            timestamp=time.time(),
        )
        
        self.state = HandshakeState.SERVER_HELLO_SENT
        self.messages_exchanged.append(('SERVER_HELLO', len(server_hello.to_bytes())))
        
        return server_hello

    def process_server_hello(self, hello: ServerHello) -> Tuple[bytes, bytes]:
        """
        Process ServerHello and establish shared secret.
        
        Args:
            hello: ServerHello message from server
            
        Returns:
            Tuple of (client_finished_message, session_key)
        """
        self.peer_kyber_public = hello.server_kyber_public_key
        self.peer_dilithium_public = hello.server_dilithium_public_key
        
        # Decapsulate shared secret
        self.shared_secret = self.kyber.decapsulate(
            self.kyber_secret,
            hello.server_kyber_ciphertext
        )
        
        # Derive session key
        handshake_context = self.peer_id.encode() + hello.server_id.encode()
        self.session_key = self.kyber.derive_session_key(self.shared_secret, handshake_context)
        
        # Sign the server's public key to authenticate
        signature = self.dilithium.sign(hello.server_kyber_public_key, self.dilithium_secret)
        
        self.state = HandshakeState.CLIENT_FINISHED_SENT
        self.messages_exchanged.append(('CLIENT_FINISHED', len(signature)))
        
        return signature, self.session_key

    def process_client_finished(self, signature: bytes) -> bytes:
        """
        Verify client's signature and send server finished.
        
        Args:
            signature: Client's signature of server public key
            
        Returns:
            Server finished message (server's signature)
        """
        # Verify client's signature
        is_valid = self.dilithium.verify(
            self.kyber_public,
            signature,
            self.peer_dilithium_public
        )
        
        if not is_valid:
            raise ValueError("Invalid client signature in handshake")
        
        # Derive session key
        handshake_context = self.peer_id.encode() + self.peer_id.encode()
        self.session_key = self.kyber.derive_session_key(self.shared_secret, handshake_context)
        
        # Sign client's public key to confirm
        server_signature = self.dilithium.sign(self.peer_kyber_public, self.dilithium_secret)
        
        self.state = HandshakeState.SERVER_FINISHED_SENT
        self.messages_exchanged.append(('SERVER_FINISHED', len(server_signature)))
        
        return server_signature

    def process_server_finished(self, signature: bytes) -> bool:
        """
        Verify server's finished signature.
        
        Args:
            signature: Server's confirmation signature
            
        Returns:
            True if handshake completed successfully
        """
        # Verify server's signature
        is_valid = self.dilithium.verify(
            self.kyber_public,
            signature,
            self.peer_dilithium_public
        )
        
        if not is_valid:
            raise ValueError("Invalid server signature in handshake")
        
        self.state = HandshakeState.COMPLETED
        
        return True

    def get_handshake_metrics(self) -> Dict[str, Any]:
        """
        Get handshake metrics for performance analysis.
        
        Returns:
            Dictionary with handshake statistics
        """
        elapsed_time = time.time() - self.start_time
        
        total_bytes = sum(msg[1] for msg in self.messages_exchanged)
        
        return {
            "peer_id": self.peer_id,
            "is_server": self.is_server,
            "state": self.state.name,
            "total_messages": len(self.messages_exchanged),
            "messages": [{"type": m[0], "size_bytes": m[1]} for m in self.messages_exchanged],
            "total_handshake_bytes": total_bytes,
            "elapsed_time_seconds": elapsed_time,
            "kyber_metrics": self.kyber.get_metrics(),
            "dilithium_metrics": self.dilithium.get_metrics(),
            "session_key_established": self.session_key is not None,
        }
