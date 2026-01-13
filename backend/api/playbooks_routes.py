"""API routes for Playbook Library."""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from backend.playbooks.renderer import PlaybookRenderer

router = APIRouter(prefix="/playbooks", tags=["playbooks"])


@router.get("/list")
def list_playbooks() -> Dict[str, Any]:
    """List all available playbook templates."""
    renderer = PlaybookRenderer()
    templates = renderer.list_templates()
    
    return {
        "templates": templates,
        "version": "V1",
    }


@router.get("/render/{template_id}")
def render_playbook(template_id: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    """Render a playbook template with variables."""
    renderer = PlaybookRenderer()
    
    template = renderer.load_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
    
    # Check if it's a sequence template
    if template.get("sequence"):
        rendered = renderer.render_sequence(template_id, variables)
        return {"template_id": template_id, "rendered": rendered}
    else:
        rendered = renderer.render(template_id, variables)
        if not rendered:
            raise HTTPException(status_code=500, detail="Failed to render template")
        return {"template_id": template_id, "rendered": rendered}

