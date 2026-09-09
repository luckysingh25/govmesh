"""Redis Streams event bus for workflow orchestration.

Provides publish/consume primitives for the step-execution pipeline.
Streams:
  - workflow:steps   — new steps ready to execute
  - workflow:retries — steps scheduled for retry after backoff
"""

import json
import logging
from typing import Optional

from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

STEP_STREAM = "workflow:steps"
RETRY_STREAM = "workflow:retries"
CONSUMER_GROUP = "workflow-workers"


def _ensure_stream_and_group(r, stream: str, group: str) -> None:
    """Create the consumer group (and implicitly the stream) if missing."""
    try:
        r.xgroup_create(stream, group, id="0", mkstream=True)
    except Exception:
        # Group already exists — safe to ignore
        pass


def publish_step_event(step_instance_id: int, action: str = "execute") -> bool:
    """Add a step-execution message to the steps stream.

    Returns True on success, False if Redis is unreachable.
    """
    try:
        r = get_redis_client()
        _ensure_stream_and_group(r, STEP_STREAM, CONSUMER_GROUP)
        r.xadd(STEP_STREAM, {
            "step_instance_id": str(step_instance_id),
            "action": action,
        })
        logger.info("published_step_event step_instance_id=%s action=%s", step_instance_id, action)
        return True
    except Exception:
        logger.warning("redis_publish_failed step_instance_id=%s — falling back to sync", step_instance_id)
        return False


def publish_retry_event(step_instance_id: int, execute_after: str) -> bool:
    """Add a retry message to the retries stream.

    `execute_after` is an ISO-8601 timestamp string.
    Returns True on success, False if Redis is unreachable.
    """
    try:
        r = get_redis_client()
        _ensure_stream_and_group(r, RETRY_STREAM, CONSUMER_GROUP)
        r.xadd(RETRY_STREAM, {
            "step_instance_id": str(step_instance_id),
            "execute_after": execute_after,
        })
        logger.info("published_retry_event step_instance_id=%s execute_after=%s", step_instance_id, execute_after)
        return True
    except Exception:
        logger.warning("redis_retry_publish_failed step_instance_id=%s", step_instance_id)
        return False


def redis_available() -> bool:
    """Quick check if Redis is reachable."""
    try:
        r = get_redis_client()
        return bool(r.ping())
    except Exception:
        return False
