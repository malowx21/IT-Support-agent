import asyncio
from uuid import uuid4

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)

from agent.graph import build_graph


async def main():
    graph = await build_graph()

    config = {
        "configurable": {
            "thread_id": str(uuid4()),
        }
    }

    result = await graph.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "Je ne reçois pas le lien "
                        "pour réinitialiser mon mot "
                        "de passe. Consulte la "
                        "documentation."
                    )
                )
            ],
            "review_response": None,
        },
        config=config,
    )

    print("\n===== PARCOURS DE L'AGENT =====\n")

    for index, message in enumerate(
        result["messages"],
        start=1,
    ):
        print(
            f"{index}. "
            f"{type(message).__name__}"
        )

        if (
            isinstance(message, AIMessage)
            and message.tool_calls
        ):
            for tool_call in message.tool_calls:
                print(
                    "   Tool appelé :",
                    tool_call["name"],
                )

                print(
                    "   Arguments :",
                    tool_call["args"],
                )

        elif isinstance(message, ToolMessage):
            print(
                "   Résultat du tool :",
                message.content,
            )

        else:
            print(
                "   Contenu :",
                message.content,
            )

        print()


if __name__ == "__main__":
    asyncio.run(main())


