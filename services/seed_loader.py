"""Validated, deterministic JSON seed loading for department simulators."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError


ModelT = TypeVar("ModelT", bound=BaseModel)


def load_seed_records(
    path: Path, model: type[ModelT], *, id_field: str = "citizen_id"
) -> dict[str, ModelT]:
    """Load a JSON list, validate every row, and index it by a unique ID."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Unable to load seed file {path.name}: {exc}") from exc

    if not isinstance(payload, list):
        raise RuntimeError(f"Seed file {path.name} must contain a JSON list")

    records: dict[str, ModelT] = {}
    for index, item in enumerate(payload):
        try:
            record = model.model_validate(item)
        except ValidationError as exc:
            raise RuntimeError(
                f"Invalid record at index {index} in {path.name}: {exc}"
            ) from exc
        record_id = getattr(record, id_field)
        if record_id in records:
            raise RuntimeError(f"Duplicate {id_field} {record_id!r} in {path.name}")
        records[record_id] = record
    return records
