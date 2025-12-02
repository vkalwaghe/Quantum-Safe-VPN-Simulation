"""
Network-based VPN Server
Actual socket-based server for quantum-safe VPN connections
"""

import socket
import threading
import logging
import time
from typing import Dict, Callable, Optional, Tuple
import json

from vpn_core import PQCHandshake, EncryptedTunnel, ClientHello, ServerHello

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VPNServer:
    """
    Post-Quantum Cryptography VPN Server
    Handles multiple client connections with PQC-based handshakes
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8443, max_clients: int = 10):
        """
        Initialize VPN server.
        
        Args:
            host: Server host IP address
            port: Server listening port
            max_clients: Maximum concurrent connections
        """
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.server_socket = None
        self.running = False
        
        # Client management
        self.clients: Dict[str, 'ClientConnection'] = {}
        self.clients_lock = threading.Lock()
        
        # Server identity
        self.server_id = f"vpn-server-{host}:{port}"
        self.handshake = None  # Will be initialized for each connection
        
        # Metrics
        self.total_connections = 0
        self.total_bytes_transferred = 0
        self.start_time = None

    def start(self):
        """Start the VPN server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_clients)
            
            self.running = True
            self.start_time = time.time()
            
            logger.info(f"[VPN Server] Started on {self.host}:{self.port}")
            logger.info(f"[VPN Server] Max clients: {self.max_clients}")
            
            # Accept connections in main thread
            self.accept_connections()
            
        except Exception as e:
            logger.error(f"[VPN Server] Failed to start: {e}")
            self.running = False

    def accept_connections(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                
                self.total_connections += 1
                client_id = f"client-{client_address[0]}:{client_address[1]}"
                
                logger.info(f"[VPN Server] New connection from {client_address}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_id, client_address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"[VPN Server] Connection error: {e}")

    def handle_client(self, client_socket: socket.socket, client_id: str, client_address: Tuple):
        """
        Handle individual client connection.
        
        Args:
            client_socket: Client's socket
            client_id: Client identifier
            client_address: Client address tuple
        """
        try:
            # Perform PQC handshake
            logger.info(f"[{client_id}] Starting PQC handshake...")
            
            server_handshake = PQCHandshake(self.server_id, is_server=True)
            
            # Receive ClientHello
            client_hello_data = client_socket.recv(4096)
            client_hello = ClientHello.from_bytes(client_hello_data)
            
            logger.info(f"[{client_id}] Received ClientHello")
            
            # Process and send ServerHello
            server_hello = server_handshake.process_client_hello(client_hello)
            client_socket.send(server_hello.to_bytes())
            
            logger.info(f"[{client_id}] Sent ServerHello")
            
            # Receive ClientFinished
            client_finished_data = client_socket.recv(4096)
            
            # Send ServerFinished
            server_finished = server_handshake.process_client_finished(client_finished_data)
            client_socket.send(server_finished)
            
            logger.info(f"[{client_id}] Handshake completed - Session key established")
            
            # Create encrypted tunnel
            tunnel = EncryptedTunnel(server_handshake.session_key, tunnel_id=client_id)
            
            # Store client connection
            with self.clients_lock:
                self.clients[client_id] = ClientConnection(
                    client_id=client_id,
                    socket=client_socket,
                    tunnel=tunnel,
                    connected_at=time.time()
                )
            
            # Handle encrypted communication
            self.handle_encrypted_communication(client_socket, tunnel, client_id)
            
        except Exception as e:
            logger.error(f"[{client_id}] Error: {e}")
        finally:
            self.disconnect_client(client_id, client_socket)

    def handle_encrypted_communication(self, client_socket: socket.socket, 
                                      tunnel: EncryptedTunnel, client_id: str):
        """
        Handle encrypted data communication with client.
        
        Args:
            client_socket: Client's socket
            tunnel: Encrypted tunnel for this connection
            client_id: Client identifier
        """
        client_socket.settimeout(30)  # 30-second timeout
        
        try:
            while self.running:
                try:
                    # Receive encrypted data
                    encrypted_data = client_socket.recv(4096)
                    
                    if not encrypted_data:
                        logger.info(f"[{client_id}] Connection closed by client")
                        break
                    
                    # Decrypt
                    from vpn_core import EncryptedPacket
                    packet = EncryptedPacket.from_bytes(encrypted_data)
                    plaintext = tunnel.decrypt(packet)
                    
                    self.total_bytes_transferred += len(plaintext)
                    
                    logger.debug(f"[{client_id}] Received {len(plaintext)} bytes")
                    
                    # Echo back encrypted (for testing)
                    response_packet = tunnel.encrypt(b"ACK: " + plaintext[:20])
                    client_socket.send(response_packet.to_bytes())
                    
                except socket.timeout:
                    logger.warning(f"[{client_id}] Connection timeout")
                    break
                    
        except Exception as e:
            logger.error(f"[{client_id}] Communication error: {e}")

    def disconnect_client(self, client_id: str, client_socket: socket.socket):
        """
        Disconnect a client.
        
        Args:
            client_id: Client identifier
            client_socket: Client socket
        """
        with self.clients_lock:
            if client_id in self.clients:
                del self.clients[client_id]
        
        try:
            client_socket.close()
        except:
            pass
        
        logger.info(f"[{client_id}] Disconnected")

    def stop(self):
        """Stop the VPN server"""
        self.running = False
        
        # Disconnect all clients
        with self.clients_lock:
            for client_id in list(self.clients.keys()):
                try:
                    self.clients[client_id].socket.close()
                except:
                    pass
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("[VPN Server] Stopped")

    def get_status(self) -> Dict:
        """
        Get server status and metrics.
        
        Returns:
            Status dictionary
        """
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        with self.clients_lock:
            active_clients = len(self.clients)
        
        return {
            "server": self.server_id,
            "address": f"{self.host}:{self.port}",
            "running": self.running,
            "uptime_seconds": elapsed,
            "active_clients": active_clients,
            "total_connections": self.total_connections,
            "total_bytes_transferred": self.total_bytes_transferred,
            "avg_throughput_mbps": (self.total_bytes_transferred * 8 / 1e6 / elapsed) if elapsed > 0 else 0
        }


class VPNClient:
    """
    Post-Quantum Cryptography VPN Client
    Connects to VPN server and establishes secure tunnel
    """

    def __init__(self, server_host: str, server_port: int, client_id: str = "vpn-client"):
        """
        Initialize VPN client.
        
        Args:
            server_host: VPN server host
            server_port: VPN server port
            client_id: Client identifier
        """
        self.server_host = server_host
        self.server_port = server_port
        self.client_id = client_id
        self.socket = None
        self.tunnel = None
        self.connected = False

    def connect(self) -> bool:
        """
        Connect to VPN server and perform handshake.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create socket and connect
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            
            logger.info(f"[{self.client_id}] Connected to server {self.server_host}:{self.server_port}")
            
            # Perform PQC handshake
            logger.info(f"[{self.client_id}] Starting PQC handshake...")
            
            client_handshake = PQCHandshake(self.client_id, is_server=False)
            
            # Send ClientHello
            client_hello = client_handshake.create_client_hello()
            self.socket.send(client_hello.to_bytes())
            
            logger.info(f"[{self.client_id}] Sent ClientHello")
            
            # Receive ServerHello
            server_hello_data = self.socket.recv(4096)
            server_hello = ServerHello.from_bytes(server_hello_data)
            
            logger.info(f"[{self.client_id}] Received ServerHello")
            
            # Send ClientFinished and get session key
            client_finished, session_key = client_handshake.process_server_hello(server_hello)
            self.socket.send(client_finished)
            
            # Receive ServerFinished
            server_finished = self.socket.recv(4096)
            client_handshake.process_server_finished(server_finished)
            
            logger.info(f"[{self.client_id}] Handshake completed - Session key established")
            
            # Create encrypted tunnel
            self.tunnel = EncryptedTunnel(session_key, tunnel_id=self.client_id)
            self.connected = True
            
            return True
            
        except Exception as e:
            logger.error(f"[{self.client_id}] Connection failed: {e}")
            return False

    def send_data(self, data: bytes) -> bool:
        """
        Send encrypted data through tunnel.
        
        Args:
            data: Data to send
            
        Returns:
            True if successful
        """
        if not self.connected or not self.tunnel:
            logger.error(f"[{self.client_id}] Not connected")
            return False
        
        try:
            packet = self.tunnel.encrypt(data)
            self.socket.send(packet.to_bytes())
            logger.debug(f"[{self.client_id}] Sent {len(data)} bytes")
            return True
        except Exception as e:
            logger.error(f"[{self.client_id}] Send failed: {e}")
            return False

    def receive_data(self, timeout: int = 5) -> Optional[bytes]:
        """
        Receive and decrypt data from tunnel.
        
        Args:
            timeout: Receive timeout in seconds
            
        Returns:
            Decrypted data or None
        """
        if not self.connected or not self.tunnel:
            logger.error(f"[{self.client_id}] Not connected")
            return None
        
        try:
            self.socket.settimeout(timeout)
            encrypted_data = self.socket.recv(4096)
            
            if not encrypted_data:
                return None
            
            from vpn_core import EncryptedPacket
            packet = EncryptedPacket.from_bytes(encrypted_data)
            plaintext = self.tunnel.decrypt(packet)
            
            logger.debug(f"[{self.client_id}] Received {len(plaintext)} bytes")
            return plaintext
            
        except socket.timeout:
            return None
        except Exception as e:
            logger.error(f"[{self.client_id}] Receive failed: {e}")
            return None

    def disconnect(self):
        """Disconnect from VPN server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.connected = False
        logger.info(f"[{self.client_id}] Disconnected")


@dataclass
class ClientConnection:
    """Represents a connected client"""
    client_id: str
    socket: socket.socket
    tunnel: EncryptedTunnel
    connected_at: float
