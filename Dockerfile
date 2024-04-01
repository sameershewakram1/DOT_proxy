FROM python:3.8-alpine

WORKDIR /dns_over_tls
# Copy your Project Code 
COPY dns_over_tls ./

ENV HOST="0.0.0.0"

# Expose the Ports 
EXPOSE 5353

# Start the Proxy 
CMD ["python", "main.py"]
