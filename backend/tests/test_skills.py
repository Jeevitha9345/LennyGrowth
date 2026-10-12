import pytest
from app.skills.ship30_skill import ship30_skill
from app.skills.artifact_skill import artifact_skill

@pytest.mark.asyncio
async def test_ship30_essay_generation():
    result = await ship30_skill.generate_essay(
        topic="Product-Led Growth Loops vs Funnels",
        target_audience="Founders and Growth Engineers",
        provider_name="mock"
    )
    assert "essay" in result
    assert "Takeaway" in result["essay"] or "Pillar" in result["essay"]
    assert result["artifact"] is not None
    assert result["artifact"].type == "essay"
    assert len(result["citations"]) > 0

def test_artifact_skill_html_extraction():
    raw_response = """Here is the calculator:
```html
<div class="card">
  <h2>PLG Calculator</h2>
  <button id="calc">Calculate</button>
</div>
```
Use it to estimate PQLs."""
    
    text, artifact = artifact_skill.extract_artifact(raw_response, user_query="Create a PLG calculator component")
    assert artifact is not None
    assert artifact.type == "html"
    assert "<button" in artifact.content
    assert "Calculator" in artifact.title

def test_artifact_skill_markdown_extraction():
    raw_response = """```markdown
# 30-Day Growth Strategy
1. Establish Sean Ellis 40% survey.
2. Build reverse trial workflow.
3. Track PQL conversion.
```"""
    text, artifact = artifact_skill.extract_artifact(raw_response, user_query="Make a growth strategy doc")
    assert artifact is not None
    assert artifact.type == "markdown"
