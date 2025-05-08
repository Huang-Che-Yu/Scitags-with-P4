import http.server
import socketserver
import socket
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    seen_connections = set()

    def GET(self):
        client_key = (self.client_address[0], self.client_address[1])
        logger.info(f"Received GET request from {client_key} for {self.path}")

        if client_key not in self.seen_connections:
            logger.info(f"New connection from {client_key}, applying 1-second delay")
            time.sleep(2)
            self.seen_connections.add(client_key)
        else:
            logger.info(f"Existing connection from {client_key}, no delay")

        logger.info("Sending response")
        super().GET()

    def end_headers(self):
        super().end_headers()

class IPv6TCPServer(socketserver.TCPServer):

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        logger.info(f"Server initialized, binding to {server_address}")

    def server_close(self):
        HTTPRequestHandler.seen_connections.clear()
        super().server_close()

PORT = 8000
BIND_ADDRESS = "bbff::11"

try:
    with IPv6TCPServer((BIND_ADDRESS, PORT), HTTPRequestHandler) as httpd:
        logger.info(f"Serving HTTP on {BIND_ADDRESS} port {PORT}...")
        httpd.serve_forever()
except KeyboardInterrupt:
    logger.info("\nShutting down server...")
    httpd.server_close()
except Exception as e:
    logger.error(f"Failed to start server: {e}")