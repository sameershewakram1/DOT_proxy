# DNS over TLS Proxy

This project implements a DNS over TLS (DoT) proxy, providing encrypted DNS resolution for enhanced privacy and security. It handles TCP and UDP queries both.

## Implementation Choices

- **Python**: Chosen for its readability, extensive networking libraries, and suitability for rapid development.
- **Threading Model**: Utilizes ThreadingTCPServer and ThreadingUDPServer to handle multiple DNS requests concurrently, improving responsiveness in scenarios with multiple clients.
- **TLS Wrapper**: A custom `tls_wrapper.py` encapsulates the TLS communication with an upstream DoT resolver. Ideally, DTLS (Datagram TLS) would be used to secure UDP DNS traffic directly. However, since a dedicated DTLS library wasn't readily available, TLS over TCP is employed as a workaround.
  - **UDP to TCP Adaptation**: A helper function (`translate_pkt_from_udp_to_tcp`) found in the `udp_handler.py` file prepends a length field to the UDP data, making it appear like a TCP stream for the upstream DoT resolver. This approach is limited to DNS queries as other protocols might have different packet structures and semantics.

## Running and Testing the Proxy

### **Prerequisites**

  * Python 3
  * Project files
  * Docker (optional, for containerized execution)

### **1. Running without Docker**
- Navigate to the project directory (**Sudo** permission maybe required to run this):
 ```bash
     cd dns_over_tls
     python3 main.py
 ```
###  **2. Run with Docker container (Always preferred way for security purposes)**
   ```bash
        docker build -t my-dns-proxy .
        docker run -d -p 5353:53/tcp my-dns-proxy
   ```
### **3. Testing**
   - **Testing without Docker**
     - UDP: ```bash dig @127.0.0.1 google.com```
     - TCP: ```bash dig @127.0.0.1 google.com +tcp```
    
   - T**esting with Docker** 
        - You have noticed that I am adding port `5353`, this is because port `53` is already occupied by our system so killing it for this project may break things in system so, I changed the port.
        - UDP: ```bash dig @127.0.0.1 -p 5353 google.com ```
        - TCP: ```bash dig @127.0.0.1 -p 5353 google.com +tcp```
    
### Troubleshooting 
- If UDP queries times out when running the proxy with Docker, you can test it from the container.
- For further debugging, you can run commands directly within the container.
- Assuming you are already running DNS proxy container, if not then please follow the Step 2 `Run with Docker`.

  ```bash
  docker exec -it my-dns-proxy bash
  ```
  Inside the container: 
  ```bash
  apk add --update bind-tools
  ```
  ``` bash
  dig @127.0.0.1 google.com
  ```
  ``` bash
  dig @127.0.0.1 google.com +tcp
  ```
    
## Security Considerations

1. **Encryption and Authentication**
   - Robust TLS Implementation: Ensure your TLS library is up-to-date and configured with strong cipher suites. Disable legacy versions of TLS (TLS 1.0, TLS 1.1) and insecure ciphers.
   - Certificate Validation: Meticulously verify certificates presented by the upstream DNS-over-TLS server to prevent man-in-the-middle (MitM) attacks. Consider certificate pinning for even stronger security guarantees.

2. **Access Control**
   - Network-level Restrictions:
     - Use Kubernetes Network Policies or firewalls to restrict which clients can communicate with your DNS proxy.
     - Allow access only from authorized subnets or specific pods/services.
   - Authentication (If Needed): If you need fine-grained control, implement a mechanism for clients to authenticate themselves to the proxy (e.g., mutual TLS authentication).

3. **Secure Coding Practices (`tls_wrapper.py`)**
   - Input Validation: Sanitize all incoming DNS queries to prevent malformed requests that could be used for injection attacks or exploits.
   - Error Handling: Implement robust error handling in proxy code to prevent unexpected behavior that could introduce vulnerabilities.
   - Dependency Management: Stay vigilant with security updates for TLS library and any other dependencies used in your DNS proxy.

4. **Infrastructure Security**
   - Host Hardening: Secure the underlying system (container host or VM) where your proxy runs. Apply OS updates, use least-privilege principles, and minimize the attack surface.
   - Secret Management: Store sensitive information (TLS certificates, authentication credentials) in a secure secret management system like Kubernetes Secrets or a dedicated vault solution (e.g., Hashicorp Vault).

5. **Monitoring and Auditing**
   - Logging:
     - Log DNS queries, responses, any authentication attempts, and security-relevant events.
     - Send logs to a centralized log aggregation system for analysis.
   - Alerting: Configure alerts for anomalies like unexpected traffic patterns, surges in failed requests, or TLS/certificate-related errors. Proactive alerting can help in early detection of attacks or misconfigurations.


6. **Additional Considerations**
    - DNSSEC: If possible, consider enabling support for DNSSEC validation in your proxy. This adds another layer of security by verifying the authenticity of DNS responses.
    - Rate Limiting: Implement rate limiting or traffic shaping mechanisms to mitigate potential denial-of-service (DoS) attacks aimed at your DNS proxy.
    - Regular Testing: Incorporate security testing (both manual and automated) into your development and deployment processes.

## Integration in a Microservices Architecture

1. **Image Design:**
   - Start with a lean base image (Alpine Linux is popular for its small size).
   - Minimize layers for efficiency and security.
   - Consider multi-stage builds to keep the final image small.
   - Health Checks: Implement liveness and readiness probes in your container to signal its health to Kubernetes.

2. **Deployment:**
   - Kubernetes Manifests: Use Deployments, Services (likely ClusterIP initially), and potentially Ingress resources for external access.
   - Versioning and Rollbacks: Tag images meticulously and use Kubernetes' rolling update strategies for safe deployments.

3. **CI/CD:**
    - Automate Everything: Build, test, package (Helm), and deploy automatically as part of a CI/CD pipeline.
    - Deployment Tools: Leverage tools like ArgoCD for GitOps-style deployments and configuration synchronization.

4. **Service Discovery:**
   - Preferred: Kubernetes DNS: Integrate your DNS-over-TLS proxy as an upstream server within coredns. This makes adoption seamless for most microservices, assuming they already rely on it.
   - Service Mesh (if applicable): If you're using a service mesh like Istio or Linkerd, leverage their built-in service discovery and traffic management capabilities.

5. **Scalability & Resiliency:**
   - Horizontal Pod Autoscaler: Use Kubernetes' HPA based on relevant metrics (request rate, CPU).
   - Multiple Replicas: Always run multiple instances of your proxy behind a load balancer for availability.
   - Node Distribution: Distribute pods across nodes for high availability in case of node failures.

6. **Observability:**
   - Metrics:
     - Export Prometheus-compatible metrics for request volume, error rates, latency distribution, etc.
     - Consider integrating with a monitoring system like Prometheus and Grafana for visualization and alerting.
   - Structured Logging: Use JSON-formatted logs for easier parsing and analysis by log aggregation tools (e.g., ElasticSearch, Logstash, Fluentd, Loki).
   - Distributed Tracing (if applicable): Integrate with a distributed tracing system (Jaeger, OpenTelemetry) to trace requests across your microservices architecture, including through the DNS proxy.


## Potential Improvements

1. **Caching:** Add a local cache to store DNS records for a short time, reducing latency for frequently requested domains.
2. **Metrics and Monitoring:** Expose metrics (e.g., request rate, errors, latency) for integration with monitoring systems like Prometheus.
3. **Asynchronous I/O:** Investigate libraries like asyncio for potential performance optimizations, especially if the upstream DNS communication becomes a bottleneck.
4. **Advanced DNS Features:** Consider adding support for DNSSEC validation or other DNS privacy extensions.
5. **Investigate DTLS Libraries:** Briefly mention exploring DTLS libraries in the future for a more native approach to securing UDP-based DNS communication.


### Sources
- https://docs.python.org/3/library/socketserver.html#asynchronous-mixins
- https://coredns.io/2017/07/23/corefile-explained/
- https://www.cloudflare.com/learning/dns/dns-over-tls/#:~:text=(TLS%20is%20also%20known%20as,forged%20via%20on%2Dpath%20attacks.
