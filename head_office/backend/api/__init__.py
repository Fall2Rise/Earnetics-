"""
Head Office API Package
"""
from head_office.backend.api.executive_router import router as executive_router
from head_office.backend.api.decisions_router import router as decisions_router
from head_office.backend.api.legal_router import router as legal_router
from head_office.backend.api.tax_router import router as tax_router
from head_office.backend.api.assets_router import router as assets_router
from head_office.backend.api.law_library_router import router as law_library_router
from head_office.backend.api.master_ai_router import router as master_ai_router

__all__ = [
    "executive_router",
    "decisions_router",
    "legal_router",
    "tax_router",
    "assets_router",
    "law_library_router",
    "master_ai_router"
]
