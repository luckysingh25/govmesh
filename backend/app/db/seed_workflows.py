"""Seed the workflow_definitions table with default templates."""

import logging
from sqlalchemy.orm import Session
from app.models.workflow import WorkflowDefinition

logger = logging.getLogger(__name__)

DEFAULT_DEFINITIONS = [
    {
        "name": "business_registration",
        "description": "Business Registration — sequential department verification pipeline",
        "steps": ["identity", "property", "municipality", "tax"],
    },
]


def seed_workflow_definitions(db: Session) -> None:
    """Insert default WorkflowDefinition rows if they don't already exist."""
    for defn in DEFAULT_DEFINITIONS:
        existing = db.query(WorkflowDefinition).filter_by(name=defn["name"]).first()
        if existing is None:
            record = WorkflowDefinition(**defn)
            db.add(record)
            logger.info("seeded_workflow_definition name=%s", defn["name"])
    db.commit()
