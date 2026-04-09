"""
Embedding service for semantic search
Uses sentence-transformers for generating embeddings (384 dimensions)
"""
from sentence_transformers import SentenceTransformer

# Initialize the model once (all-MiniLM-L6-v2 = 384 dimensions, matches our schema)
# Download on first run, cached locally after that
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> list:
    """
    Generate a 384-dimensional embedding for the given text.
    
    Args:
        text: The text to embed (e.g., food name or description)
    
    Returns:
        List of 384 floats representing the embedding
    """
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def batch_generate_embeddings(texts: list) -> list:
    """
    Generate embeddings for multiple texts efficiently.
    
    Args:
        texts: List of texts to embed
    
    Returns:
        List of embeddings
    """
    embeddings = model.encode(texts, convert_to_numpy=True)
    return [emb.tolist() for emb in embeddings]
