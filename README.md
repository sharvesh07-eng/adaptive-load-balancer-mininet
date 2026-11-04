# Adaptive Load Balancer Using Mininet

## 1. Project Overview

This project implements an adaptive software-based load balancer
using Python and Mininet.

The load balancer distributes incoming HTTP requests between
multiple backend servers based on their active request counts.

It performs backend health checks and avoids routing requests
to unavailable servers.

## 2. Network Architecture

The Mininet topology contains four hosts and one Open vSwitch.

| Host | Role | IP Address |
|------|------|------------|
| h1 | Client | 10.0.0.1 |
| h2 | Load Balancer | 10.0.0.2 |
| h3 | Backend Server 1 | 10.0.0.3 |
| h4 | Backend Server 2 | 10.0.0.4 |

Switch: s1

## 3. Backend Configuration

Backend 1:
- Host: h3
- Port: 9001
- Simulated processing delay: 0.8 seconds

Backend 2:
- Host: h4
- Port: 9001
- Simulated processing delay: 0.1 seconds

Load Balancer:
- Host: h2
- Port: 8000

## 4. Load Balancing Algorithm

The load balancer uses the following procedure:

1. Receive an incoming client request.
2. Check the health of configured backend servers.
3. Identify the healthy backend servers.
4. Read the active request count of each healthy backend.
5. Select the backend with the lowest active request count.
6. Use round-robin selection when multiple backends have
   the same active request count.
7. Forward the client request to the selected backend.
8. Forward the backend response to the client.
9. Decrease the selected backend's active request count.

If no healthy backend is available, the load balancer
returns HTTP 503 Service Unavailable.

If the backend connection fails during forwarding,
the load balancer returns HTTP 502 Bad Gateway.

## 5. Project Structure

adaptive-load-balancer/
|
|-- app/
|   |-- backend_server.py
|   |-- load_balancer.py
|
|-- topology/
|   |-- topology.py
|
|-- tests/
|
|-- results/
|
|-- README.md
|-- .gitignore

## 6. Requirements

- Ubuntu Linux
- Python 3
- Mininet
- Open vSwitch
- curl

## 7. Running the Project

From the project directory, start Mininet:

sudo mn --custom topology/topology.py --topo adaptive

Start Backend 1:

h3 python3 /home/sharsem3/adaptive-load-balancer/app/backend_server.py --name backend1 --port 9001 --delay 0.8 &

Start Backend 2:

h4 python3 /home/sharsem3/adaptive-load-balancer/app/backend_server.py --name backend2 --port 9001 --delay 0.1 &

Start the load balancer:

h2 python3 /home/sharsem3/adaptive-load-balancer/app/load_balancer.py --listen-port 8000 --backends 10.0.0.3:9001,10.0.0.4:9001 &

Send a request from the client:

h1 curl http://10.0.0.2:8000

## 8. Testing

The following tests have been performed:

1. Mininet connectivity test:
   All four hosts successfully communicated.

2. Sequential request test:
   Requests were successfully forwarded to both backends.

3. Concurrent request test:
   Eight simultaneous requests were successfully handled.

4. Backend failure test:
   Requests continued through the surviving backend.

5. Complete backend failure test:
   HTTP 503 was returned when no healthy backend remained.

6. Backend recovery test:
   A restarted backend became available for subsequent requests.

## 9. Limitations

- Backend load is estimated using active request counts.
- CPU and memory utilisation are not measured.
- Health checks use TCP connection availability.
- HTTP forwarding is designed for simple HTTP requests.
- This implementation runs as a user-space proxy and does not
  implement an OpenFlow controller.

## 10. Future Improvements

- Add CPU and memory utilisation monitoring.
- Implement periodic health monitoring.
- Improve HTTP request and response handling.
- Compare adaptive selection against round-robin scheduling.
- Add performance benchmarking and visualisation.
