from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from database import get_connection
from schemas import ContentConfigCreate


def _serialize_item(row: Any) -> Dict[str, Any]:
    return dict(row)


def list_content_config() -> Dict[str, List[Dict[str, Any]]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, kind, title, status, channel, published_at,
                   target_group, placement, created_by, updated_by,
                   created_at, updated_at
            FROM admin_content_config
            ORDER BY kind, updated_at DESC, id
            """
        ).fetchall()
    grouped: Dict[str, List[Dict[str, Any]]] = {
        "special_news": [],
        "advertising": [],
    }
    for row in rows:
        item = _serialize_item(row)
        grouped[item["kind"]].append(item)
    return grouped


def get_content_config_item(item_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, kind, title, status, channel, published_at,
                   target_group, placement, created_by, updated_by,
                   created_at, updated_at
            FROM admin_content_config
            WHERE id = ?
            """,
            (item_id,),
        ).fetchone()
    return _serialize_item(row) if row is not None else None


def create_content_config_item(payload: ContentConfigCreate, actor: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    item_id = str(uuid4())
    published_at = payload.published_at
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO admin_content_config (
                id, kind, title, status, channel, published_at, target_group,
                placement, created_by, updated_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                payload.kind,
                payload.title,
                payload.status,
                payload.channel,
                published_at.isoformat() if published_at else None,
                payload.target_group,
                payload.placement,
                actor,
                actor,
                now,
                now,
            ),
        )
    item = get_content_config_item(item_id)
    if item is None:
        raise RuntimeError("Created content configuration item could not be loaded")
    return item


def update_content_config_item(
    item_id: str, payload: ContentConfigCreate, actor: str
) -> Optional[Dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    published_at = payload.published_at
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE admin_content_config
            SET title = ?, status = ?, channel = ?, published_at = ?,
                target_group = ?, placement = ?, updated_by = ?, updated_at = ?
            WHERE id = ? AND kind = ?
            """,
            (
                payload.title,
                payload.status,
                payload.channel,
                published_at.isoformat() if published_at else None,
                payload.target_group,
                payload.placement,
                actor,
                now,
                item_id,
                payload.kind,
            ),
        )
        if cursor.rowcount == 0:
            return None
    return get_content_config_item(item_id)
