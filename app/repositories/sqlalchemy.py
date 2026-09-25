"""Repositorio de Tickets basado en SQLAlchemy.

Los modelos ORM (TicketORM, etc.) son un detalle de persistencia: el
repositorio siempre traduce filas ORM a las dataclasses de dominio
(_ticket_to_domain) antes de devolverlas, para que TicketService nunca
tenga que conocer detalles de SQLAlchemy.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from app.models.entities import Comment, HistoryEvent, Ticket, TicketStatus
from app.repositories.base import TicketRepository


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    role: Mapped[str] = mapped_column(String(20))


class TicketORM(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(20), default=TicketStatus.OPEN)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    requester = relationship("UserORM", foreign_keys=[requester_id])
    assignee = relationship("UserORM", foreign_keys=[assignee_id])

    comments: Mapped[list["CommentORM"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
    history: Mapped[list["HistoryEventORM"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )


class CommentORM(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE")
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    ticket = relationship("TicketORM", back_populates="comments")


class HistoryEventORM(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE")
    )
    event: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    ticket = relationship("TicketORM", back_populates="history")


def _ticket_to_domain(row: TicketORM) -> Ticket:
    ticket = Ticket(
        id=row.id,
        title=row.title,
        description=row.description,
        requester_id=row.requester_id,
        status=TicketStatus(row.status),
        assignee_id=row.assignee_id,
    )
    ticket.comments = [
        Comment(
            id=c.id,
            ticket_id=c.ticket_id,
            author_id=c.author_id,
            body=c.body,
            created_at=c.created_at,
        )
        for c in row.comments
    ]
    ticket.history = [
        HistoryEvent(
            id=h.id, ticket_id=h.ticket_id, event=h.event, created_at=h.created_at
        )
        for h in row.history
    ]
    return ticket


class SqlAlchemyTicketRepository(TicketRepository):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def add(self, ticket: Ticket) -> Ticket:
        with self._session_factory() as session:
            row = TicketORM(
                title=ticket.title,
                description=ticket.description,
                status=str(ticket.status),
                requester_id=ticket.requester_id,
                assignee_id=ticket.assignee_id,
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return _ticket_to_domain(row)

    def by_id(self, ticket_id: int) -> Ticket | None:
        with self._session_factory() as session:
            row = session.get(TicketORM, ticket_id)
            return _ticket_to_domain(row) if row is not None else None

    def list(
        self,
        *,
        status: str | None = None,
        assignee_id: int | None = None,
        requester_id: int | None = None,
    ) -> list[Ticket]:
        with self._session_factory() as session:
            stmt = select(TicketORM)
            if status is not None:
                stmt = stmt.where(TicketORM.status == status)
            if assignee_id is not None:
                stmt = stmt.where(TicketORM.assignee_id == assignee_id)
            if requester_id is not None:
                stmt = stmt.where(TicketORM.requester_id == requester_id)
            rows = session.scalars(stmt).all()
            return [_ticket_to_domain(row) for row in rows]

    def next_id(self) -> int:
        # El id lo asigna la base de datos (autoincrement) al hacer add().
        raise NotImplementedError(
            "SqlAlchemyTicketRepository asigna el id automáticamente en add()"
        )

    def update(self, ticket: Ticket) -> Ticket:
        with self._session_factory() as session:
            row = session.get(TicketORM, ticket.id)
            if row is None:
                raise ValueError(f"No existe el ticket {ticket.id} para actualizar")
            row.title = ticket.title
            row.description = ticket.description
            row.status = str(ticket.status)
            row.assignee_id = ticket.assignee_id
            session.commit()
            session.refresh(row)
            return _ticket_to_domain(row)

    # --- Ejercicio 5: consulta agregada con SQLAlchemy ----------------------
    def count_by_status(self) -> dict[str, int]:
        """Cuenta tickets agrupados por estado.

        Devuelve solo los estados presentes en la tabla y {} si no hay
        tickets. No modifica la interfaz abstracta TicketRepository: es un
        método adicional propio de esta implementación.
        """
        with self._session_factory() as session:
            stmt = select(TicketORM.status, func.count()).group_by(TicketORM.status)
            rows = session.execute(stmt).all()
            return {status: count for status, count in rows}
