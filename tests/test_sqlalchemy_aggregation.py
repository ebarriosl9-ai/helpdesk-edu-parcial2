import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.repositories.sqlalchemy import Base, SqlAlchemyTicketRepository, TicketORM, UserORM


@pytest.fixture
def repo():
    # StaticPool: todas las sesiones de la prueba comparten la misma
    # conexión en memoria y ven las mismas tablas.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    with session_factory() as session:
        session.add(UserORM(id=1, name="Ana", email="ana@edu.gt", role="requester"))
        session.add(UserORM(id=2, name="Luis", email="luis@edu.gt", role="technician"))
        session.commit()

    return SqlAlchemyTicketRepository(session_factory)


def test_count_by_status_diccionario_completo(repo: SqlAlchemyTicketRepository):
    # Tres tickets en dos estados válidos: dos en 'open', uno en 'in_progress'.
    with repo._session_factory() as session:
        session.add(TicketORM(title="A", description="d", status="open", requester_id=1))
        session.add(TicketORM(title="B", description="d", status="open", requester_id=1))
        session.add(
            TicketORM(title="C", description="d", status="in_progress", requester_id=1)
        )
        session.commit()  # confirma la transacción y cierra la unidad de trabajo

    # Consulta desde una sesión nueva sobre el mismo engine.
    result = repo.count_by_status()

    assert result == {"open": 2, "in_progress": 1}
    assert sum(result.values()) == 3


def test_count_by_status_base_vacia_devuelve_diccionario_vacio(repo: SqlAlchemyTicketRepository):
    result = repo.count_by_status()

    assert result == {}
