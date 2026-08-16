from typing import List, Optional
from pydantic import BaseModel, Field

class ClauseViolation(BaseModel):
    rule_id: str = Field(description="The ID of the policy rule evaluated (e.g., RULE_LIABILITY)")
    clause_title: str = Field(description="Title or topic of the audited clause")
    original_text: str = Field(description="Exact quote or excerpt from the contract document")
    risk_level: str = Field(description="Risk level of the evaluation: LOW, MEDIUM, or HIGH")
    is_compliant: bool = Field(description="True if the clause passes corporate policy, False if it violates it")
    violation_reason: Optional[str] = Field(
        default=None, 
        description="Detailed explanation of why the text violates corporate policy"
    )
    proposed_redline: Optional[str] = Field(
        default=None, 
        description="Suggested replacement phrasing that brings the clause into compliance"
    )

class AuditSummary(BaseModel):
    total_clauses_reviewed: int = Field(description="Total number of key clauses extracted and analyzed")
    failed_clauses_count: int = Field(description="Total number of non-compliant clauses")
    high_risk_violations: int = Field(description="Number of HIGH risk violations identified")

class ContractAuditResult(BaseModel):
    contract_title: str = Field(description="Title or heading of the audited legal contract")
    vendor_name: str = Field(description="Name of the vendor or counterparty")
    overall_status: str = Field(description="Final verdict: APPROVED (if 0 violations) or REQUIRES_REVIEW")
    compliance_score: float = Field(description="Score between 0.0 (total failure) and 1.0 (fully compliant)")
    executive_summary: str = Field(description="Concise 2-3 sentence executive summary for legal counsel")
    summary_metrics: AuditSummary = Field(description="Quantitative breakdown of the audit")
    audited_clauses: List[ClauseViolation] = Field(description="Detailed list of key clauses evaluated")