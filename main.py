import asyncio
import os
from pathlib import Path
from app.services.agent import ComplianceAgentService
from app.tools.document_generator import DocumentGeneratorTool
from app.tools.slack_notifier import SlackNotifierTool
import logging

# Suppress SDK-level AFC warning noise for AsyncModels
logging.getLogger("google.genai").setLevel(logging.ERROR)
async def main():
    test_file = Path("test_contracts/sample_contract.txt")
    
    if not test_file.exists():
        print(f"[!] Test file missing at {test_file}.")
        return

    agent = ComplianceAgentService()
    print("\n" + "="*60)
    print("      STARTING AUTONOMOUS COMPLIANCE TRIAGE RUN      ")
    print("="*60)

    try:
        report = await agent.audit_contract(test_file)

        # Trigger Action Tool 1: Generate Redline Markdown Document
        doc_path = DocumentGeneratorTool.generate_redline_report(report)

        # Trigger Action Tool 2: Dispatch Slack Notification (if WEBHOOK_URL is present)
        slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")
        if report.overall_status == "REQUIRES_REVIEW":
            SlackNotifierTool.send_audit_alert(slack_webhook, report)

        print("\n" + "="*60)
        print("          AUTONOMOUS ACTION PIPELINE COMPLETE         ")
        print("="*60)
        print(f"[+] Output Report Created: {doc_path}")

    except Exception as e:
        print(f"[!] Audit failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())