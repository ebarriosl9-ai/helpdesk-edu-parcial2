"""Servicio de aplicación para Tickets.

TicketService recibe sus colaboradores por inyección de dependencias
(repository, users, notifier) en lugar de crearlos internamente, y nunca
accede directamente a los repositorios de otros servicios: para datos de
usuarios siempre pasa por self._users.
"""

from __future__ import annotations

from app.domain.errors import DuplicateAssignmentError, TicketNotFoundError
from app.models.entities import Ticket, TicketStatus, User
from app.repositories.base import TicketRepository, UserRepository
from app.services.notifications import Notifier


class TicketService:
    def __init__(
        self,
        repository: TicketRepository,
        users: UserRepository,
        notifier: Notifier | None = None,
    ) -> None:
        self._repository = repository
        self._users = users
        self._notifier = notifier

    def require(self, ticket_id: int) -> Ticket:
        """Devuelve el ticket o lanza TicketNotFoundError si no existe."""
        ticket = self._repository.by_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(ticket_id)
        return ticket

    def create(self, title: str, description: str, requester_id: int) -> Ticket:
        self._users.require(requester_id)
        ticket = Ticket(
            id=self._repository.next_id(),
            title=title,
            description=description,
            requester_id=requester_id,
            status=TicketStatus.OPEN,
        )
        return self._repository.add(ticket)

    # --- Ejercicio 3: excepción y polimorfismo -----------------------------
    def assign(self, ticket_id: int, technician_id: int) -> Ticket:
        """Asigna un técnico al ticket.

        Rechaza la asignación si el ticket ya tiene ese mismo técnico
        (DuplicateAssignmentError), antes de tocar historial o notificar.
        Mantiene las validaciones existentes: el técnico debe existir.
        """
        technician = self._users.require(technician_id)
        ticket = self.require(ticket_id)

        if ticket.assignee_id == technician.id:
            raise DuplicateAssignmentError(ticket_id, technician_id)

        ticket.assignee_id = technician.id
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.history.append(
            _make_history_event(ticket_id, f"Asignado a {technician.name}")
        )
        self._repository.update(ticket)

        if self._notifier is not None:
            self._notifier.notify(
                "ticket.assigned",
                {"ticket_id": ticket_id, "technician_id": technician_id},
            )
        return ticket

    # --- Ejercicio 2: observadores y relaciones entre objetos --------------
    def watchers(self, ticket_id: int) -> list[User]:
        """Devuelve el solicitante y, si existe, el técnico asignado.

        No repite usuarios con el mismo id (por ejemplo si el solicitante
        y el técnico asignado fueran el mismo usuario).
        """
        ticket = self.require(ticket_id)
        result = [self._users.require(ticket.requester_id)]

        if ticket.assignee_id is not None:
            technician = self._users.require(ticket.assignee_id)
            if technician.id not in {user.id for user in result}:
                result.append(technician)

        return result


def _make_history_event(ticket_id: int, description: str):
    from app.models.entities import HistoryEvent

    return HistoryEvent(id=0, ticket_id=ticket_id, event=description)
