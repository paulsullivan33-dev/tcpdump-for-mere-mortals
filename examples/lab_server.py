#!/usr/bin/env python3
"""Packet lab fixture for "tcpdump for Mere Mortals".

Stands up, on 127.0.0.1 only:

  - a specimen web server on tcp/45080 that serves one
    invented page (and a plain 404 for anything else)
  - a UDP echo on udp/45053 that answers every datagram
    with "echo: " in front of what you sent

Deliberately closed specimens: tcp/45999 and udp/45998
have nothing listening, because a genuine refusal and
a genuine silence are lessons too.

Usage:
    python3 lab_server.py           # run until Ctrl-C
    python3 lab_server.py --check   # say what would run
"""

import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HTTP_ADDR = ("127.0.0.1", 45080)
UDP_ADDR = ("127.0.0.1", 45053)

PAGE = (
    b"<!doctype html>\n"
    b"<title>Packet Lab - Specimen Page</title>\n"
    b"<h1>Packet Lab</h1>\n"
    b"<p>This page exists so tcpdump has something\n"
    b"honest to look at. Every byte of it crossed the\n"
    b"loopback interface to get to you.</p>\n"
)


class Handler(BaseHTTPRequestHandler):
    server_version = "PacketLab/1.0"
    sys_version = ""

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body, code = PAGE, 200
        else:
            body, code = b"no specimen at this address\n", 404
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("lab http: %s\n" % (fmt % args))


def udp_echo():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(UDP_ADDR)
    while True:
        try:
            data, peer = sock.recvfrom(2048)
        except OSError:
            continue
        try:
            # Reply from the fixture's own port, on a connected
            # socket: some locked-down environments refuse an
            # unconnected sendto() even on loopback. The armour
            # keeps one odd datagram from silencing the fixture.
            with socket.socket(socket.AF_INET,
                               socket.SOCK_DGRAM) as reply:
                reply.setsockopt(socket.SOL_SOCKET,
                                 socket.SO_REUSEADDR, 1)
                reply.bind(UDP_ADDR)
                reply.connect(peer)
                reply.send(b"echo: " + data)
        except OSError:
            pass


def main():
    if "--check" in sys.argv:
        print("packet fixture: tcp/45080 http + udp/45053 echo,"
              " on 127.0.0.1")
        print("page: Packet Lab - Specimen Page"
              " (Server: PacketLab/1.0)")
        print("deliberately closed specimens: tcp/45999,"
              " udp/45998 (nothing binds them)")
        return
    threading.Thread(target=udp_echo, daemon=True).start()
    server = ThreadingHTTPServer(HTTP_ADDR, Handler)
    print("packet lab listening: http tcp/45080, udp echo"
          " udp/45053 (127.0.0.1 only) - Ctrl-C to stop",
          file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
