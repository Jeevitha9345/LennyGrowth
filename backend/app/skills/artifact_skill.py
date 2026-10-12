import re
import uuid
import logging
from typing import Optional, Tuple
from app.models import ArtifactPayload

logger = logging.getLogger("lenny_growth.skills.artifact")

HTML_BLOCK_REGEX = re.compile(r'```(?:html|xml)\s*\n(.*?)```', re.DOTALL | re.IGNORECASE)
MARKDOWN_BLOCK_REGEX = re.compile(r'```(?:markdown|md)\s*\n(.*?)```', re.DOTALL | re.IGNORECASE)

class ArtifactSkill:
    def extract_artifact(self, text: str, user_query: str = "") -> Tuple[str, Optional[ArtifactPayload]]:
        """
        Scans text for code blocks that represent standalone UI components or documents.
        Returns cleaned text and extracted ArtifactPayload if found.
        """
        # 1. Check for HTML/CSS snippet
        html_match = HTML_BLOCK_REGEX.search(text)
        if html_match:
            html_content = html_match.group(1).strip()
            # Basic validation: ensure it has standard HTML/CSS tags
            if any(tag in html_content.lower() for tag in ["<div", "<html", "<style", "<script", "<svg", "<button", "<card"]):
                title = self._infer_title(user_query, html_content, fallback="Interactive Growth Component")
                artifact = ArtifactPayload(
                    id=str(uuid.uuid4())[:8],
                    title=title,
                    type="html",
                    content=html_content,
                    language="html",
                    summary="Interactive UI / Dashboard component rendered in sandboxed iframe."
                )
                return text, artifact

        # 2. Check for explicit Markdown document block
        md_match = MARKDOWN_BLOCK_REGEX.search(text)
        if md_match:
            md_content = md_match.group(1).strip()
            if len(md_content) > 40:
                title = self._infer_title(user_query, md_content, fallback="Growth Strategy Document")
                artifact = ArtifactPayload(
                    id=str(uuid.uuid4())[:8],
                    title=title,
                    type="markdown",
                    content=md_content,
                    language="markdown",
                    summary="Structured growth document / template."
                )
                return text, artifact

        return text, None

    def _infer_title(self, query: str, content: str, fallback: str) -> str:
        # Check for title in content
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
            
        h1_match = re.search(r'<h[12]>(.*?)</h[12]>', content, re.IGNORECASE)
        if h1_match:
            clean = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
            if clean:
                return clean

        # Infer from query
        if query:
            clean_q = re.sub(r'(create|generate|make|build|an|a|interactive|html|css|component|artifact)\s+', '', query, flags=re.IGNORECASE).strip()
            if len(clean_q) > 3:
                return clean_q[:50].title()

        return fallback

artifact_skill = ArtifactSkill()
