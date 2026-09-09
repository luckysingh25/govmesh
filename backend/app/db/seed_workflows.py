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
    existing_records = {w.name: w for w in db.query(WorkflowDefinition).all()}
    needs_commit = False
    for defn in DEFAULT_DEFINITIONS:
        name = defn["name"]
        if name not in existing_records:
            db.add(WorkflowDefinition(**defn))
            needs_commit = True
            logger.info("seeded_workflow_definition name=%s", name)
        else:
            rec = existing_records[name]
            if rec.description != defn["description"] or rec.steps != list(defn["steps"]):
                rec.description = defn["description"]
                rec.steps = list(defn["steps"])
                needs_commit = True

    if needs_commit:
        db.commit()
