import os
from pathlib import Path
from app.schemas.contract_schema import ContractAuditResult

class DocumentGeneratorTool:
    """Tool for generating downloadable redline reports and legal documents."""

    @staticmethod
    def generate_redline_report(audit_result: ContractAuditResult, output_dir: str = "output") -> Path:
        """Generates a structured Markdown file containing the redline proposals."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        filename = f"REDLINE_{audit_result.contract_title.replace(' ', '_')}.md"
        file_filepath = out_path / filename

        md_content = f"# LEGAL REDLINE & AUDIT REPORT\n\n"
        md_content += f"**Contract:** {audit_result.contract_title}\n"
        md_content += f"**Vendor:** {audit_result.vendor_name}\n"
        md_content += f"**Status:** {audit_result.overall_status}\n"
        md_content += f"**Compliance Score:** {audit_result.compliance_score * 100:.1f}%\n\n"
        md_content += f"## Executive Summary\n{audit_result.executive_summary}\n\n"
        md_content += f"---\n\n## Audited Clauses & Proposed Redlines\n\n"

        for idx, clause in enumerate(audit_result.audited_clauses, 1):
            status = "APPROVED" if clause.is_compliant else f"REJECTED ({clause.risk_level} RISK)"
            md_content += f"### {idx}. {clause.clause_title} [{status}]\n"
            md_content += f"- **Rule ID:** `{clause.rule_id}`\n"
            md_content += f"- **Original Excerpt:** *\"{clause.original_text}\"*\n"
            
            if not clause.is_compliant:
                md_content += f"- **Violation Reason:** {clause.violation_reason}\n"
                md_content += f"- **Proposed Redline:**\n  > {clause.proposed_redline}\n"
            md_content += "\n"

        with open(file_filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"[+] Redline report generated successfully at: {file_filepath}")
        return file_filepath