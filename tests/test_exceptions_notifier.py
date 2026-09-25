import pytest

from app.domain.errors import DuplicateAssignmentError
from app.models.entities import Role, User
from app.repositories.memory import InMemoryTicketRepository, InMemoryUserRepository
from app.services.notifications import WebhookNotifier
from app.services.tickets import TicketService


@pytest.fixture
def setup():
    tickets = InMemoryTicketRepository()
    users = InMemoryUserRepository()
    users.add(User(id=1, name="Ana", email="ana@edu.gt", role=Role.REQUESTER))
    users.add(User(id=2, name="Luis", email="luis@edu.gt", role=Role.TECHNICIAN))
    notifier = WebhookNotifier()
    service = TicketService(tickets, users, notifier=notifier)
    return service, notifier


def test_reasignar_mismo_tecnico_lanza_excepcion_sin_efectos_adicionales(setup):
    service, notifier = setup
    ticket = service.create("Sin red", "No hay conexión", requester_id=1)
    service.assign(ticket.id, technician_id=2)

    history_len_antes = len(service.require(ticket.id).history)
    payloads_antes = len(notifier.sent_payloads)

    with pytest.raises(DuplicateAssignmentError):
        service.assign(ticket.id, technician_id=2)

    ticket_despues = service.require(ticket.id)
    assert len(ticket_despues.history) == history_len_antes
    assert len(notifier.sent_payloads) == payloads_antes


def test_asignacion_valida_notifica_con_payload_correcto(setup):
    service, notifier = setup
    ticket = service.create("Sin red", "No hay conexión", requester_id=1)

    service.assign(ticket.id, technician_id=2)

    assert len(notifier.sent_payloads) == 1
    payload = notifier.sent_payloads[0]
    assert payload["event"] == "ticket.assigned"
    assert payload["ticket_id"] == ticket.id
    assert payload["technician_id"] == 2
