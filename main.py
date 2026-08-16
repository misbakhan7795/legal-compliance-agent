import asyncio
from pathlib import Path
from app.services.agent import ComplianceAgentService
import logging

# Suppress SDK-level AFC warning noise for AsyncModels
logging.getLogger("google.genai").setLevel(logging.ERROR)
async def main():
    test_file = Path("test_contracts/sample_contract.txt")
    
    if not test_file.exists():
        print(f"[!] Test file missing at {test_file}. Please create it first.")
        return

    agent = ComplianceAgentService()
    print("\n" + "="*60)
    print("      STARTING AUTONOMOUS COMPLIANCE TRIAGE RUN      ")
    print("="*60)

    try:
        report = await agent.audit_contract(test_file)

        print("\n" + "="*60)
        print("              CONTRACT AUDIT RESULT                  ")
        print("="*60)
        print(f"Contract Title   : {report.contract_title}")
        print(f"Vendor Name      : {report.vendor_name}")
        print(f"Overall Status   : {report.overall_status}")
        print(f"Compliance Score : {report.compliance_score * 100:.1f}%")
        print("-" * 60)
        print(f"Executive Summary:\n{report.executive_summary}\n")
        print("-" * 60)
        print("SUMMARY METRICS:")
        print(f"  - Reviewed Clauses : {report.summary_metrics.total_clauses_reviewed}")
        print(f"  - Failed Clauses   : {report.summary_metrics.failed_clauses_count}")
        print(f"  - High Risk Count  : {report.summary_metrics.high_risk_violations}")
        print("-" * 60)
        print("AUDITED CLAUSES & REDLINES:")

        for idx, clause in enumerate(report.audited_clauses, 1):
            status = "[✓] PASS" if clause.is_compliant else f"[!] FAIL ({clause.risk_level} RISK)"
            print(f"\n{idx}. Rule: {clause.rule_id} ({clause.clause_title}) -> {status}")
            print(f"   Excerpt  : \"{clause.original_text}\"")
            if not clause.is_compliant:
                print(f"   Violation: {clause.violation_reason}")
                print(f"   Redline  : {clause.proposed_redline}")

        print("="*60)

    except Exception as e:
        print(f"[!] Audit failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())