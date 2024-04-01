import logging
import socket
import ssl
from socketserver import BaseRequestHandler

from tls_wrapper import TLSWrapper

logger = logging.getLogger("DNS_over_TLS")


class ThreadedUDPRequestHandler(BaseRequestHandler):
    """
    Handles UDP DNS queries using TLS.
    """

    def handle(self):

        try:
            # Receive UDP data
            # self.request consists of a pair of data and client socket
            udp_data = self.request[0]

            logger.info(f"UDP Client Adress: {self.client_address}")
            # Prepare data for TCP transmission 
            data = self.translate_pkt_from_udp_to_tcp(udp_data)
            # Process the DNS query using the TLS wrapper
            response = TLSWrapper.handle_tcp_and_udp_query(data)
            if response:
                # Send response back to the UDP client
                self.request[1].sendto(response[2:], self.client_address)
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

    def translate_pkt_from_udp_to_tcp(self, data):
        # Prepend a 2-byte length field to the UDP data for TCP compatibility
        data_len = bytes([00]) + bytes([len(data)])
        data = data_len + data
        return data
