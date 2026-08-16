import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from app.tools.document_generator import DocumentGeneratorTool
from app.tools.slack_notifier import SlackNotifierTool
from app.schemas.contract_schema import ContractAuditResult

# Initialize FastMCP Server
mcp = FastMCP("Legal Compliance Tools")

# ------------------------------------------------------------------
# MCP Resource: Expose Corporate Compliance Policy dynamically
# ------------------------------------------------------------------
@mcp.resource("policy://corporate_rules")
def get_compliance_policy() -> str:
    """Provides the active enterprise contract compliance policy rules."""
    policy_path = Path("policy.json")
    if policy_path.exists():
        return policy_path.read_text(encoding="utf-8")
    return "{}"

# ------------------------------------------------------------------
# MCP Tool 1: Generate Redline Document
# ------------------------------------------------------------------
@mcp.tool()
def generate_redline_report(audit_result_json: str) -> str:
    """
    Generates a structured legal redline Markdown document from audit results.
    :param audit_result_json: JSON string matching ContractAuditResult schema.
    """
    data = json.loads(audit_result_json)
    audit_result = ContractAuditResult(**data)
    filepath = DocumentGeneratorTool.generate_redline_report(audit_result)
    return f"Redline document generated at: {filepath}"

# ------------------------------------------------------------------
# MCP Tool 2: Dispatch Slack Compliance Alert
# ------------------------------------------------------------------
@mcp.tool()
def send_slack_audit_alert(webhook_url: str, audit_result_json: str) -> str:
    """
    Dispatches a high-priority compliance alert to a team Slack channel.
    :param webhook_url: Incoming Slack Webhook URL.
    :param audit_result_json: JSON string matching ContractAuditResult schema.
    """
    data = json.loads(audit_result_json)
    audit_result = ContractAuditResult(**data)
    success = SlackNotifierTool.send_audit_alert(webhook_url, audit_result)
    return "Slack alert dispatched successfully." if success else "Failed to send Slack alert."

if __name__ == "__main__":
    mcp.run()