import json
import urllib.request
from app.schemas.contract_schema import ContractAuditResult

class SlackNotifierTool:
    """Tool for sending automated webhook alerts to legal teams."""

    @staticmethod
    def send_audit_alert(webhook_url: str, audit_result: ContractAuditResult) -> bool:
        """Sends an interactive payload to a Slack Webhook."""
        if not webhook_url:
            print("[!] Slack Webhook URL not provided. Skipping notification.")
            return False

        payload = {
            "text": f"🚨 *Contract Audit Alert: {audit_result.contract_title}*",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Legal Compliance Audit Alert*\n*Contract:* {audit_result.contract_title}\n*Vendor:* {audit_result.vendor_name}\n*Verdict:* `{audit_result.overall_status}`\n*Compliance Score:* {audit_result.compliance_score * 100:.1f}%"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:* {audit_result.executive_summary}"
                    }
                },
                {
                    "type": "divider"
                }
            ]
        }

        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print("[+] Slack compliance alert dispatched successfully.")
                    return True
        except Exception as e:
            print(f"[!] Failed to send Slack alert: {e}")
            return False
        return False