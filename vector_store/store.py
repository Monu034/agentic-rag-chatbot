import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class VectorStore:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks: List[Dict] = []
        
    def add_chunks(self, chunks: List[Dict]):
        if not chunks:
            return
        texts = [chunk["text"] for chunk in chunks]
        # Batch encode with multi-threading enabled
        embeddings = self.model.encode(
            texts, 
            batch_size=32, 
            show_progress_bar=False, 
            convert_to_numpy=True
        )
        self.index.add(embeddings.astype('float32'))
        self.chunks.extend(chunks)
        
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        if self.index.ntotal == 0:
            return []
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.chunks):
                chunk_data = self.chunks[idx].copy()
                chunk_data["distance"] = float(distances[0][i])
                results.append(chunk_data)
        return results
