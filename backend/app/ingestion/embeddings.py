from __future__ import annotations

from typing import List
import hashlib
import logging
from functools import lru_cache

from app.config import settings

logger = logging.getLogger(__name__)

# Global model variable
_model = None

def get_model():
    """Lazy load the fastembed model."""
    global _model
    if _model is None:
        try:
            from fastembed import TextEmbedding
            # FastEmbed uses slightly different model names, but "BAAI/bge-small-en-v1.5" or similar are good.
            # "sentence-transformers/all-MiniLM-L6-v2" is also supported by FastEmbed as "QA/all-MiniLM-L6-v2" or similar mappings.
            # We'll use the default or a specific compatible one.
            # For simplicity and compatibility, let's use a very standard one supported by fastembed.
            # "BAAI/bge-small-en-v1.5" is great, but let's stick to what we had if possible, or close to it.
            # FastEmbed defaults to "BAAI/bge-small-en-v1.5" which is 384 dim, same as all-MiniLM-L6-v2.
            logger.info(f"Loading embedding model (FastEmbed): {settings.embeddings_model}")
            _model = TextEmbedding(model_name=settings.embeddings_model)
        except ImportError:
            logger.error("fastembed not installed. Please install it with: pip install fastembed")
            raise
    return _model

def _hash_to_vector(text: str, dim: int = 8) -> List[float]:
    """Legacy hash-based embeddings for testing."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    # Repeat the digest to fill dimensions if needed
    extended_digest = digest * (dim // len(digest) + 1)
    values = [b for b in extended_digest[:dim]]
    return [v / 255.0 for v in values]

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts.
    Supports 'sentence-transformers' (mapped to FastEmbed) and 'hash' (deterministic/random).
    """
    if settings.embeddings_provider == "sentence-transformers":
        model = get_model()
        # FastEmbed returns a generator of numpy arrays
        embeddings_generator = model.embed(texts)
        return [e.tolist() for e in embeddings_generator]
    
    # Fallback/Legacy hash embeddings
    dim = max(1, int(settings.embeddings_dim))
    return [_hash_to_vector(text, dim=dim) for text in texts]
