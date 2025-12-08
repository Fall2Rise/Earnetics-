"""Local embedding service for Fallat_CrewAI.

This module provides helper functions for generating embeddings using a
SentenceTransformer model that is downloaded once and cached locally. It keeps
the entire embedding pipeline offline, which aligns with the project's data
sovereignty goals.
"""

from __future__ import annotations

import functools
import logging
import os
from typing import Iterable, List, Sequence

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/all-MiniLM-L6-v2",
)

MODEL_CACHE_DIR = os.getenv("EMBEDDING_MODEL_CACHE_DIR")


@functools.lru_cache(maxsize=1)
def _load_model(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    kwargs = {}
    if MODEL_CACHE_DIR:
        kwargs["cache_folder"] = MODEL_CACHE_DIR

    logger.info("Loading embedding model %s (cache=%s)", model_name, MODEL_CACHE_DIR or "default")
    model = SentenceTransformer(model_name, **kwargs)
    model.eval()
    return model


def embed_text(text: str) -> List[float]:
    model = _load_model()
    embedding: Sequence[float] = model.encode(text, convert_to_numpy=True).tolist()
    return list(embedding)


def embed_texts(texts: Iterable[str]) -> List[List[float]]:
    model = _load_model()
    embeddings = model.encode(list(texts), convert_to_numpy=True)
    return [row.tolist() for row in embeddings]

