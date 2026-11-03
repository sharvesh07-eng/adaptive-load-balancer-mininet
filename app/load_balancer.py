#!/usr/bin/env python3

import argparse
import socket
import socketserver
import threading


class AdaptiveLoadBalancer:

    def __init__(self, backends, timeout=0.25):

        self.backends = list(backends)
        self.timeout = timeout

        self.active = {
            backend: 0 for backend in self.backends
        }

        self.lock = threading.Lock()
        self.round_robin_index = 0

    def is_healthy(self, backend):

        try:
            with socket.create_connection(
                backend, timeout=self.timeout
            ):
                return True

        except OSError:
            return False

    def choose_backend(self):

        healthy_backends = [
            backend
            for backend in self.backends
            if self.is_healthy(backend)
        ]

        if not healthy_backends:
            return None

        with self.lock:

            least_active = min(
                self.active[backend]
                for backend in healthy_backends
            )

            candidates = [
                backend
                for backend in healthy_backends
                if self.active[backend] == least_active
            ]

            backend = candidates[
                self.round_robin_index % len(candidates)
            ]

            self.round_robin_index += 1
            self.active[backend] += 1

            active_count = self.active[backend]

        print(
            f"[LB] Selected {backend[0]}:{backend[1]} "
            f"(active requests: {active_count})",
            flush=True
        )

        return backend

    def release_backend(self, backend):

        if backend is None:
            return

        with self.lock:
            self.active[backend] = max(
                0, self.active[backend] - 1
            )


class ProxyHandler(socketserver.BaseRequestHandler):

    def send_error_response(self, status, reason, message):

        body = (message + "\n").encode("utf-8")

        response = (
            f"HTTP/1.1 {status} {reason}\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode("ascii") + body

        self.request.sendall(response)

    def handle(self):

        balancer = self.server.balancer
        backend = balancer.choose_backend()

        if backend is None:

            self.send_error_response(
                503,
                "Service Unavailable",
                "No healthy backend is available"
            )

            return

        try:

            self.request.settimeout(5)

            request_data = self.request.recv(65536)

            if not request_data:
                return

            with socket.create_connection(
                backend, timeout=3
            ) as upstream:

                upstream.settimeout(10)
                upstream.sendall(request_data)

                while True:

                    chunk = upstream.recv(65536)

                    if not chunk:
                        break

                    self.request.sendall(chunk)

        except OSError as error:

            print(
                f"[LB] Request failed through {backend}: {error}",
                flush=True
            )

            try:
                self.send_error_response(
                    502,
                    "Bad Gateway",
                    "Backend connection failed"
                )
            except OSError:
                pass

        finally:
            balancer.release_backend(backend)


class ThreadedProxyServer(socketserver.ThreadingTCPServer):

    allow_reuse_address = True
    daemon_threads = True


def parse_backends(value):

    backends = []

    for item in value.split(","):

        host, port = item.strip().rsplit(":", 1)

        backends.append((host, int(port)))

    return backends


def main():

    parser = argparse.ArgumentParser(
        description="Adaptive Load Balancer"
    )

    parser.add_argument(
        "--listen-host",
        default="0.0.0.0"
    )

    parser.add_argument(
        "--listen-port",
        type=int,
        default=8000
    )

    parser.add_argument(
        "--backends",
        default="10.0.0.3:9001,10.0.0.4:9001"
    )

    args = parser.parse_args()

    backends = parse_backends(args.backends)

    balancer = AdaptiveLoadBalancer(backends)

    server = ThreadedProxyServer(
        (args.listen_host, args.listen_port),
        ProxyHandler
    )

    server.balancer = balancer

    print(
        f"[LB] Listening on {args.listen_host}:{args.listen_port}",
        flush=True
    )

    print(
        f"[LB] Configured backends: {backends}",
        flush=True
    )

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\n[LB] Shutting down")

    finally:
        server.server_close()


if __name__ == "__main__":
    main()
