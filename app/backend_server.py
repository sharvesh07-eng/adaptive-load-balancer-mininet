#!/usr/bin/env python3

import argparse
import socketserver
import threading
import time


REQUEST_COUNT = 0
COUNT_LOCK = threading.Lock()


class BackendHandler(socketserver.BaseRequestHandler):

    def handle(self):
        global REQUEST_COUNT

        try:
            data = self.request.recv(65536)

            # Health checks may connect and close without sending data.
            if not data:
                return

            with COUNT_LOCK:
                REQUEST_COUNT += 1
                request_number = REQUEST_COUNT

            # Simulate the processing time of this backend.
            time.sleep(self.server.delay_seconds)

            body = (
                f"Served by: {self.server.backend_name}\n"
                f"Request number: {request_number}\n"
                f"Processing delay: "
                f"{self.server.delay_seconds:.2f} seconds\n"
            ).encode("utf-8")

            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain; charset=utf-8\r\n"
                + f"Content-Length: {len(body)}\r\n".encode("ascii")
                + b"Connection: close\r\n"
                + b"\r\n"
                + body
            )

            self.request.sendall(response)

        except OSError as error:
            print(f"[{self.server.backend_name}] Error: {error}",
                  flush=True)


class BackendServer(socketserver.ThreadingTCPServer):

    allow_reuse_address = True
    daemon_threads = True


def main():

    parser = argparse.ArgumentParser(
        description="Adaptive Load Balancer backend server"
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Name of this backend"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=9001,
        help="Port on which the server listens"
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Simulated processing delay in seconds"
    )

    args = parser.parse_args()

    server = BackendServer(
        ("0.0.0.0", args.port),
        BackendHandler
    )

    server.backend_name = args.name
    server.delay_seconds = max(0.0, args.delay)

    print(
        f"[{args.name}] Listening on port {args.port}; "
        f"delay={server.delay_seconds:.2f}s",
        flush=True
    )

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print(f"\n[{args.name}] Shutting down")

    finally:
        server.server_close()


if __name__ == "__main__":
    main()
