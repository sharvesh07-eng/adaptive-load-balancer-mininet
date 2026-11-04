# Adaptive Load Balancer – Test Results

## 1. Introduction

This document records the testing and validation of the Adaptive Load Balancer implemented using Mininet.

The objective is to verify network connectivity, request forwarding, concurrent request handling, backend failure handling, and service recovery.

## 2. Testing Environment

The project was tested in an Ubuntu virtual machine using Mininet.

### Network Topology

| Component | Role | IP Address |
|---|---|---|
| h1 | Client | 10.0.0.1 |
| h2 | Load Balancer | 10.0.0.2 |
| h3 | Backend Server 1 | 10.0.0.3 |
| h4 | Backend Server 2 | 10.0.0.4 |
| s1 | Open vSwitch | — |

### Server Configuration

| Backend | Port | Simulated Processing Delay |
|---|---|---|
| Backend 1 | 9001 | 0.80 seconds |
| Backend 2 | 9001 | 0.10 seconds |

The load balancer listens on port 8000.

The configured delays simulate different backend processing times. They are not dynamically measured performance metrics.

## 3. Network Topology Validation

### Objective

Verify that all four Mininet hosts can communicate through the virtual switch.

### Command

```bash
sudo mn --custom topology/topology.py --topo adaptive --test pingall

```

### Observed Result

```text
*** Results: 0% dropped (12/12 received)
```

### Conclusion

All 12 connectivity checks succeeded, with 0% packet loss. This confirms that the Mininet topology and basic host connectivity are functioning correctly.

## 4. Functional Testing

### Test 1: Backend Server Availability

**Objective:** Verify that both backend servers start and listen on port 9001.

**Observed Result:**
- Backend 1 was listening on port 9001.
- Backend 2 was listening on port 9001.
- The load balancer was listening on port 8000.

**Conclusion:** All three application components successfully started.

### Test 2: Basic Client Request

**Objective:** Verify that a client request reaches the load balancer and receives a backend response.

**Command:**

```bash
h1 curl http://10.0.0.2:8000
```

**Observed Responses:**

```text
Served by: backend1
Request number: 1
Processing delay: 0.80 seconds
```

A subsequent request returned:

```text
Served by: backend2
Request number: 1
Processing delay: 0.10 seconds
```

**Conclusion:** Both backend servers successfully received requests through the load balancer, and their responses reached the client.

## 5. Concurrent Request Testing

### Objective

Verify that the load balancer can handle multiple simultaneous client requests.

### Command

```bash
h1 bash -c 'for i in 1 2 3 4 5 6 7 8; do (curl -s http://10.0.0.2:8000 | grep "Served by") & done; wait'
```

### Observed Result

Eight responses were received:

- Backend 1: 4 requests
- Backend 2: 4 requests

### Conclusion

The load balancer successfully handled eight concurrent requests, with both backend servers serving requests.

This test verifies concurrent request handling and distribution. It does not establish a throughput improvement over another load-balancing algorithm.

## 6. Backend Failure Handling

### Objective

Verify that the load balancer can continue serving requests when a backend is unavailable.

### Test Procedure

Backend 2 was stopped. Backend 1 was brought back online and verified to be listening on port 9001.

A client request was then sent through the load balancer.

### Observed Result

```text
Served by: backend1
Request number: 1
Processing delay: 0.80 seconds
```

### Conclusion

The load balancer successfully served a request through Backend 1 while Backend 2 was unavailable.

## 7. Backend Recovery

### Objective

Verify that a backend can become available for request handling again after restarting.

### Test Procedure

Backend 2 was restarted and verified to be listening on port 9001.

A client request was sent through the load balancer.

### Observed Result

```text
Served by: backend2
Request number: 1
Processing delay: 0.10 seconds
```

### Conclusion

The recovered backend became available for request handling again.

## 8. Complete Backend Outage

### Objective

Verify the load balancer's behaviour when both backend servers are unavailable.

### Test Procedure

Both backend servers were stopped while the load balancer remained running.

A client request was sent to the load balancer.

### Observed Result

```text
HTTP/1.1 503 Service Unavailable
Content-Type: text/plain; charset=utf-8

No healthy backend is available
```

### Conclusion

The load balancer correctly returned HTTP 503 when neither backend was healthy.

## 9. Service Recovery After Complete Outage

### Objective

Verify that the service can recover after all backend servers become unavailable.

### Test Procedure

After confirming that both backends were stopped, Backend 1 was restarted without restarting the load balancer.

A new client request was sent.

### Observed Result

```text
HTTP/1.1 200 OK

Served by: backend1
Request number: 1
Processing delay: 0.80 seconds
```

### Conclusion

The load balancer successfully resumed request forwarding after a backend became available again.

## 10. Results Summary

| Test | Expected Behaviour | Observed Result | Status |
|---|---|---|---|
| Network connectivity | All hosts communicate | 12/12 successful, 0% loss | PASS |
| Backend availability | Both backends listen on port 9001 | Both listening | PASS |
| Basic request | Client receives backend response | Both backends served requests | PASS |
| Concurrent requests | Handle simultaneous requests | 8 responses received | PASS |
| Backend failure | Continue using available backend | Backend 1 served request | PASS |
| Backend recovery | Recovered backend becomes selectable | Backend 2 served request | PASS |
| Complete outage | Return service unavailable response | HTTP 503 returned | PASS |
| Service recovery | Resume service after backend restart | HTTP 200 returned | PASS |

## 11. Limitations

The current implementation and testing have the following limitations:

1. Backend processing delays are manually configured to simulate different processing speeds.
2. The load balancer uses the number of active requests for backend selection; it does not measure CPU or memory utilization.
3. The concurrent request test verifies successful handling but does not provide a detailed throughput or latency benchmark.
4. The tests were conducted in a Mininet virtual environment and may not represent real-world production traffic.
5. The implementation is a user-space TCP/HTTP proxy and does not currently implement OpenFlow-based traffic control.

## 12. Conclusion

The testing results demonstrate that the Adaptive Load Balancer can successfully route client requests to backend servers, handle concurrent requests, identify unavailable backends, and recover when backend services become available again.

The implementation also correctly returns an HTTP 503 response when no healthy backend is available.

Overall, the observed tests validate the core functionality of the load-balancing system within the Mininet environment.
