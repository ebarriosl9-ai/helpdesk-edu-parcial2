import pytest

from app.domain.errors import ValidationError
from app.models.entities import Ticket, TicketStatus


def make_ticket(ticket_id: int = 1) -> Ticket:
    return Ticket(
        id=ticket_id,
        title="Impresora no responde",
        description="La impresora del laboratorio no imprime",
        requester_id=1,
        status=TicketStatus.OPEN,
    )


def test_add_tag_normaliza_y_evita_duplicados():
    ticket = make_ticket()

    ticket.add_tag("  Hardware ")
    ticket.add_tag("hardware")  # duplicado tras normalizar

    assert ticket.tags == ("hardware",)


def test_add_tag_rechaza_espacios_en_blanco():
    ticket = make_ticket()

    with pytest.raises(ValidationError):
        ticket.add_tag("   ")


def test_add_tag_rechaza_string_vacio():
    ticket = make_ticket()

    with pytest.raises(ValidationError):
        ticket.add_tag("")


def test_tags_son_independientes_entre_instancias():
    ticket_a = make_ticket(ticket_id=1)
    ticket_b = make_ticket(ticket_id=2)

    ticket_a.add_tag("red")

    assert ticket_a.tags == ("red",)
    assert ticket_b.tags == ()


def test_tags_no_permite_reasignacion_publica():
    ticket = make_ticket()

    with pytest.raises(AttributeError):
        ticket.tags = ("otra",)
