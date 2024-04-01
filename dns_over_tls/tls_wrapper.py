import logging
import socket
import ssl

logger = logging.getLogger("DNS_over_TLS")


class TLSWrapper:
    """
    1. Establishes a plain TCP connection.
    2. "Wraps" that connection with TLS encryption provided by the ssl library.
    3. Send response back to relevant handler(TCP or UDP)
    """

    def handle_tcp_and_udp_query(data):
        CLOUDFLARE_RESOLVER = "1.1.1.1"
        CLOUDFLARE_PORT = 853  # Standard port for DNS over TLS (DOT)
        QUAD_RESOLVER = "9.9.9.9"  # Quad Resolver, was also playing with this one

        # Creates an SSL context object. 
        # This context holds settings, certificates, and configurations necessary for
        # establishing secure TLS connections.
        context = ssl.create_default_context()
        try:
            with socket.create_connection((CLOUDFLARE_RESOLVER, CLOUDFLARE_PORT)) as sock:
                sock.settimeout(5)
                # This establishes the TLS connection over the socket.
                # 'server_hostname' is used for Server Name Indication (SNI) to 
                # ensure the correct server certificate is presented.
                with context.wrap_socket(sock, server_hostname=CLOUDFLARE_RESOLVER) as tls_sock:
                    logger.info(f"TLS Version: {tls_sock.version()}")
                    # Send the DNS query over the TLS connection
                    logger.info(f"DNS query: {data}")
                    tls_sock.sendall(data)
                    # Receive response from Cloudflare
                    tls_response = tls_sock.recv(4096)
                    logger.info(f"Response from DNS server: {tls_response}")
                    return tls_response  # Return the raw response
        except socket.timeout:
            logger.error("Connection or communication timed out")
            return None
        except ssl.SSLError as e:
            logger.error(f"TLS/SSL issue: {e}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")  # Logs the full traceback
            return None
