import logging
from sqlalchemy.orm import Session
from app.models.data_lineage import DataLineage
from typing import Optional, List

logger = logging.getLogger(__name__)

class DataLineageService:
    """Records field-level data flow and mappings across systems."""

    def record_lineage(
        self,
        db: Session,
        correlation_id: str,
        source_system: str,
        source_field: str,
        destination_system: str,
        destination_field: str,
        transformation: Optional[str] = None,
        service_request_id: Optional[str] = None,
        commit: bool = True,
    ) -> DataLineage:
        record = DataLineage(
            correlation_id=correlation_id,
            service_request_id=service_request_id,
            source_system=source_system,
            source_field=source_field,
            destination_system=destination_system,
            destination_field=destination_field,
            transformation=transformation,
        )
        db.add(record)
        if commit:
            db.commit()
            db.refresh(record)
        
        logger.info(
            "data_lineage_recorded correlation_id=%s source=%s.%s dest=%s.%s",
            correlation_id, source_system, source_field, destination_system, destination_field
        )
        return record

    def get_lineage_by_correlation(self, db: Session, correlation_id: str) -> List[DataLineage]:
        return (
            db.query(DataLineage)
            .filter(DataLineage.correlation_id == correlation_id)
            .order_by(DataLineage.created_at.asc())
            .all()
        )
