"""Implementaciones en memoria de los repositorios, usadas en pruebas."""

from __future__ import annotations

from app.models.entities import Ticket, User
from app.repositories.base import TicketRepository, UserRepository


class InMemoryTicketRepository(TicketRepository):
    def __init__(self) -> None:
        self._tickets: dict[int, Ticket] = {}
        self._counter = 0

    def add(self, ticket: Ticket) -> Ticket:
        self._tickets[ticket.id] = ticket
        return ticket

    def by_id(self, ticket_id: int) -> Ticket | None:
        return self._tickets.get(ticket_id)

    def list(
        self,
        *,
        status: str | None = None,
        assignee_id: int | None = None,
        requester_id: int | None = None,
    ) -> list[Ticket]:
        result = list(self._tickets.values())
        if status is not None:
            result = [t for t in result if t.status == status]
        if assignee_id is not None:
            result = [t for t in result if t.assignee_id == assignee_id]
        if requester_id is not None:
            result = [t for t in result if t.requester_id == requester_id]
        return result

    def next_id(self) -> int:
        self._counter += 1
        return self._counter

    def update(self, ticket: Ticket) -> Ticket:
        self._tickets[ticket.id] = ticket
        return ticket


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[int, User] = {}

    def add(self, user: User) -> User:
        self._users[user.id] = user
        return user

    def by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)
