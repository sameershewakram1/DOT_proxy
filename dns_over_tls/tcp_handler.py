import logging
import socket
import ssl
from socketserver import BaseRequestHandler

from tls_wrapper import TLSWrapper

logger = logging.getLogger("DNS_over_TLS")


class ThreadedTCPRequestHandler(BaseRequestHandler):
    """
    Handles TCP DNS queries using TLS.
    """

    def handle(self):
        try:
            while True:
                # Receive TCP data
                data = self.request.recv(1024)
                if not data:
                    break
                logger.info(f"TCP Client Address: {self.client_address}")
                # Process the DNS query using the TLS wrapper
                response = TLSWrapper.handle_tcp_and_udp_query(data)
                if response:
                    # Send response back to the TCP client
                    self.request.sendall(response)
                else:
                    logger.info("NO RESPONSE FROM DNS SERVER")
        except socket.timeout:
            logger.error("Connection or communication timed out")
            return None
        except ssl.SSLError as e:
            logger.error(f"TLS/SSL issue: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")  # Logs the full traceback
            return None
