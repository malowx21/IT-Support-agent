import os
from pathlib import Path

from fastmcp import FastMCP

from mcp_server.repository import TicketRepository
from mcp_server.schemas import TicketCreate, TicketPriority, TicketStatus
from mcp_server.service import KnowledgeService, TicketService

from config import settings

DATABASE_PATH = Path(settings.database_path)
KNOWLEDGE_PATH = Path(settings.documents_path)


DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
repository = TicketRepository(DATABASE_PATH)
repository.initialize()
ticket_service = TicketService(repository)
knowledge_service = KnowledgeService(KNOWLEDGE_PATH,DATABASE_PATH)

mcp = FastMCP("support-server")


def seed_demo_data() -> None:
    """Crée quelques tickets seulement lorsque la base est vide."""
    if repository.count_tickets() > 0:
        return
    repository.create(
        TicketCreate(
            subject="Impossible de se connecter",
            description="Le client ne reçoit pas le lien de réinitialisation.",
            customer_email="marie@example.com",
            priority=TicketPriority.medium,
        ),
        ticket_id="ticket-123",
    )
    repository.create(
        TicketCreate(
            subject="Service indisponible",
            description="L'application affiche une erreur 503 pour toute l'équipe.",
            customer_email="admin@example.com",
            priority=TicketPriority.critical,
        ),
        ticket_id="ticket-456",
    )


seed_demo_data()


# Tools : découverts et appelés par l'agent.


@mcp.tool()
def get_ticket(ticket_id: str) -> dict:
    """Retourne un ticket de support à partir de son identifiant exact."""
    return ticket_service.get_ticket(ticket_id).model_dump(mode="json")


@mcp.tool()
def list_tickets(
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
    limit: int = 20,
) -> dict:
    """Liste les tickets, avec filtres optionnels de statut et de priorité."""
    return ticket_service.list_tickets(status=status, priority=priority, limit=limit).model_dump(mode="json")


@mcp.tool()
def create_ticket(
    subject: str,
    description: str,
    customer_email: str,
    priority: TicketPriority = TicketPriority.medium,
) -> dict:
    """Crée un nouveau ticket de support à partir d'une demande client."""
    payload = TicketCreate(
        subject=subject,
        description=description,
        customer_email=customer_email,
        priority=priority,
    )
    return ticket_service.create_ticket(payload).model_dump(mode="json")


@mcp.tool()
def update_ticket_priority(ticket_id: str, priority: TicketPriority, actor: str) -> dict:
    """Modifie la priorité. Action sensible : exiger une validation humaine avant cet appel."""
    return ticket_service.update_priority(ticket_id, priority, actor).model_dump(mode="json")


@mcp.tool()
def close_ticket(ticket_id: str, reason: str, actor: str) -> dict:
    """Ferme un ticket. Action sensible : exiger une validation humaine avant cet appel."""
    return ticket_service.close_ticket(ticket_id, reason, actor).model_dump(mode="json")


@mcp.tool()
def search_documentation(query: str, limit: int = 3) -> dict:
    """Recherche les passages de documentation utiles pour une question de support."""
    results = knowledge_service.search(query,limit)
    return {"success": True, "data": results, "error": None}


# Resources : lues explicitement par l'application cliente.


@mcp.resource("docs://{slug}")
def documentation_resource(slug: str) -> str:
    """Lit un document de la base de connaissances à partir de son slug."""
    return knowledge_service.read(slug)


@mcp.resource("ticket://{ticket_id}")
def ticket_resource(ticket_id: str) -> dict:
    """Expose le ticket et son journal d'audit en lecture seule."""
    result = ticket_service.ticket_with_audit(ticket_id)
    if result is None:
        return {"success": False, "error": {"code": "TICKET_NOT_FOUND", "message": "Ticket introuvable."}}
    return {"success": True, "data": result, "error": None}


# Prompts : modèles récupérés explicitement par le client.


@mcp.prompt()
def analyze_support_ticket(ticket_content: str) -> str:
    """Prépare une analyse structurée et prudente d'un ticket."""
    return f"""
Tu es chargé du triage d'un service de support technique.

Analyse le ticket ci-dessous sans inventer d'information :

<ticket>
{ticket_content}
</ticket>

Retourne un objet JSON avec :
- category : access, billing, bug, account ou general ;
- priority : low, medium, high ou critical ;
- summary : résumé en une phrase ;
- needs_documentation : booléen ;
- proposed_tool : nom d'outil ou null ;
- missing_information : liste de chaînes ;
- confidence : nombre entre 0 et 1.

Ne demande jamais l'exécution directe d'une action sensible.
""".strip()


@mcp.prompt()
def write_customer_response(
    customer_name: str,
    ticket_summary: str,
    solution: str,
    source_titles: str = "",
) -> str:
    """Prépare une réponse client fondée sur une solution vérifiée."""
    return f"""
Rédige en français une réponse professionnelle et concise destinée à {customer_name}.

Résumé du ticket : {ticket_summary}
Solution vérifiée : {solution}
Sources utilisées : {source_titles or 'aucune source externe'}

Contraintes :
- ne promets aucune action qui n'a pas été exécutée ;
- n'invente aucune procédure ;
- explique clairement la prochaine étape ;
- termine sans formule commerciale excessive.
""".strip()


@mcp.prompt()
def review_sensitive_action(tool_name: str, arguments_json: str, risk_reason: str) -> str:
    """Prépare le résumé présenté avant une action sensible."""
    return f"""
Examine l'action sensible suivante avant validation humaine.

Outil : {tool_name}
Arguments : {arguments_json}
Risque identifié : {risk_reason}

Présente :
1. l'effet attendu ;
2. les données modifiées ;
3. les vérifications à effectuer ;
4. une recommandation approve, reject ou edit, avec justification.

La décision finale appartient obligatoirement à l'opérateur humain.
""".strip()


if __name__ == "__main__":
    # La bannière FastMCP vérifie les mises à jour et retarde le handshake
    # dans certains environnements sans accès réseau.
    mcp.run(transport="stdio", show_banner=False)
