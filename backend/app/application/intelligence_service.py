import re
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.intelligence import SystemSchema, SchemaField, MappingSuggestion, ImpactAnalysis

logger = logging.getLogger(__name__)

# Basic canonical target fields in GovMesh for mapping suggestions
TARGET_FIELDS = [
    "citizen.citizen_id",
    "citizen.name",
    "citizen.address",
    "citizen.date_of_birth",
    "property.property_id",
    "property.property_type",
    "property.owner_name",
    "property.address",
]

def normalize_string(name: str) -> str:
    """Convert camelCase, PascalCase, or kebab-case to snake_case."""
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    name = name.replace('-', '_')
    return name.lower()

def compute_similarity(source: str, target: str) -> float:
    """Super naive similarity for demo purposes. In reality, use embeddings."""
    source_words = set(source.split('_'))
    target_words = set(target.replace('.', '_').split('_'))
    intersection = source_words.intersection(target_words)
    if not intersection:
        return 0.1
    return len(intersection) / max(len(source_words), len(target_words))

def extract_fields_from_schema(schema_content: Dict[str, Any], prefix="") -> List[Dict[str, str]]:
    """Flatten a basic JSON schema representation."""
    fields = []
    # If it's a standard JSON Schema properties dict
    properties = schema_content.get("properties", schema_content)
    
    for key, val in properties.items():
        if isinstance(val, dict):
            if "type" in val and val["type"] != "object":
                fields.append({
                    "name": f"{prefix}{key}",
                    "type": val.get("type", "string"),
                    "required": "true" if key in schema_content.get("required", []) else "false"
                })
            elif "properties" in val:
                fields.extend(extract_fields_from_schema(val, prefix=f"{prefix}{key}."))
            else:
                fields.append({"name": f"{prefix}{key}", "type": "object", "required": "false"})
        else:
            fields.append({"name": f"{prefix}{key}", "type": "string", "required": "false"})
    return fields


class IntelligenceService:
    """Core engine for interoperability schema parsing, mapping, and impact analysis."""

    def ingest_schema(self, db: Session, system_name: str, schema_content: Dict[str, Any]) -> SystemSchema:
        """Upload a new schema, detect changes, and generate mappings/impact analysis."""
        # Find active schema
        old_schema = db.query(SystemSchema).filter_by(system_name=system_name, status="active").first()
        
        new_version = 1
        if old_schema:
            new_version = old_schema.version + 1
            old_schema.status = "superseded"
            db.commit()

        new_schema = SystemSchema(
            system_name=system_name,
            version=new_version,
            content=schema_content,
            status="active"
        )
        db.add(new_schema)
        db.commit()
        db.refresh(new_schema)

        # 1. Parse fields
        extracted = extract_fields_from_schema(schema_content)
        new_fields = []
        for ext in extracted:
            field = SchemaField(
                schema_id=new_schema.id,
                field_name=ext["name"],
                normalized_name=normalize_string(ext["name"]),
                field_type=ext["type"],
                is_required=ext["required"]
            )
            db.add(field)
            new_fields.append(field)
        
        db.commit()
        for f in new_fields:
            db.refresh(f)

        # 2. Generate Semantic Mappings
        self._generate_mapping_suggestions(db, new_fields)

        # 3. Analyze Impact if version > 1
        if old_schema:
            self._analyze_impact(db, system_name, old_schema, new_schema)

        return new_schema

    def _generate_mapping_suggestions(self, db: Session, fields: List[SchemaField]):
        """Analyze fields and suggest mappings."""
        for field in fields:
            best_target = None
            best_score = 0.0
            
            # Very basic hardcoded semantic rules for the demo scenario
            if "owner" in field.normalized_name and "name" in field.normalized_name:
                best_target = "citizen.name"
                best_score = 0.95
            elif "address" in field.normalized_name:
                best_target = "citizen.address"
                best_score = 0.90
            else:
                # Fallback to naive similarity
                for target in TARGET_FIELDS:
                    score = compute_similarity(field.normalized_name, target)
                    if score > best_score:
                        best_score = score
                        best_target = target

            if best_score > 0.4 and best_target:
                mapping_type = "exact" if best_score > 0.98 else "semantic"
                if "property" in field.normalized_name and best_target == "citizen.name":
                    mapping_type = "transformation-required"

                suggestion = MappingSuggestion(
                    source_field_id=field.id,
                    target_field=best_target,
                    confidence_score=best_score,
                    mapping_type=mapping_type,
                    status="pending"
                )
                db.add(suggestion)
        
        db.commit()

    def _analyze_impact(self, db: Session, system_name: str, old_schema: SystemSchema, new_schema: SystemSchema):
        """Compare two schemas and determine what broke."""
        old_fields = {f.field_name: f for f in old_schema.fields}
        new_fields = {f.field_name: f for f in new_schema.fields}

        removed = []
        added = []
        renamed = [] # Naive rename detection based on similarity
        
        for name, field in old_fields.items():
            if name not in new_fields:
                # Did it get renamed?
                renamed_to = None
                for new_name, new_f in new_fields.items():
                    if new_name not in old_fields and compute_similarity(field.normalized_name, new_f.normalized_name) > 0.55:
                        renamed_to = new_name
                        break
                
                if renamed_to:
                    renamed.append({"old": name, "new": renamed_to, "reason": "High semantic similarity"})
                else:
                    removed.append(name)

        for name, field in new_fields.items():
            if name not in old_fields and not any(r["new"] == name for r in renamed):
                added.append(name)

        affected_workflows = []
        if removed or renamed:
            affected_workflows.append({
                "workflow": "Business Registration",
                "step": f"{system_name.capitalize()} Integration",
                "risk_level": "High - Breaking Change",
                "detail": f"Field mapping for {removed or [r['old'] for r in renamed]} is now broken."
            })

        analysis = {
            "changes": {
                "added": added,
                "removed": removed,
                "renamed": renamed
            },
            "affected_workflows": affected_workflows,
            "impact_summary": f"{len(removed)} fields removed, {len(renamed)} fields renamed, {len(added)} fields added."
        }

        impact = ImpactAnalysis(
            system_name=system_name,
            old_version=old_schema.version,
            new_version=new_schema.version,
            analysis_result=analysis
        )
        db.add(impact)
        db.commit()

    def approve_suggestion(self, db: Session, suggestion_id: int):
        sug = db.query(MappingSuggestion).filter_by(id=suggestion_id).first()
        if sug:
            sug.status = "approved"
            db.commit()
        return sug

    def reject_suggestion(self, db: Session, suggestion_id: int):
        sug = db.query(MappingSuggestion).filter_by(id=suggestion_id).first()
        if sug:
            sug.status = "rejected"
            db.commit()
        return sug
