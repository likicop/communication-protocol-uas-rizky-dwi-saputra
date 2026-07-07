# Evidence Screenshot

Folder ini berisi screenshot evidence UAS:

- success-01.png = GET /health 200 OK
- success-02.png = POST /incidents 201 Created
- success-03.png = GET /incidents 200 OK
- failure-01.png = POST /incidents body kosong 400 Bad Request
- failure-02.png = GET incident ID salah 404 Not Found
- failure-03.png = GET /rate-limit-test 429 Too Many Requests
- observability-metrics.png = GET /metrics
- observability-log.png = GET /logs
- swagger-docs.png = FastAPI Swagger Docs
- wireshark-capture.png = FastAPI traffic port 8000
- wireshark-rate-limit-429.png = Wireshark response 429
- n8n-execution-success.png = n8n workflow succeeded
- n8n-webhook-simulation.png = webhook simulation response
- wireshark-n8n-capture.png = n8n webhook traffic port 5678
