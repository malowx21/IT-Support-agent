from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from mcp_server.schemas import TicketCreate


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class TicketRepository:
    """Accès SQLite. Cette classe ne contient aucune logique MCP ou LLM."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys= ON")
        
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    description TEXT NOT NULL,
                    customer_email TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    closed_reason TEXT
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    ticket_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
                );
                """
            )

    def count_tickets(self) -> int:
        with self.connection() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM tickets").fetchone()
            return int(row["count"])

    def create(self, payload: TicketCreate, ticket_id: str | None = None) -> dict:
        identifier = ticket_id or str(uuid4())
        now = utc_now()
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO tickets
                    (id, subject, description, customer_email, status, priority, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'open', ?, ?, ?)
                """,
                (
                    identifier,
                    payload.subject,
                    payload.description,
                    payload.customer_email,
                    payload.priority.value,
                    now,
                    now,
                ),
            )
        self.add_audit_event(identifier, "ticket_created", "system", {"priority": payload.priority.value})
        return self.get(identifier)  # type: ignore[return-value]

    def get(self, ticket_id: str) -> dict | None:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
            return dict(row) if row else None

    def list(self, status: str | None = None, priority: str | None = None, limit: int = 20) -> list[dict]:
        conditions: list[str] = []
        values: list[object] = []
        if status:
            conditions.append("status = ?")
            values.append(status)
        if priority:
            conditions.append("priority = ?")
            values.append(priority)
        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        values.append(limit)
        query = f"SELECT * FROM tickets{where} ORDER BY created_at DESC LIMIT ?"
        with self.connection() as connection:
            return [dict(row) for row in connection.execute(query, values).fetchall()]

    def update_priority(self, ticket_id: str, priority: str) -> dict | None:
        with self.connection() as connection:
            cursor = connection.execute(
                "UPDATE tickets SET priority = ?, updated_at = ? WHERE id = ?",
                (priority, utc_now(), ticket_id),
            )
            if cursor.rowcount == 0:
                return None
        return self.get(ticket_id)

    def close(self, ticket_id: str, reason: str) -> dict | None:
        with self.connection() as connection:
            cursor = connection.execute(
                """
                UPDATE tickets
                SET status = 'closed', closed_reason = ?, updated_at = ?
                WHERE id = ? AND status != 'closed'
                """,
                (reason, utc_now(), ticket_id),
            )
            if cursor.rowcount == 0:
                return None
        return self.get(ticket_id)

    def add_audit_event(self, ticket_id: str, event_type: str, actor: str, details: dict) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO audit_events (id, ticket_id, event_type, actor, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (str(uuid4()), ticket_id, event_type, actor, json.dumps(details), utc_now()),
            )

    def audit_events(self, ticket_id: str) -> list[dict]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM audit_events WHERE ticket_id = ? ORDER BY created_at",
                (ticket_id,),
            ).fetchall()
        events = [dict(row) for row in rows]
        for event in events:
            event["details"] = json.loads(event["details"])
        return events
