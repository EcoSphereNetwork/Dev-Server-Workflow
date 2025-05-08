"""
Template manager for the Prompt MCP Server.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from promplate import Template as PromplateTemplate

from ..models.template import Template, TemplateCreate, TemplateUpdate
from .config import settings

# Create logger
logger = logging.getLogger(__name__)


class TemplateManager:
    """Template manager class."""

    def __init__(self):
        """Initialize the template manager."""
        self.templates: Dict[str, Template] = {}
        self.promplate_templates: Dict[str, PromplateTemplate] = {}
        self.templates_dir = Path(settings.TEMPLATES_DIRECTORY)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._load_templates()

    def _load_templates(self) -> None:
        """Load templates from the templates directory."""
        try:
            # Load templates from JSON file if it exists
            templates_file = self.templates_dir / "templates.json"
            if templates_file.exists():
                with open(templates_file, "r") as f:
                    templates_data = json.load(f)
                    for template_data in templates_data:
                        template = Template(**template_data)
                        self.templates[template.id] = template
                        self.promplate_templates[template.id] = PromplateTemplate(template.content)
            
            # Load templates from individual files
            for file_path in self.templates_dir.glob("*.j2"):
                template_id = file_path.stem
                if template_id not in self.templates:
                    with open(file_path, "r") as f:
                        content = f.read()
                        template = Template(
                            id=template_id,
                            name=template_id,
                            content=content,
                        )
                        self.templates[template.id] = template
                        self.promplate_templates[template.id] = PromplateTemplate(content)
            
            logger.info(f"Loaded {len(self.templates)} templates")
        except Exception as e:
            logger.exception(f"Error loading templates: {e}")

    def _save_templates(self) -> None:
        """Save templates to the templates directory."""
        try:
            # Save templates to JSON file
            templates_file = self.templates_dir / "templates.json"
            with open(templates_file, "w") as f:
                json.dump([template.model_dump() for template in self.templates.values()], f, indent=2)
            
            # Save templates to individual files
            for template_id, template in self.templates.items():
                file_path = self.templates_dir / f"{template_id}.j2"
                with open(file_path, "w") as f:
                    f.write(template.content)
            
            logger.info(f"Saved {len(self.templates)} templates")
        except Exception as e:
            logger.exception(f"Error saving templates: {e}")

    def list_templates(self, skip: int = 0, limit: int = 100) -> List[Template]:
        """
        List all templates.

        Args:
            skip: Number of templates to skip
            limit: Maximum number of templates to return

        Returns:
            List of templates
        """
        return list(self.templates.values())[skip:skip + limit]

    def get_template(self, template_id: str) -> Optional[Template]:
        """
        Get a template by ID.

        Args:
            template_id: The template ID

        Returns:
            The template if found, None otherwise
        """
        return self.templates.get(template_id)

    def get_promplate_template(self, template_id: str) -> Optional[PromplateTemplate]:
        """
        Get a Promplate template by ID.

        Args:
            template_id: The template ID

        Returns:
            The Promplate template if found, None otherwise
        """
        return self.promplate_templates.get(template_id)

    def create_template(self, template_create: TemplateCreate) -> Template:
        """
        Create a new template.

        Args:
            template_create: The template creation data

        Returns:
            The created template
        """
        # Create template
        template = Template(
            name=template_create.name,
            description=template_create.description,
            content=template_create.content,
            type=template_create.type,
            metadata=template_create.metadata or {},
            tags=template_create.tags or [],
        )

        # Add template
        self.templates[template.id] = template
        self.promplate_templates[template.id] = PromplateTemplate(template.content)

        # Save templates
        self._save_templates()

        return template

    def update_template(self, template_id: str, template_update: TemplateUpdate) -> Optional[Template]:
        """
        Update a template.

        Args:
            template_id: The template ID
            template_update: The template update data

        Returns:
            The updated template if found, None otherwise
        """
        # Get template
        template = self.templates.get(template_id)
        if not template:
            return None

        # Update template
        if template_update.name is not None:
            template.name = template_update.name
        if template_update.description is not None:
            template.description = template_update.description
        if template_update.content is not None:
            template.content = template_update.content
            self.promplate_templates[template.id] = PromplateTemplate(template.content)
        if template_update.type is not None:
            template.type = template_update.type
        if template_update.metadata is not None:
            template.metadata = template_update.metadata
        if template_update.tags is not None:
            template.tags = template_update.tags
        
        template.updated_at = datetime.utcnow()

        # Save templates
        self._save_templates()

        return template

    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.

        Args:
            template_id: The template ID

        Returns:
            True if the template was deleted, False otherwise
        """
        # Check if template exists
        if template_id not in self.templates:
            return False

        # Delete template
        del self.templates[template_id]
        del self.promplate_templates[template_id]

        # Save templates
        self._save_templates()

        return True

    def render_template(self, template_id: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.

        Args:
            template_id: The template ID
            context: The context to render the template with

        Returns:
            The rendered template
        """
        # Get template
        template = self.promplate_templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Render template
        return template.render(**context)