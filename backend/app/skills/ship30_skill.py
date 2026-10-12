import uuid
import logging
from typing import Dict, Any, List

from app.models import ArtifactPayload, SourceCitation
from app.retrieval.indexer import retriever
from app.providers.factory import provider_factory

logger = logging.getLogger("lenny_growth.skills.ship30")

SHIP30_SYSTEM_PROMPT = """You are an elite Ship 30 for 30 atomic essay writer and Growth Lead.
Your goal is to write an approximately 800-1,250 word high-impact growth essay grounded STRICTLY in Lenny's Podcast transcripts.

Structure rules:
1. **Title & 1-Sentence Takeaway**: Catchy title + a bold 1-sentence synthesis.
2. **The Hook**: Open with an engaging problem within 3 sentences (e.g. why funnels fail, why PMs burn out).
3. **Core Pillars**: Break down the topic into 3-4 structured, skimmable sections with bold subheaders and bullet points.
4. **Transcript Evidence vs Strategic Inference Table**: An explicit markdown table clearly separating what the podcast guest said vs the derived tactical inference.
5. **Actionable 24-Hour Checklist**: 3-4 immediate steps the reader can take today.

Grounding rules:
- Mention the guest by name and quote or reference their specific frameworks.
- Do NOT hallucinate advice not grounded in the provided transcripts.
- If information is missing, state it explicitly in the table.
"""

class Ship30Skill:
    async def generate_essay(
        self,
        topic: str,
        target_audience: str = "Product Managers and Growth Engineers",
        focus_guest: str = None,
        provider_name: str = None
    ) -> Dict[str, Any]:
        # 1. Retrieve relevant transcript chunks
        search_query = f"{topic} {focus_guest or ''}".strip()
        chunks, insufficient = retriever.search(search_query, top_k=4)
        
        context_blocks = []
        for c in chunks:
            context_blocks.append(
                f"[Source: {c['source_title']} - Guest: {c['guest_name']}]\n{c['content']}"
            )
        context_str = "\n\n---\n\n".join(context_blocks)

        system_prompt = (
            f"{SHIP30_SYSTEM_PROMPT}\n\n"
            f"Target Audience: {target_audience}\n\n"
            f"=== RETRIEVED TRANSCRIPTS ===\n{context_str}\n==============================\n"
        )

        messages = [
            {"role": "user", "content": f"Write a comprehensive Ship 30 for 30 essay on: {topic}"}
        ]

        provider = provider_factory.get_provider(provider_name)
        active_name = provider_factory.get_active_provider_name(provider_name)
        
        response = await provider.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=1500
        )

        citations = retriever.format_citations(chunks)

        artifact = ArtifactPayload(
            id=str(uuid.uuid4())[:8],
            title=f"Ship 30 Essay: {topic[:50]}",
            type="essay",
            content=response.content,
            language="markdown",
            summary=f"Ship 30 for 30 structured essay on {topic}"
        )

        return {
            "essay": response.content,
            "artifact": artifact,
            "citations": citations,
            "provider_used": active_name,
            "latency_ms": response.latency_ms,
            "error": response.error
        }

ship30_skill = Ship30Skill()
