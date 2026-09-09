"""Seed the workflow_definitions table with default templates."""

import logging
from sqlalchemy.orm import Session
from app.core.service_types import WORKFLOW_DEFINITIONS
from app.models.workflow import WorkflowDefinition

logger = logging.getLogger(__name__)

DEFAULT_DEFINITIONS = [
    {"name": name, **definition}
    for name, definition in WORKFLOW_DEFINITIONS.items()
]


def seed_workflow_definitions(db: Session) -> None:
    """Insert default WorkflowDefinition rows if they don't already exist."""
    for defn in DEFAULT_DEFINITIONS:
        existing = db.query(WorkflowDefinition).filter_by(name=defn["name"]).first()
        if existing is None:
            record = WorkflowDefinition(**defn)
            db.add(record)
            logger.info("seeded_workflow_definition name=%s", defn["name"])
        else:
            existing.description = defn["description"]
            existing.steps = list(defn["steps"])
    db.commit()
