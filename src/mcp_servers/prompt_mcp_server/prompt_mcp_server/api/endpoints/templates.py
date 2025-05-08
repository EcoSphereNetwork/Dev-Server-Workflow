"""
Template API endpoints for the Prompt MCP Server.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...core.template_manager import TemplateManager
from ...models.template import Template, TemplateCreate, TemplateUpdate

# Create router
router = APIRouter()

# Create logger
logger = logging.getLogger(__name__)


# Create dependencies
def get_template_manager():
    """Get template manager dependency."""
    return TemplateManager()


@router.get("", response_model=List[Template])
async def list_templates(
    template_manager: TemplateManager = Depends(get_template_manager),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[Template]:
    """List all templates."""
    return template_manager.list_templates(skip=skip, limit=limit)


@router.post("", response_model=Template, status_code=201)
async def create_template(
    template: TemplateCreate,
    template_manager: TemplateManager = Depends(get_template_manager),
) -> Template:
    """Create a new template."""
    try:
        return template_manager.create_template(template)
    except Exception as e:
        logger.exception(f"Error creating template: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{template_id}", response_model=Template)
async def get_template(
    template_id: str,
    template_manager: TemplateManager = Depends(get_template_manager),
) -> Template:
    """Get a specific template."""
    template = template_manager.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
    return template


@router.put("/{template_id}", response_model=Template)
async def update_template(
    template_id: str,
    template_update: TemplateUpdate,
    template_manager: TemplateManager = Depends(get_template_manager),
) -> Template:
    """Update a template."""
    try:
        template = template_manager.update_template(template_id, template_update)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
        return template
    except Exception as e:
        logger.exception(f"Error updating template: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{template_id}", response_model=Dict[str, str])
async def delete_template(
    template_id: str,
    template_manager: TemplateManager = Depends(get_template_manager),
) -> Dict[str, str]:
    """Delete a template."""
    if not template_manager.delete_template(template_id):
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
    return {"status": "success", "message": f"Template {template_id} deleted"}