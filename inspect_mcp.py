"""Client de diagnostic : vérifie les trois primitives sans lancer LangGraph."""

import asyncio

from fastmcp import Client

from mcp_server.server import mcp


async def main() -> None:
    # Transport mémoire pour diagnostiquer le protocole sans réseau ni LLM.
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print("TOOLS")
        for tool in tools:
            print(f"- {tool.name}")

        print("\nTOOL CALL")
        tool_result = await client.call_tool("get_ticket", {"ticket_id": "ticket-123"})
        print(tool_result.data)

        print("\nRESOURCE TEMPLATES")
        templates = await client.list_resource_templates()
        for template in templates:
            print(f"- {template.uriTemplate}")

        print("\nRESOURCE")
        resources = await client.read_resource("docs://refund-policy")
        for resource in resources:
            print(resource.text)

        print("\nPROMPT")
        prompt = await client.get_prompt(
            "analyze_support_ticket",
            {"ticket_content": "L'application affiche une erreur 503."},
        )
        for message in prompt.messages:
            print(f"{message.role}: {message.content}")


if __name__ == "__main__":
    asyncio.run(main())
