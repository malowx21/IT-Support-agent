
import json 
import sqlite3
from contextlib import contextmanager
from mcp_server.repository import utc_now
from langchain_core.documents import Document

class RepositoryRag:
    
    def __init__(self,database_path):
        self.database_path = database_path
        
    @contextmanager
    def connection(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_key=ON")
        try :
            yield connection
            connection.commit()
        except:
            connection.rollback()
            raise
        finally:
            connection.close()
    
    def initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                document_chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            
            # Creer un index sur le document_id permet d'accelerer les recherches dans la table
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_document_chunks_document_id
                ON document_chunks(document_id)
                """
            )

    def replace_chunks(
        self,
        chunks: list[Document],
        embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Le nombre de chunks doit être "
                "égal au nombre d'embeddings."
            )

        if not chunks:
            return

        document_ids = {
            chunk.metadata["document_stem"]
            for chunk in chunks
        }

        with self.connection() as connection:
            for document_id in document_ids:
                connection.execute(
                    """
                    DELETE FROM document_chunks
                    WHERE document_id = ?
                    """,
                    (document_id,),
                )

            rows = []

            for chunk, embedding in zip(
                chunks,
                embeddings,
                strict=True,
            ):
                document_id = chunk.metadata[
                    "document_stem"
                ]

                chunk_index = chunk.metadata[
                    "chunk_index"
                ]

                chunk_id = (
                    f"{document_id}:{chunk_index}"
                )

                rows.append(
                    (
                        chunk_id,
                        document_id,
                        chunk.page_content,
                        json.dumps(
                            chunk.metadata
                        ),
                        json.dumps(
                            embedding
                        ),
                        utc_now(),
                    )
                )

            connection.executemany(
                """
                INSERT INTO document_chunks (
                    id,
                    document_id,
                    content,
                    metadata,
                    embedding,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

    def get_all_chunks(
        self) -> list[dict]:
        with self.connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM document_chunks
                ORDER BY document_id, id
                """
            ).fetchall()

        chunks = []

        for row in rows:
            item = dict(row)

            item["metadata"] = json.loads(
                item["metadata"]
            )

            item["embedding"] = json.loads(
                item["embedding"]
            )

            chunks.append(item)

        return chunks

    def count_chunks(self) -> int:
        with self.connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM document_chunks
                """
            ).fetchone()

        return int(row["count"])
