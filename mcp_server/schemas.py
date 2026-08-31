from enum import StrEnum
from pydantic import BaseModel, Field

# class de la priorité
class TicketPriority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

# état du ticket 
class TicketStatus(StrEnum):
    open = "open"
    pending = "pending"
    closed = "closed"

# Création du ticket 
class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5, max_length=5000)
    customer_email: str = Field(min_length=3, max_length=320)
    priority: TicketPriority = TicketPriority.medium

# Cas d'une erreur 
class ToolError(BaseModel):
    code: str
    message: str

# Résultat du tool
class ToolResult(BaseModel):
    success: bool
    data: dict | list | None = None
    error: ToolError | None = None

