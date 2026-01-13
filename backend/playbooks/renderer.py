"""Playbook Renderer - renders templates with variables."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PLAYBOOKS_DIR = PROJECT_ROOT / "backend" / "playbooks" / "V1"


class PlaybookRenderer:
    """Renders playbook templates with variables."""

    def __init__(self):
        self.playbooks_dir = PLAYBOOKS_DIR

    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Load a template by ID."""
        # Search in all subdirectories
        for subdir in ["offers", "outreach", "landing", "objections"]:
            template_file = self.playbooks_dir / subdir / f"{template_id.lower()}.json"
            if template_file.exists():
                with open(template_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        
        return None

    def list_templates(self) -> Dict[str, List[str]]:
        """List all available templates by category."""
        templates = {
            "offers": [],
            "outreach": [],
            "landing": [],
            "objections": [],
        }
        
        for category in templates.keys():
            category_dir = self.playbooks_dir / category
            if category_dir.exists():
                for file in category_dir.glob("*.json"):
                    with open(file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        templates[category].append(data.get("template_id", file.stem))
        
        return templates

    def render(self, template_id: str, variables: Dict[str, Any]) -> Optional[str]:
        """Render a template with variables."""
        template = self.load_template(template_id)
        if not template:
            return None
        
        # Get the template string
        template_str = template.get("template") or template.get("body_template") or ""
        
        # Replace variables
        result = template_str
        for key, value in variables.items():
            placeholder = f"[{key}]"
            result = result.replace(placeholder, str(value))
        
        # Handle subject separately for emails
        if template.get("script_type") == "email" and "subject_template" in template:
            subject = template["subject_template"]
            for key, value in variables.items():
                subject = subject.replace(f"[{key}]", str(value))
            result = f"Subject: {subject}\n\n{result}"
        
        return result

    def render_sequence(self, template_id: str, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Render a sequence template (like follow-ups)."""
        template = self.load_template(template_id)
        if not template or "sequence" not in template:
            return []
        
        rendered = []
        for item in template["sequence"]:
            rendered_item = {
                "delay_hours": item.get("delay_hours", 0),
                "message": item.get("template", ""),
            }
            
            # Replace variables
            for key, value in variables.items():
                rendered_item["message"] = rendered_item["message"].replace(f"[{key}]", str(value))
            
            rendered.append(rendered_item)
        
        return rendered

