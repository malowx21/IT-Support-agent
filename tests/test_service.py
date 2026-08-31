from mcp_server.repository import TicketRepository
from mcp_server.schemas import TicketCreate, TicketPriority
from mcp_server.service import KnowledgeService, TicketService


def make_service(tmp_path) -> TicketService:
    repository = TicketRepository(tmp_path / "test.db")
    repository.initialize()
    return TicketService(repository)


def create_sample(service: TicketService) -> str:
    result = service.create_ticket(
        TicketCreate(
            subject="Erreur de connexion",
            description="Le client ne peut plus se connecter.",
            customer_email="client@example.com",
            priority=TicketPriority.medium,
        )
    )
    assert result.success
    return result.data["id"]


def test_ticket_lifecycle_is_persisted_and_audited(tmp_path):
    service = make_service(tmp_path)
    ticket_id = create_sample(service)

    updated = service.update_priority(ticket_id, TicketPriority.high, "operator@example.com")
    closed = service.close_ticket(ticket_id, "Incident résolu", "operator@example.com")
    snapshot = service.ticket_with_audit(ticket_id)

    assert updated.success
    assert updated.data["priority"] == "high"
    assert closed.success
    assert closed.data["status"] == "closed"
    assert [event["event_type"] for event in snapshot["audit_events"]] == [
        "ticket_created",
        "priority_updated",
        "ticket_closed",
    ]


def test_closed_ticket_cannot_be_modified(tmp_path):
    service = make_service(tmp_path)
    ticket_id = create_sample(service)
    service.close_ticket(ticket_id, "Résolu", "operator@example.com")

    result = service.update_priority(ticket_id, TicketPriority.critical, "operator@example.com")

    assert not result.success
    assert result.error.code == "TICKET_CLOSED"


def test_missing_ticket_returns_structured_error(tmp_path):
    service = make_service(tmp_path)

    result = service.get_ticket("ticket-unknown")

    assert not result.success
    assert result.error.code == "TICKET_NOT_FOUND"


def test_knowledge_search_returns_relevant_document(
    monkeypatch,
    tmp_path,
):
    expected_results = [
        {
            "document_id": "refund-policy",
            "content": "Politique de remboursement",
            "score": 0.9,
        }
    ]

    def fake_retrieve_docs(
        query,
        limit,
        database_path,
    ):
        assert query == (
            "Comment demander un remboursement ?"
        )
        assert limit == 3
        return expected_results

    monkeypatch.setattr(
        "mcp_server.service.retrieve_docs",
        fake_retrieve_docs,
    )

    service = KnowledgeService(
        knowledge_directory="mcp_server/knowledge",
        database_path=tmp_path / "test.db",
    )

    results = service.search(
        "Comment demander un remboursement ?"
    )

    assert results == expected_results

