import asyncio
import logging
from pathlib import Path
from google import genai
from google.genai import types

from app.config import Config
from app.schemas.contract_schema import ContractAuditResult

# Suppress SDK-level AFC warning noise for AsyncModels
logging.getLogger("google.genai").setLevel(logging.ERROR)


class ComplianceAgentService:
    """Core agentic service leveraging Gemini 3.5 Flash and the official google-genai SDK for document triage."""

    def __init__(self):
        Config.validate()
        # Initialize official GenAI Client
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.policy_context = Config.load_policy()
        self.model_name = "gemini-3.5-flash"

    async def audit_contract(self, file_path: str | Path) -> ContractAuditResult:
        """
        Uploads a contract PDF/TXT file using the Gemini File API, parses it asynchronously 
        with Gemini 3.5 Flash using structured response schemas, and returns a validated 
        ContractAuditResult Pydantic object.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Contract file not found at: {file_path}")

        print(f"[*] Uploading '{file_path.name}' to Gemini File API...")
        uploaded_file = self.client.files.upload(file=file_path)
        print(f"[+] Uploaded successfully as File ID: {uploaded_file.name}")

        try:
            print(f"[*] Dispatching document to {self.model_name} for compliance triage...")

            # Configure system instructions and strict Pydantic response schema
            system_instruction = f"""
            You are an autonomous Legal Compliance Agent for Enterprise Shield Corp.
            Analyze the provided contract document against our official Corporate Compliance Policy rules:

            {self.policy_context}

            INSTRUCTIONS:
            1. Review all major clauses (Liability, Governing Law, Data Retention, Indemnification, etc.).
            2. Compare each clause against the corresponding rule in our policy.
            3. Flag non-compliant clauses, assign risk levels (LOW, MEDIUM, HIGH), and detail the exact reason for failure.
            4. Provide exact redline text proposals to bring non-compliant clauses into 100% compliance.
            5. Cross-reference failed clauses against relevant state/federal legal precedents or statutory rules where applicable.
            6. Output the result strictly matching the provided JSON response schema.
            """

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=ContractAuditResult,
                temperature=0.1,  # Low temperature for deterministic output
                tools=[{"google_search": {}}]  # Dynamic grounding against live legal statutes
            )

            prompt = "Perform a thorough compliance triage audit on this attached legal document."

            # Asynchronous call using the official google-genai SDK async client
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=[uploaded_file, prompt],
                config=config,
            )

            # SDK automatically validates and parses JSON into ContractAuditResult Pydantic model
            audit_result: ContractAuditResult = response.parsed
            return audit_result

        finally:
            # Resource lifecycle management: delete temporary file from Gemini storage
            print(f"[*] Cleaning up remote file '{uploaded_file.name}' from Gemini storage...")
            self.client.files.delete(name=uploaded_file.name)
            print("[+] Storage cleanup complete.")