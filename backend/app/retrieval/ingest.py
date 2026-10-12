import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any

from app.config import settings

logger = logging.getLogger("lenny_growth.ingest")

def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    metadata = {
        "title": "Lenny's Podcast Transcript",
        "guest": "Expert Guest",
        "guest_role": "Product Leader",
        "url": "https://www.lennyspodcast.com/",
        "date": "2023-01-01",
        "topics": "Growth, Product Management",
    }
    
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_meta = parts[1]
            body = parts[2].strip()
            for line in raw_meta.strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    metadata[k.strip().lower()] = v.strip()
    return metadata, body

def chunk_text(text: str, chunk_size_words: int = 180, overlap_words: int = 40) -> List[str]:
    # Split on double newlines (paragraphs/chapters) first for natural semantic boundaries
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for paragraph in paragraphs:
        words = paragraph.split()
        if not words:
            continue
            
        if current_word_count + len(words) > chunk_size_words and current_chunk:
            combined_text = "\n\n".join(current_chunk)
            chunks.append(combined_text)
            
            # Keep overlap from the end of the previous chunk
            overlap = words[:overlap_words] if len(words) >= overlap_words else words
            current_chunk = [paragraph]
            current_word_count = len(words)
        else:
            current_chunk.append(paragraph)
            current_word_count += len(words)
            
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    return chunks

def ingest_transcripts(transcripts_dir: str = None, cache_file: str = None) -> List[Dict[str, Any]]:
    t_dir = Path(transcripts_dir or settings.transcripts_dir)
    c_file = Path(cache_file or settings.chunks_cache_file)
    c_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not t_dir.exists():
        logger.warning(f"Transcripts directory not found at: {t_dir}")
        return []
        
    all_chunks = []
    doc_files = list(t_dir.glob("*.md")) + list(t_dir.glob("*.txt"))
    logger.info(f"Found {len(doc_files)} transcript documents in {t_dir}")
    
    for file_path in doc_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(content)
            
            chunks = chunk_text(body)
            for idx, chunk in enumerate(chunks):
                chunk_id = f"{file_path.stem}_chunk_{idx}"
                all_chunks.append({
                    "id": chunk_id,
                    "source_file": file_path.name,
                    "source_title": meta.get("title", file_path.stem),
                    "guest_name": meta.get("guest", "Lenny's Guest"),
                    "source_url": meta.get("url", "https://www.lennyspodcast.com/"),
                    "chunk_index": idx,
                    "content": chunk,
                    "word_count": len(chunk.split()),
                    "topics": meta.get("topics", "")
                })
        except Exception as e:
            logger.error(f"Error processing transcript {file_path}: {e}")
            
    # Save processed cache
    with open(c_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Successfully indexed and cached {len(all_chunks)} chunks to {c_file}")
    return all_chunks

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingest_transcripts()
