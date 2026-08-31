# Support Copilot — couche MCP

Cette première étape contient un serveur MCP réellement relié à SQLite, mais pas encore l'agent LangGraph.

## Primitives exposées

- Tools : `get_ticket`, `list_tickets`, `create_ticket`, `update_ticket_priority`, `close_ticket`, `search_documentation`
- Resources : `docs://{slug}`, `ticket://{ticket_id}`
- Prompts : `analyze_support_ticket`, `write_customer_response`, `review_sensitive_action`

`update_ticket_priority` et `close_ticket` sont des actions sensibles. Le futur graphe LangGraph devra les intercepter et obtenir une décision humaine avant de laisser `ToolNode` les exécuter.

## Exécution

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python inspect_mcp.py
pytest
```

Le transport `stdio` réserve la sortie standard au protocole. Ne pas ajouter de `print()` dans `mcp_server/server.py`.
