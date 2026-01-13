"""
Head Office Services Package
"""
from head_office.backend.services.database import HeadOfficeDB, get_db
from head_office.backend.services.contract_scanner import ContractScanner
from head_office.backend.services.signature_assistant import SignatureAssistant

__all__ = [
    "HeadOfficeDB",
    "get_db",
    "ContractScanner",
    "SignatureAssistant"
]
