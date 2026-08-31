import re
from pathlib import Path

from mcp_server.repository import TicketRepository
from mcp_server.schemas import TicketCreate, TicketPriority, TicketStatus, ToolError, ToolResult
from rag.retriever import retrieve_docs

class TicketService:
    """Règles métier utilisées par MCP aujourd'hui et FastAPI plus tard."""

    def __init__(self, repository: TicketRepository) -> None:
        self.repository = repository

    def get_ticket(self, ticket_id: str) -> ToolResult:
        ticket = self.repository.get(ticket_id)
        if ticket is None:
            return self._not_found(ticket_id)
        return ToolResult(success=True, data=ticket)

    def list_tickets(
        self,
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        limit: int = 20,
    ) -> ToolResult:
        tickets = self.repository.list(
            status=status.value if status else None,
            priority=priority.value if priority else None,
            limit=max(1, min(limit, 100)),
        )
        return ToolResult(success=True, data=tickets)

    def create_ticket(self, payload: TicketCreate) -> ToolResult:
        return ToolResult(success=True, data=self.repository.create(payload))

    def update_priority(self, ticket_id: str, priority: TicketPriority, actor: str) -> ToolResult:
        current = self.repository.get(ticket_id)
        if current is None:
            return self._not_found(ticket_id)
        if current["status"] == TicketStatus.closed.value:
            return ToolResult(
                success=False,
                error=ToolError(code="TICKET_CLOSED", message="La priorité d'un ticket fermé ne peut pas être modifiée."),
            )
        updated = self.repository.update_priority(ticket_id, priority.value)
        self.repository.add_audit_event(
            ticket_id,
            "priority_updated",
            actor,
            {"previous": current["priority"], "new": priority.value},
        )
        return ToolResult(success=True, data=updated)

    def close_ticket(self, ticket_id: str, reason: str, actor: str) -> ToolResult:
        current = self.repository.get(ticket_id)
        if current is None:
            return self._not_found(ticket_id)
        if current["status"] == TicketStatus.closed.value:
            return ToolResult(
                success=False,
                error=ToolError(code="ALREADY_CLOSED", message=f"Le ticket {ticket_id} est déjà fermé."),
            )
        updated = self.repository.close(ticket_id, reason)
        self.repository.add_audit_event(ticket_id, "ticket_closed", actor, {"reason": reason})
        return ToolResult(success=True, data=updated)

    def ticket_with_audit(self, ticket_id: str) -> dict | None:
        ticket = self.repository.get(ticket_id)
        if ticket is None:
            return None
        return {"ticket": ticket, "audit_events": self.repository.audit_events(ticket_id)}

    @staticmethod
    def _not_found(ticket_id: str) -> ToolResult:
        return ToolResult(
            success=False,
            error=ToolError(code="TICKET_NOT_FOUND", message=f"Le ticket {ticket_id} n'existe pas."),
        )


class KnowledgeService:
    def __init__(self, knowledge_directory: str | Path, database_path: str|Path) -> None:
        self.knowledge_directory = Path(knowledge_directory)
        self.database_path = Path(database_path)
        
    def read(self, slug: str) -> str:
        path = self.knowledge_directory / f"{slug}.md"
        if not path.is_file():
            raise FileNotFoundError(f"Document inconnu : {slug}")
        return path.read_text(encoding="utf-8")

    def search(self, query: str, limit: int = 3) -> list[dict]:

        return retrieve_docs(query,limit,database_path=self.database_path)
