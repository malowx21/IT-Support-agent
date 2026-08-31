# import asyncio

# from agent.mcp_client import create_mcp_client


# async def main() -> None:
#     client = create_mcp_client()

#     tools = await client.get_tools()

#     print("Tools disponibles :")

#     for tool in tools:
#         print(f"- {tool.name}")
#         # print(f"  {tool.description}")


# if __name__ == "__main__":
#     asyncio.run(main())

# import asyncio
# from langchain_core.messages import HumanMessage
# from agent.graph import build_graph


# async def main():
#     workflow = await build_graph()
#     res = await workflow.ainvoke({"messages":[HumanMessage(content="Comment réinitialiser mon mot de passe ?")]})
#     print(res["messages"][-1].content)
    
# if __name__ == "__main__":
#     asyncio.run(main())


# import asyncio

# from langchain_core.messages import HumanMessage
# from langgraph.types import Command

# from agent.graph import build_graph


# async def main():
#     workflow = await build_graph()

#     config = {
#         "configurable": {
#             "thread_id": "ticket-demo-1",
#         }
#     }

#     result = await workflow.ainvoke(
#         {
#             "messages": [
#                 HumanMessage(
#                     content=(
#                         "Ferme le ticket ticket-456 "
#                         "car le problème est résolu."
#                     )
#                 )
#             ],
#             "review_response": None,
#         },
#         config=config,
#     )

#     if "__interrupt__" not in result:
#         print(result["messages"][-1].content)
#         return

#     for interruption in result["__interrupt__"]:
#         print("\nValidation demandée :")
#         print(interruption.value)

#     decision = input(
#         "\nDécision (approve/reject) : "
#     ).strip().lower()

#     final_result = await workflow.ainvoke(
#         Command(
#             resume={
#                 "decision": decision,
#             }
#         ),
#         config=config,
#     )

#     print("\nRéponse finale :")
#     print(
#         final_result["messages"][-1].content
#     )


# if __name__ == "__main__":
#     asyncio.run(main())


# from pathlib import Path

# path = Path(__file__).parent / "mcp_server" / "knowledge"

# doc = path.glob("*.md")

# for d in doc :
#     c = d.read_text(encoding="utf-8")
#     print(c)
#     print(d)
#     print("apa")


# from rag.loader import load_documents
# from rag.splitter import split_documents


# documents = load_documents(
#     "mcp_server/knowledge"
# )

# chunks = split_documents(
#     documents,
#     chunk_size=150,
#     chunk_overlap=30,
# )

# for chunk in chunks:
#     print(chunk.metadata)
#     print(chunk.page_content)
#     print("-" * 50)

# from rag.embed import (
#     embed_doc,
#     embed_query,
# )
# from rag.loader import load_documents
# from rag.splitter import split_documents


# documents = load_documents(
#     "mcp_server/knowledge"
# )

# chunks = split_documents(
#     documents,
#     150,
#     30
# )

# vectors = embed_doc(
#     chunks
# )

# query_vector = embed_query(
#     "Comment réinitialiser mon mot de passe ?"
# )

# print("Nombre de chunks :", len(chunks))
# print("Nombre de vecteurs :", len(vectors))

# print(
#     "Dimension d'un vecteur :",
#     len(vectors[0]),
# )

# print(
#     "Dimension de la question :",
#     len(query_vector),
# )

# from rag.retriever import (
#     retrieve_docs,
# )


# results = retrieve_docs(
#     query=(
#         "Je ne reçois pas l'email pour "
#         "changer mon mot de passe."
#     ),
#     limit=3,
# )

# for result in results:
#     print(
#         "Document :",
#         result["document_id"],
#     )

#     print(
#         "Chunk :",
#         result["metadata"]["chunk_index"],
#     )

#     print(
#         "Score :",
#         round(result["score"], 3),
#     )

#     print(result["content"])
#     print("-" * 50)


from pathlib import Path

import pytest

from config import settings
from mcp_server.service import KnowledgeService
from rag.ingest import ingest_documents
from rag.retriever import cosine_similarity


def test_cosine_similarity():
    assert cosine_similarity(
        [1.0, 0.0],
        [1.0, 0.0],
    ) == pytest.approx(1.0)

    assert cosine_similarity(
        [1.0, 0.0],
        [0.0, 1.0],
    ) == pytest.approx(0.0)

    assert cosine_similarity(
        [1.0, 0.0],
        [-1.0, 0.0],
    ) == pytest.approx(-1.0)


@pytest.fixture(scope="module")
def knowledge_service(
    tmp_path_factory,
) -> KnowledgeService:
    temporary_directory = (
        tmp_path_factory.mktemp("rag")
    )

    database_path = (
        temporary_directory / "rag-test.db"
    )

    ingest_documents(
        database_path=database_path,
        documents_path=settings.documents_path,
        chunk_size=500,
        chunk_overlap=80,
    )

    return KnowledgeService(
        knowledge_directory=(
            settings.documents_path
        ),
        database_path=database_path,
    )


@pytest.mark.parametrize(
    (
        "query",
        "expected_document_id",
    ),
    [
        (
            (
                "Je ne reçois pas le lien pour "
                "réinitialiser mon mot de passe."
            ),
            "password-reset",
        ),
        (
            (
                "Dans quelles conditions puis-je "
                "obtenir un remboursement ?"
            ),
            "refund-policy",
        ),
        (
            (
                "Je n'ai plus accès à mon ancienne "
                "adresse email."
            ),
            "account-email",
        ),
    ],
)
def test_rag_returns_relevant_document(
    knowledge_service,
    query,
    expected_document_id,
):
    results = knowledge_service.search(
        query=query,
        limit=3,
    )

    assert results

    returned_document_ids = {
        result["document_id"]
        for result in results
    }

    assert (
        expected_document_id
        in returned_document_ids
    )

    for result in results:
        assert result["content"]

        assert isinstance(
            result["score"],
            float,
        )

        assert -1 <= result["score"] <= 1

        assert "embedding" not in result


def test_results_are_sorted_by_score(
    knowledge_service,
):
    results = knowledge_service.search(
        query="Comment modifier mon adresse email ?",
        limit=3,
    )

    scores = [
        result["score"]
        for result in results
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )
