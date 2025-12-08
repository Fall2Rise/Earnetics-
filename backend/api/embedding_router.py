from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.embedding_service import embed_text, embed_texts

router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])


class EmbedTextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Plain text to embed locally")


class EmbedBatchRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, description="List of texts to embed")


@router.post("/single")
def generate_single_embedding(request: EmbedTextRequest):
    try:
        vector = embed_text(request.text)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {exc}") from exc

    return {"embedding": vector, "dimensions": len(vector)}


@router.post("/batch")
def generate_batch_embeddings(request: EmbedBatchRequest):
    try:
        vectors = embed_texts(request.texts)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {exc}") from exc

    return {"embeddings": vectors, "dimensions": len(vectors[0]) if vectors else 0}

