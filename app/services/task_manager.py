import uuid
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from app.services.agent import ComplianceAgentService
from app.tools.document_generator import DocumentGeneratorTool
from app.tools.slack_notifier import SlackNotifierTool

class TaskManager:
    """In-memory background job manager for asynchronous contract processing."""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.agent = ComplianceAgentService()

    def create_task(self, filename: str) -> str:
        task_id = str(uuid.uuid4())[:8]
        self.tasks[task_id] = {
            "task_id": task_id,
            "filename": filename,
            "status": "QUEUED",
            "result": None,
            "redline_file": None,
            "error": None
        }
        return task_id

    async def process_task_background(self, task_id: str, file_path: Path, slack_webhook: Optional[str] = None):
        """Runs Gemini 3.5 Flash triage asynchronously in the background."""
        self.tasks[task_id]["status"] = "PROCESSING"
        print(f"[*] [Task {task_id}] Background processing started for {file_path.name}...")

        try:
            # Execute Gemini Agent Audit
            report = await self.agent.audit_contract(file_path)
            
            # Generate Redline Markdown File
            doc_path = DocumentGeneratorTool.generate_redline_report(report)

            # Send Slack Alert if required
            if slack_webhook and report.overall_status == "REQUIRES_REVIEW":
                SlackNotifierTool.send_audit_alert(slack_webhook, report)

            self.tasks[task_id]["status"] = "COMPLETED"
            self.tasks[task_id]["result"] = report.model_dump()
            self.tasks[task_id]["redline_file"] = str(doc_path)
            print(f"[+] [Task {task_id}] Audit completed successfully!")

        except Exception as e:
            print(f"[!] [Task {task_id}] Processing failed: {e}")
            self.tasks[task_id]["status"] = "FAILED"
            self.tasks[task_id]["error"] = str(e)
            
        finally:
            # Clean up local temporary upload file
            if file_path.exists():
                file_path.unlink()

task_manager = TaskManager()