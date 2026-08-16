import os
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.task_manager import task_manager

app = FastAPI(title="Legal Compliance Triage Engine API")

UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/audit")
async def submit_contract(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """API Endpoint to submit a contract for async triage."""
    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT contracts are supported.")

    # Save uploaded file locally
    temp_path = UPLOAD_DIR / f"{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Register background task
    task_id = task_manager.create_task(file.filename)
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")

    # Dispatch to background execution pool
    background_tasks.add_task(
        task_manager.process_task_background,
        task_id=task_id,
        file_path=temp_path,
        slack_webhook=slack_webhook
    )

    return {"task_id": task_id, "status": "QUEUED", "message": "Contract submitted for asynchronous triage."}

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """API Endpoint to poll task status."""
    if task_id not in task_manager.tasks:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    return task_manager.tasks[task_id]

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Live execution dashboard for hackathon demo."""
    html_content = """
    <!進入 html>
    <html>
    <head>
        <title>Compliance Triage Taskmaster</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; background: #f8fafc; color: #1e293b; }
            .card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 24px; }
            h1 { color: #0f172a; margin-bottom: 8px; }
            .subtitle { color: #64748b; margin-top: 0; font-size: 14px; }
            button { background: #2563eb; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; }
            button:hover { background: #1d4ed8; }
            pre { background: #1e293b; color: #f8fafc; padding: 16px; border-radius: 8px; overflow-x: auto; font-size: 13px; }
            .status-badge { display: inline-block; padding: 4px 12px; border-radius: 9999px; font-weight: 600; font-size: 12px; }
            .status-QUEUED { background: #fef3c7; color: #92400e; }
            .status-PROCESSING { background: #dbeafe; color: #1e40af; }
            .status-COMPLETED { background: #dcfce7; color: #166534; }
            .status-FAILED { background: #fee2e2; color: #991b1b; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>⚖️ Legal Compliance Triage Engine</h1>
            <p class="subtitle">Taskmaster Track • Autonomous Asynchronous Pipeline powered by Gemini 3.5 Flash</p>
            <hr style="border:0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
            <h3>Upload Contract Document</h3>
            <input type="file" id="contractFile" accept=".txt,.pdf">
            <button onclick="uploadContract()">Submit for Async Audit</button>
        </div>

        <div class="card" id="statusCard" style="display:none;">
            <h3>Task Execution Monitor</h3>
            <p>Task ID: <strong id="taskIdDisplay"></strong></p>
            <p>Status: <span id="statusBadge" class="status-badge"></span></p>
            <h4>Live Engine Response:</h4>
            <pre id="jsonOutput">Waiting for state updates...</pre>
        </div>

        <script>
            let currentTaskId = null;
            let pollInterval = null;

            async function uploadContract() {
                const fileInput = document.getElementById('contractFile');
                if (!fileInput.files[0]) {
                    alert('Please select a PDF or TXT contract file first.');
                    return;
                }

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                const response = await fetch('/api/audit', { method: 'POST', body: formData });
                const data = await response.json();

                currentTaskId = data.task_id;
                document.getElementById('taskIdDisplay').innerText = currentTaskId;
                document.getElementById('statusCard').style.display = 'block';

                if (pollInterval) clearInterval(pollInterval);
                pollInterval = setInterval(checkStatus, 2000);
                checkStatus();
            }

            async function checkStatus() {
                if (!currentTaskId) return;
                const response = await fetch('/api/tasks/' + currentTaskId);
                const data = await response.json();

                const badge = document.getElementById('statusBadge');
                badge.innerText = data.status;
                badge.className = 'status-badge status-' + data.status;

                document.getElementById('jsonOutput').innerText = JSON.stringify(data, null, 2);

                if (data.status === 'COMPLETED' || data.status === 'FAILED') {
                    clearInterval(pollInterval);
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)