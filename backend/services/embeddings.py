"""
Embedding service for semantic search
Uses sentence-transformers for generating embeddings (384 dimensions)
"""
import logging

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    # Initialize the model once (all-MiniLM-L6-v2 = 384 dimensions, matches our schema)
    # Download on first run, cached locally after that
    model = SentenceTransformer('all-MiniLM-L6-v2')
    HAS_ML = True
except ImportError:
    model = None
    HAS_ML = False
    logger.warning("sentence_transformers not installed. Semantic search and automatic embeddings generation will use zero-vectors.")

def generate_embedding(text: str) -> list:
    """
    Generate a 384-dimensional embedding for the given text.
    """
    if not HAS_ML:
        return [0.0] * 384
        
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def batch_generate_embeddings(texts: list) -> list:
    """
    Generate embeddings for multiple texts efficiently.
    """
    if not HAS_ML:
        return [[0.0] * 384 for _ in texts]
        
    embeddings = model.encode(texts, convert_to_numpy=True)
    return [emb.tolist() for emb in embeddings]
