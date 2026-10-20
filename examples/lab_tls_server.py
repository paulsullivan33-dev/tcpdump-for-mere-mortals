#!/usr/bin/env python3
"""TLS specimen for "tcpdump for Mere Mortals", chapter 8.

Serves the packet lab's specimen page over HTTPS on
127.0.0.1 tcp/45443, using a self-signed certificate you
make yourself (the chapter shows the openssl commands).
The point of the fixture is what tcpdump can and cannot
see of an encrypted conversation.

Usage:
    openssl req -x509 -newkey rsa:2048 -nodes \
        -keyout lab-key.pem -out lab-cert.pem -days 30 \
        -subj "/CN=lab.test" \
        -addext "subjectAltName=DNS:lab.test"
    python3 lab_tls_server.py lab-cert.pem lab-key.pem
    curl -k --resolve lab.test:45443:127.0.0.1 \
        https://lab.test:45443/
"""

import ssl
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ADDR = ("127.0.0.1", 45443)

PAGE = (
    b"<!doctype html>\n"
    b"<title>Packet Lab - Specimen Page</title>\n"
    b"<h1>Packet Lab</h1>\n"
    b"<p>The same specimen page, this time under TLS.\n"
    b"The packets still cross the loopback; only the\n"
    b"reading of them changed.</p>\n"
)


class Handler(BaseHTTPRequestHandler):
    server_version = "PacketLabTLS/1.0"
    sys_version = ""

    def do_GET(self):
        body, code = (PAGE, 200) if self.path in ("/", "/index.html") \
            else (b"no specimen at this address\n", 404)
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("lab tls: %s\n" % (fmt % args))


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(sys.argv[1], sys.argv[2])
    server = ThreadingHTTPServer(ADDR, Handler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    print("tls packet lab listening: https tcp/45443"
          " (127.0.0.1 only) - Ctrl-C to stop", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
