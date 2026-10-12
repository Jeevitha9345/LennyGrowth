import pytest
from app.retrieval.indexer import BM25Retriever, tokenize
from app.retrieval.ingest import chunk_text, parse_frontmatter

def test_tokenize():
    text = "Product-Led Growth & Retention in B2B Startups!"
    tokens = tokenize(text)
    assert "product-led" in tokens or "product" in tokens
    assert "growth" in tokens
    assert "retention" in tokens
    assert "b2b" in tokens
    assert "in" not in tokens  # Stopword removed

def test_chunk_text():
    sample = "Paragraph 1 is about product market fit.\n\nParagraph 2 is about growth loops and retention."
    chunks = chunk_text(sample, chunk_size_words=5, overlap_words=2)
    assert len(chunks) >= 2

def test_parse_frontmatter():
    sample = """---
title: Test Title
guest: Elena Verna
url: https://example.com/elena
---
This is the transcript body."""
    meta, body = parse_frontmatter(sample)
    assert meta["title"] == "Test Title"
    assert meta["guest"] == "Elena Verna"
    assert meta["url"] == "https://example.com/elena"
    assert body == "This is the transcript body."

def test_bm25_search_grounding():
    retriever = BM25Retriever()
    # Search for Elena Verna's PLG topic
    results, insufficient = retriever.search("Elena Verna reverse trial and PLG", top_k=2)
    assert not insufficient
    assert len(results) > 0
    assert any("elena" in r["guest_name"].lower() for r in results)

def test_bm25_insufficient_evidence():
    retriever = BM25Retriever()
    # Search for completely out-of-domain query
    results, insufficient = retriever.search("Quantum chromodynamics quark gluon plasma", top_k=2)
    assert insufficient
    assert len(results) == 0
