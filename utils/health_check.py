"""
Health check module for AWS App Runner.
This sets up a health check endpoint for the Streamlit application.
"""

import os
import logging
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # Suppress logging for health check requests
        if args[0].startswith('GET /health'):
            return
        logger.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))

def run_health_check_server(port):
    """Run a simple HTTP server for health checks."""
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"Health check server started on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Error starting health check server: {str(e)}")

def setup_health_check():
    """Set up a health check endpoint for AWS App Runner."""
    # Only run health check server if specified in environment
    if os.environ.get('ENABLE_HEALTH_CHECK', 'false').lower() == 'true':
        health_port = int(os.environ.get('HEALTH_PORT', 8080))
        thread = threading.Thread(target=run_health_check_server, args=(health_port,), daemon=True)
        thread.start()
        logger.info(f"Health check endpoint enabled on port {health_port}")
    else:
        logger.info("Health check endpoint not enabled") 