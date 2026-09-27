import json
import math
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.vector_embeddings import DocumentChunk
from app.core.config import settings

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)

def simple_keyword_score(query: str, text: str) -> float:
    q_words = set(query.lower().split())
    t_words = set(text.lower().split())
    if not q_words:
        return 0.0
    overlap = q_words.intersection(t_words)
    return len(overlap) / len(q_words)

class RAGEngine:
    @staticmethod
    async def index_document_chunks(
        db: AsyncSession, 
        user_id: str, 
        document_id: str, 
        chunks: List[str]
    ):
        for idx, chunk_text in enumerate(chunks):
            # In production, can call Google Gemini embed_content API or fallback
            chunk = DocumentChunk(
                user_id=user_id,
                document_id=document_id,
                chunk_index=idx,
                content=chunk_text,
                embedding_json=None, # populated when embedder available
                metadata_json=json.dumps({"length": len(chunk_text)})
            )
            db.add(chunk)
        await db.commit()

    @staticmethod
    async def search_relevant_chunks(
        db: AsyncSession,
        user_id: str,
        query: str,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        stmt = select(DocumentChunk).where(DocumentChunk.user_id == user_id)
        result = await db.execute(stmt)
        all_chunks = result.scalars().all()

        scored = []
        for c in all_chunks:
            score = simple_keyword_score(query, c.content)
            scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "chunk_id": item[1].id,
                "document_id": item[1].document_id,
                "content": item[1].content,
                "relevance_score": item[0]
            }
            for item in scored[:top_k] if item[0] > 0.05
        ]
