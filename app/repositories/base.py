"""Contratos abstractos de repositorios (puertos del dominio)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.errors import UserNotFoundError
from app.models.entities import Ticket, User


class TicketRepository(ABC):
    @abstractmethod
    def add(self, ticket: Ticket) -> Ticket: ...

    @abstractmethod
    def by_id(self, ticket_id: int) -> Ticket | None: ...

    @abstractmethod
    def list(
        self,
        *,
        status: str | None = None,
        assignee_id: int | None = None,
        requester_id: int | None = None,
    ) -> list[Ticket]: ...

    @abstractmethod
    def next_id(self) -> int: ...

    @abstractmethod
    def update(self, ticket: Ticket) -> Ticket: ...


class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User: ...

    @abstractmethod
    def by_id(self, user_id: int) -> User | None: ...

    def require(self, user_id: int) -> User:
        """Devuelve el usuario o lanza UserNotFoundError si no existe."""
        user = self.by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user
