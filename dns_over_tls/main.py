import os
import logging.handlers
import threading
from socketserver import ThreadingTCPServer, ThreadingUDPServer

from tcp_handler import ThreadedTCPRequestHandler
from udp_handler import ThreadedUDPRequestHandler

# ----- Logging Configuration ------
logger = logging.getLogger("DNS_over_TLS")  # Create a central logger
logger.setLevel(logging.DEBUG)  # Set desired logging level

# File handler for log rotation
handler = logging.handlers.RotatingFileHandler('app.log', maxBytes=1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s -  %(filename)s:%(lineno)d  - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Console handler for immediate output
console_handler = logging.StreamHandler()  # StreamHandler defaults to sys.stderr
console_handler.setFormatter(formatter)  # Use the same formatter as the file handler
logger.addHandler(console_handler)

# ----- Network Configuration -----
HOST, PORT = os.getenv("HOST", "localhost"), os.getenv("PORT", 53)

# Allow address reuse
ThreadingTCPServer.allow_reuse_address = True
ThreadingUDPServer.allow_reuse_address = True

# ----- Server Setup -----
tcp_server = ThreadingTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
udp_server = ThreadingUDPServer((HOST, PORT), ThreadedUDPRequestHandler)

# ----- Start Servers -----
tcp_thread = threading.Thread(target=tcp_server.serve_forever)
udp_thread = threading.Thread(target=udp_server.serve_forever)

tcp_thread.start()
udp_thread.start()

# Block the main thread until servers exit (e.g., for graceful shutdown handling)
tcp_thread.join()
udp_thread.join()
