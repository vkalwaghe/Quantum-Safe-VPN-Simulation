"""
Performance Evaluation Module
Benchmark PQC algorithms vs classical cryptography
"""

import time
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import statistics

from vpn_core.kyber_kex import KyberKeyExchange
from vpn_core.dilithium_sig import DilithiumSignature
from vpn_core.handshake import PQCHandshake
from vpn_core.tunnel import EncryptedTunnel


@dataclass
class PerformanceResult:
    """Container for performance benchmark results"""
    algorithm: str
    operation: str
    iterations: int
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    total_time_ms: float


class PerformanceBenchmark:
    """
    Benchmark PQC algorithms and evaluate performance metrics.
    """

    def __init__(self):
        """Initialize benchmarking tools"""
        self.results: List[PerformanceResult] = []

    def benchmark_kyber_keygen(self, iterations: int = 10) -> PerformanceResult:
        """
        Benchmark Kyber keypair generation.
        
        Args:
            iterations: Number of times to run the operation
            
        Returns:
            PerformanceResult with timing statistics
        """
        times = []
        
        for _ in range(iterations):
            kyber = KyberKeyExchange("512")
            start = time.perf_counter()
            kyber.generate_keypair()
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            times.append(elapsed)
        
        result = PerformanceResult(
            algorithm="Kyber512",
            operation="KeyGen",
            iterations=iterations,
            avg_time_ms=statistics.mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0,
            total_time_ms=sum(times),
        )
        
        self.results.append(result)
        return result

    def benchmark_kyber_encapsulation(self, iterations: int = 10) -> PerformanceResult:
        """
        Benchmark Kyber encapsulation (client side).
        
        Args:
            iterations: Number of times to run the operation
            
        Returns:
            PerformanceResult with timing statistics
        """
        # Generate server keypair
        kyber_server = KyberKeyExchange("512")
        server_public, _ = kyber_server.generate_keypair()
        
        times = []
        
        for _ in range(iterations):
            kyber_client = KyberKeyExchange("512")
            start = time.perf_counter()
            kyber_client.encapsulate(server_public)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        result = PerformanceResult(
            algorithm="Kyber512",
            operation="Encapsulate",
            iterations=iterations,
            avg_time_ms=statistics.mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0,
            total_time_ms=sum(times),
        )
        
        self.results.append(result)
        return result

    def benchmark_kyber_decapsulation(self, iterations: int = 10) -> PerformanceResult:
        """
        Benchmark Kyber decapsulation (server side).
        
        Args:
            iterations: Number of times to run the operation
            
        Returns:
            PerformanceResult with timing statistics
        """
        # Generate server keypair and client ciphertext
        kyber_server = KyberKeyExchange("512")
        server_public, server_secret = kyber_server.generate_keypair()
        
        kyber_client = KyberKeyExchange("512")
        ciphertext, _ = kyber_client.encapsulate(server_public)
        
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            kyber_server.decapsulate(server_secret, ciphertext)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        result = PerformanceResult(
            algorithm="Kyber512",
            operation="Decapsulate",
            iterations=iterations,
            avg_time_ms=statistics.mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0,
            total_time_ms=sum(times),
        )
        
        self.results.append(result)
        return result

    def benchmark_dilithium_keygen(self, iterations: int = 10) -> PerformanceResult:
        """
        Benchmark Dilithium keypair generation.
        
        Args:
            iterations: Number of times to run the operation
            
        Returns:
            PerformanceResult with timing statistics
        """
        times = []
        
        for _ in range(iterations):
            dilithium = DilithiumSignature("2")
            start = time.perf_counter()
            dilithium.generate_keypair()
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        result = PerformanceResult(
            algorithm="Dilithium2",
            operation="KeyGen",
            iterations=iterations,
            avg_time_ms=statistics.mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0,
            total_time_ms=sum(times),
        )
        
        self.results.append(result)
        return result

    def benchmark_dilithium_sign(self, iterations: int = 10) -> PerformanceResult:
        """
        Benchmark Dilithium signature generation.
        
        Args:
            iterations: Number of times to run the operation
            
        Returns:
            PerformanceResult with timing statistics
        """
        dilithium = DilithiumSignature("2")
        _, secret_key = dilithium.generate_keypair()
        message = b"Test message for signing"
        
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            dilithium.sign(message, secret_key)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        result = PerformanceResult(
            algorithm="Dilithium2",
            operation="Sign",
            iterations=iterations,
            avg_time_ms=statistics.mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0,
            total_time_ms=sum(times),
        )
        
        self.results.append(result)
        return result

    def benchmark_dilithium_verify(self, iterations: int = 10) -> PerformanceResult:
        """
        Benchmark Dilithium signature verification.
        
        Args:
            iterations: Number of times to run the operation
            
        Returns:
            PerformanceResult with timing statistics
        """
        dilithium = DilithiumSignature("2")
        public_key, secret_key = dilithium.generate_keypair()
        message = b"Test message for signing"
        signature = dilithium.sign(message, secret_key)
        
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            dilithium.verify(message, signature, public_key)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        result = PerformanceResult(
            algorithm="Dilithium2",
            operation="Verify",
            iterations=iterations,
            avg_time_ms=statistics.mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0,
            total_time_ms=sum(times),
        )
        
        self.results.append(result)
        return result

    def benchmark_full_handshake(self, iterations: int = 5) -> Dict[str, Any]:
        """
        Benchmark complete PQC VPN handshake.
        
        Args:
            iterations: Number of times to run the operation
            
        Returns:
            Dictionary with handshake timing and metrics
        """
        times = []
        handshake_metrics = []
        
        for i in range(iterations):
            start = time.perf_counter()
            
            # Client initialization
            client = PQCHandshake("client-1", is_server=False)
            client_hello = client.create_client_hello()
            
            # Server initialization and response
            server = PQCHandshake("server-1", is_server=True)
            server_hello = server.process_client_hello(client_hello)
            
            # Client processes response
            client_finished, session_key = client.process_server_hello(server_hello)
            
            # Server verification
            server_finished = server.process_client_finished(client_finished)
            
            # Client verification
            client.process_server_finished(server_finished)
            
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            
            handshake_metrics.append({
                "iteration": i + 1,
                "handshake_time_ms": elapsed,
                "total_bytes_exchanged": sum(m[1] for m in client.messages_exchanged),
            })
        
        result = {
            "handshake_type": "PQC-Based VPN",
            "iterations": iterations,
            "avg_time_ms": statistics.mean(times),
            "min_time_ms": min(times),
            "max_time_ms": max(times),
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "total_time_ms": sum(times),
            "details": handshake_metrics,
        }
        
        return result

    def benchmark_tunnel_encryption(self, data_size_kb: int = 100, iterations: int = 10) -> PerformanceResult:
        """
        Benchmark encrypted tunnel operations.
        
        Args:
            data_size_kb: Size of data to encrypt in KB
            iterations: Number of times to run the operation
            
        Returns:
            PerformanceResult with timing statistics
        """
        # Create tunnel with dummy session key
        session_key = b'0' * 32  # 256-bit key
        tunnel = EncryptedTunnel(session_key)
        
        # Generate test data
        test_data = b'X' * (data_size_kb * 1024)
        
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            tunnel.encrypt(test_data)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        result = PerformanceResult(
            algorithm="AES-256-GCM",
            operation=f"Encrypt_{data_size_kb}KB",
            iterations=iterations,
            avg_time_ms=statistics.mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0,
            total_time_ms=sum(times),
        )
        
        self.results.append(result)
        return result

    def get_all_results(self) -> List[Dict[str, Any]]:
        """
        Get all benchmark results.
        
        Returns:
            List of benchmark results as dictionaries
        """
        return [asdict(r) for r in self.results]

    def generate_comparison_report(self) -> Dict[str, Any]:
        """
        Generate a comparison report for PQC vs classical cryptography.
        
        Returns:
            Detailed comparison analysis
        """
        return {
            "pqc_kyber": KyberKeyExchange.compare_with_classical(),
            "pqc_dilithium": DilithiumSignature.compare_with_classical(),
            "benchmark_results": self.get_all_results(),
            "conclusions": {
                "kyber_advantages": [
                    "Quantum-resistant key exchange",
                    "NIST-approved standard",
                    "Proven security assumptions",
                ],
                "kyber_tradeoffs": [
                    "Larger public keys and ciphertexts than ECDH",
                    "Slightly higher computational cost",
                    "Larger bandwidth requirements"
                ],
                "dilithium_advantages": [
                    "Quantum-resistant signatures",
                    "NIST-approved standard",
                    "Deterministic signing process"
                ],
                "dilithium_tradeoffs": [
                    "Larger signatures than ECDSA",
                    "Larger public/secret keys",
                    "Higher verification computational cost"
                ],
                "6g_implications": [
                    "PQC enables quantum-safe 6G infrastructure",
                    "Hybrid approaches can mitigate key size overhead",
                    "Forward secrecy combined with PQC strengthens security",
                    "Latency overhead is acceptable for security benefits",
                ]
            }
        }
