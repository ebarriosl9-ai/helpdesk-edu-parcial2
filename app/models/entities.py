"""Entidades de dominio del proyecto HelpDesk EDU.

Estas clases son dataclasses "puros": no conocen SQLAlchemy ni ningún
detalle de persistencia. Los repositorios se encargan de traducir entre
estas entidades y su representación en la base de datos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.domain.errors import ValidationError


class Role(StrEnum):
    REQUESTER = "requester"
    TECHNICIAN = "technician"
    ADMIN = "admin"


class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


@dataclass
class User:
    id: int
    name: str
    email: str
    role: Role


@dataclass
class Comment:
    id: int
    ticket_id: int
    author_id: int
    body: str
    created_at: datetime = field(default_factory=lambda: datetime.now().astimezone())


@dataclass
class HistoryEvent:
    id: int
    ticket_id: int
    event: str
    created_at: datetime = field(default_factory=lambda: datetime.now().astimezone())


@dataclass
class Ticket:
    id: int
    title: str
    description: str
    requester_id: int
    status: TicketStatus = TicketStatus.OPEN
    assignee_id: int | None = None
    comments: list[Comment] = field(default_factory=list)
    history: list[HistoryEvent] = field(default_factory=list)

    # Ejercicio 1 (Serie II): etiquetas encapsuladas.
    # - Colección interna por instancia, no participa en __init__ ni en repr.
    # - Se expone solo de lectura mediante la propiedad `tags` (tupla).
    # - La única forma de modificarla es `add_tag`.
    _tags: list[str] = field(default_factory=list, init=False, repr=False)

    @property
    def tags(self) -> tuple[str, ...]:
        """Vista de solo lectura de las etiquetas del ticket."""
        return tuple(self._tags)

    def add_tag(self, tag: str) -> None:
        """Agrega una etiqueta normalizada, validando vacíos y duplicados."""
        normalized = tag.strip().lower()
        if not normalized:
            raise ValidationError("La etiqueta no puede ser vacía o solo espacios")
        if normalized in self._tags:
            return  # evita duplicados silenciosamente
        self._tags.append(normalized)
