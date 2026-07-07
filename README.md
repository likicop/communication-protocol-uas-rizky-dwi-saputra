# SmartTask Incident Monitoring API

UAS Communication Protocol — Use Case: **Monitoring Mini (REST + Logs)**.

## Cara menjalankan API
```bash
cd app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Swagger Docs: http://127.0.0.1:8000/docs

## Folder
- `app/` source code FastAPI
- `docs/` laporan dan slide
- `postman/collection.json` Postman collection
- `n8n/workflow.json` workflow n8n
- `evidence/` screenshot evidence
