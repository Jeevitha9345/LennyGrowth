import pytest
from app.skills.artifact_skill import artifact_skill

def test_artifact_security_isolation_tags():
    # Verify malicious tags or scripts are encapsulated inside artifact payload without execution on server
    raw_payload = """```html
<script>
  window.parent.postMessage('steal_secrets', '*');
  localStorage.setItem('compromised', 'true');
</script>
<div>Security Test</div>
```"""
    text, artifact = artifact_skill.extract_artifact(raw_payload, "Test Security")
    assert artifact is not None
    assert artifact.type == "html"
    # Ensure content is passed as raw string to be safely isolated inside React's sandboxed iframe
    assert "localStorage" in artifact.content
    assert "Security Test" in artifact.content
