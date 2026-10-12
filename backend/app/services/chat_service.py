import time
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.models import ChatResponse, SourceCitation, ArtifactPayload
from app.retrieval.indexer import retriever
from app.providers.factory import provider_factory
from app.skills.artifact_skill import artifact_skill
from app.services.session_service import session_service

logger = logging.getLogger("lenny_growth.services.chat")

GROUNDED_SYSTEM_PROMPT = """You are "The Lenny Growth Assistant", an elite product management and growth advisor grounded in Lenny's Podcast transcripts.

Guidelines:
1. Ground your answers directly in the provided retrieved transcript context.
2. Quote or reference guests (Elena Verna, Brian Balfour, Shreyas Doshi, Rahul Vohra, etc.) and their specific terminology accurately.
3. Be structured, concise, and highly practical. Use bold key terms and bullet points.
4. If the retrieved transcripts do not contain enough evidence to answer the user's question, state clearly and honestly:
   "Based on the indexed Lenny's Podcast transcripts, there is insufficient evidence to answer this question authoritatively."
   Do NOT fabricate transcript quotes or make up advice.
5. If the user asks for code, interactive tools, calculators, wireframes, or landing pages, provide complete, functional, well-styled HTML/CSS inside ```html ``` code blocks so the sandboxed artifact viewer can render it.
"""

class ChatService:
    async def process_chat(
        self,
        db: Session,
        message: str,
        session_id: Optional[str] = None,
        provider_name: Optional[str] = None
    ) -> ChatResponse:
        start_time = time.perf_counter()
        
        # 1. Resolve or create session
        active_provider_name = provider_factory.get_active_provider_name(provider_name)
        if not session_id:
            summary = session_service.create_session(db, title="New Growth Conversation", provider=active_provider_name)
            session_id = summary.id
        else:
            session_obj = session_service.get_session(db, session_id)
            if not session_obj:
                summary = session_service.create_session(db, title="New Growth Conversation", provider=active_provider_name)
                session_id = summary.id

        # 2. Persist user message
        session_service.add_message(db, session_id=session_id, role="user", content=message)

        # 3. Retrieve relevant transcript context
        chunks, insufficient = retriever.search(
            query=message,
            top_k=settings.top_k_chunks,
            min_score=settings.min_relevance_score
        )

        citations: List[SourceCitation] = retriever.format_citations(chunks)

        # 4. Assemble context and system prompt
        context_parts = []
        for c in chunks:
            context_parts.append(
                f"[Source: {c['source_title']} | Guest: {c['guest_name']} | URL: {c.get('source_url', '')}]\n{c['content']}"
            )
        
        retrieved_context_str = "\n\n---\n\n".join(context_parts)
        if not retrieved_context_str:
            retrieved_context_str = "(No relevant transcript passages found for this query above the similarity threshold.)"

        system_prompt = (
            f"{GROUNDED_SYSTEM_PROMPT}\n\n"
            f"=== RETRIEVED TRANSCRIPTS KNOWLEDGE BASE ===\n"
            f"{retrieved_context_str}\n"
            f"============================================\n"
        )

        # 5. Fetch previous conversation messages for multi-turn context (bounded)
        db_session_data = session_service.get_session(db, session_id)
        history_messages = []
        if db_session_data and db_session_data.messages:
            # Take last 6 messages to stay strictly within low-resource memory budget
            recent_msgs = db_session_data.messages[-6:]
            for m in recent_msgs:
                history_messages.append({"role": m.role, "content": m.content})
        else:
            history_messages = [{"role": "user", "content": message}]

        # 6. Execute Model Provider
        provider = provider_factory.get_provider(active_provider_name)
        provider_resp = await provider.generate_response(
            messages=history_messages,
            system_prompt=system_prompt,
            temperature=settings.temperature,
            max_tokens=settings.max_response_tokens
        )

        reply_content = provider_resp.content
        if provider_resp.error:
            reply_content = (
                f"**Provider Notice ({active_provider_name})**: {provider_resp.error}\n\n"
                f"*(Note: You can switch active providers via environment variables or try the deterministic mock engine.)*"
            )

        # 7. Extract artifacts if present
        reply_content, artifact = artifact_skill.extract_artifact(reply_content, user_query=message)

        # 8. Persist assistant reply
        assistant_db_msg = session_service.add_message(
            db=db,
            session_id=session_id,
            role="assistant",
            content=reply_content,
            citations=citations,
            artifact=artifact
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return ChatResponse(
            session_id=session_id,
            message_id=assistant_db_msg.id,
            reply=reply_content,
            citations=citations,
            artifact=artifact,
            insufficient_evidence=insufficient,
            provider_used=active_provider_name,
            latency_ms=round(elapsed_ms, 2)
        )

chat_service = ChatService()
