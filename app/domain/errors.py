"""Jerarquía de excepciones de dominio para HelpDesk EDU."""

from __future__ import annotations


class DomainError(Exception):
    """Error base de todas las reglas de negocio del dominio."""


class ValidationError(DomainError):
    """Un dato de entrada no cumple una regla de validación del dominio."""


class NotFoundError(DomainError):
    """Base para errores de "no encontrado" en repositorios y servicios."""


class TicketNotFoundError(NotFoundError):
    """No existe un Ticket con el id solicitado."""

    def __init__(self, ticket_id: int) -> None:
        super().__init__(f"No existe un ticket con id={ticket_id!r}")
        self.ticket_id = ticket_id


class UserNotFoundError(NotFoundError):
    """No existe un User con el id solicitado."""

    def __init__(self, user_id: int) -> None:
        super().__init__(f"No existe un usuario con id={user_id!r}")
        self.user_id = user_id


class DuplicateAssignmentError(DomainError):
    """Se intentó asignar un ticket al técnico que ya lo tiene asignado."""

    def __init__(self, ticket_id: int, technician_id: int) -> None:
        super().__init__(
            f"El ticket {ticket_id!r} ya está asignado al técnico {technician_id!r}"
        )
        self.ticket_id = ticket_id
        self.technician_id = technician_id
