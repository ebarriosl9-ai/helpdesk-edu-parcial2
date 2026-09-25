import pytest

from app.domain.errors import TicketNotFoundError
from app.models.entities import Role, User
from app.repositories.memory import InMemoryTicketRepository, InMemoryUserRepository
from app.services.tickets import TicketService


@pytest.fixture
def service() -> TicketService:
    tickets = InMemoryTicketRepository()
    users = InMemoryUserRepository()
    users.add(User(id=1, name="Ana", email="ana@edu.gt", role=Role.REQUESTER))
    users.add(User(id=2, name="Luis", email="luis@edu.gt", role=Role.TECHNICIAN))
    users.add(User(id=3, name="Marta", email="marta@edu.gt", role=Role.TECHNICIAN))
    return TicketService(tickets, users)


def test_watchers_sin_tecnico_devuelve_solo_al_solicitante(service: TicketService):
    ticket = service.create("Sin red", "No hay conexión", requester_id=1)

    watchers = service.watchers(ticket.id)

    assert [w.id for w in watchers] == [1]


def test_watchers_con_tecnico_distinto_devuelve_ambos(service: TicketService):
    ticket = service.create("Sin red", "No hay conexión", requester_id=1)
    service.assign(ticket.id, technician_id=2)

    watchers = service.watchers(ticket.id)

    assert [w.id for w in watchers] == [1, 2]


def test_watchers_propaga_error_de_ticket_inexistente(service: TicketService):
    with pytest.raises(TicketNotFoundError):
        service.watchers(999)


def test_watchers_deduplica_si_solicitante_y_tecnico_son_el_mismo_usuario(
    service: TicketService,
):
    # Caso controlado: el propio solicitante termina siendo el técnico asignado.
    ticket = service.create("Autoservicio", "Revisión propia", requester_id=1)
    service._repository.by_id(ticket.id).assignee_id = 1  # asignación directa de prueba

    watchers = service.watchers(ticket.id)

    assert [w.id for w in watchers] == [1]
