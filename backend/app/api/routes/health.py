import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.knowledge.catalog import RuleCatalog
from app.llm.provider import get_llm_provider, OllamaProvider

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str
    provider: str
    is_ollama_online: bool
    rules_count: int
    environment: str

@router.get("/health", response_model=HealthResponse)
def get_health():
    catalog = RuleCatalog()
    provider = get_llm_provider()
    ollama_check = OllamaProvider().is_available()

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        provider=provider.get_provider_name(),
        is_ollama_online=ollama_check,
        rules_count=len(catalog.get_all_rules()),
        environment="production-ready"
    )
