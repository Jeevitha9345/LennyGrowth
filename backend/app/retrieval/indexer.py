import json
import logging
import math
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

from app.config import settings
from app.models import SourceCitation
from app.retrieval.ingest import ingest_transcripts

logger = logging.getLogger("lenny_growth.indexer")

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "can", "did", "do", "does", "doing", "don", "down", "during", "each", "few", "for", 
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", 
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", 
    "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", 
    "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she", 
    "should", "so", "some", "such", "t", "than", "that", "the", "their", "theirs", "them", 
    "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too", 
    "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", 
    "while", "who", "whom", "why", "will", "with", "you", "your", "yours", "yourself", "yourselves"
}

def tokenize(text: str) -> List[str]:
    # Extract lowercased alphanumeric tokens
    tokens = re.findall(r'\b[a-zA-Z0-9_\-\$]+\b', text.lower())
    return [t for t in tokens if len(t) > 1 and t not in STOPWORDS]

class BM25Retriever:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[Dict[str, Any]] = []
        self.doc_len: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_term_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self.is_indexed: bool = False
        self._load_or_index()

    def _load_or_index(self):
        cache_path = Path(settings.chunks_cache_file)
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                logger.info(f"Loaded {len(self.chunks)} chunks from cache: {cache_path}")
            except Exception as e:
                logger.warning(f"Failed to load cache ({e}), re-ingesting...")
                self.chunks = ingest_transcripts()
        else:
            self.chunks = ingest_transcripts()

        if not self.chunks:
            logger.warning("No transcript chunks available for indexing.")
            return

        self._build_index()

    def _build_index(self):
        N = len(self.chunks)
        if N == 0:
            return

        total_len = 0
        self.doc_len = []
        self.doc_term_freqs = []
        df: Dict[str, int] = {}

        for chunk in self.chunks:
            tokens = tokenize(chunk["content"])
            d_len = len(tokens)
            self.doc_len.append(d_len)
            total_len += d_len

            tf = {}
            for token in tokens:
                tf[token] = tf.get(token, 0) + 1
            self.doc_term_freqs.append(tf)

            for token in tf.keys():
                df[token] = df.get(token, 0) + 1

        self.avg_doc_len = total_len / N if N > 0 else 1.0

        # Calculate Okapi BM25 Inverse Document Frequency (IDF)
        self.idf = {}
        for token, freq in df.items():
            # Standard smoothed BM25 IDF formula
            self.idf[token] = math.log(1.0 + (N - freq + 0.5) / (freq + 0.5))

        self.is_indexed = True
        logger.info(f"BM25 index built successfully with {N} documents and {len(self.idf)} unique vocabulary terms.")

    def search(self, query: str, top_k: int = 4, min_score: float = None) -> Tuple[List[Dict[str, Any]], bool]:
        if not self.is_indexed or not self.chunks:
            return [], True

        threshold = min_score if min_score is not None else settings.min_relevance_score
        query_tokens = tokenize(query)
        if not query_tokens:
            return [], True

        scores = []
        for i, chunk in enumerate(self.chunks):
            score = 0.0
            doc_tf = self.doc_term_freqs[i]
            d_len = self.doc_len[i]

            for token in query_tokens:
                if token not in doc_tf:
                    continue
                tf = doc_tf[token]
                idf_val = self.idf.get(token, 0.0)
                # BM25 term weighting
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (d_len / self.avg_doc_len))
                score += idf_val * (numerator / denominator)

            # Boost if guest name or title matches directly in query
            guest_lower = chunk["guest_name"].lower()
            title_lower = chunk["source_title"].lower()
            for token in query_tokens:
                if token in guest_lower:
                    score += 0.4
                if token in title_lower:
                    score += 0.2

            if score > 0:
                scores.append((score, chunk))

        scores.sort(key=lambda x: x[0], reverse=True)

        if not scores or scores[0][0] < threshold:
            logger.info(f"Query '{query}' produced top score {scores[0][0] if scores else 0.0:.3f} below threshold {threshold:.3f}.")
            return [], True  # insufficient evidence

        top_results = []
        for score, chunk in scores[:top_k]:
            res = dict(chunk)
            res["score"] = round(score, 4)
            top_results.append(res)

        return top_results, False

    def format_citations(self, results: List[Dict[str, Any]]) -> List[SourceCitation]:
        citations = []
        for r in results:
            # Create a 2-sentence snippet
            raw_text = r["content"]
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', raw_text) if s.strip()]
            snippet = " ".join(sentences[:2]) if sentences else raw_text[:200]
            if len(snippet) > 280:
                snippet = snippet[:277] + "..."

            citations.append(SourceCitation(
                id=r["id"],
                source_title=r["source_title"],
                guest_name=r["guest_name"],
                source_url=r.get("source_url"),
                chunk_index=r["chunk_index"],
                score=r["score"],
                snippet=snippet
            ))
        return citations

# Singleton instance
retriever = BM25Retriever()
