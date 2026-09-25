# README - Segundo Parcial (Semanas 7-11) - HelpDesk EDU

## Instrucciones reproducibles

1. Instalar dependencias:
   ```
   uv sync
   ```
   (o `pip install -e ".[dev]"` si no usas `uv`)
2. Ejecutar todas las pruebas:
   ```
   uv run pytest -q
   ```
3. Para el ejercicio de SQL (ejercicio 4), cargar `docs/database/database.sql`
   en una base PostgreSQL, insertar datos de prueba y ejecutar
   `docs/database/queries_parcial2.sql` con un cliente como `psql`.

## Archivos modificados / agregados por ejercicio

| Ejercicio | Archivos | Resumen |
|---|---|---|
| 1. Etiquetas y encapsulamiento | `app/models/entities.py`, `app/domain/errors.py` | `Ticket._tags` privado + init=False + repr=False; propiedad `tags` de solo lectura; `add_tag()` con `strip().lower()`, rechazo de vacíos (`ValidationError`) y sin duplicados. |
| 2. Observadores y relaciones | `app/services/tickets.py` | `TicketService.watchers(ticket_id)` devuelve solicitante + técnico (si existe), sin duplicar por id, usando `self.require()` y `self._users.require()`. |
| 3. Excepciones y polimorfismo | `app/domain/errors.py`, `app/services/tickets.py`, `app/services/notifications.py` | `DuplicateAssignmentError(DomainError)`; `assign()` la lanza antes de tocar historial/notificaciones; `WebhookNotifier` implementa `Notifier` guardando payloads en `sent_payloads` (sin HTTP ni print); se inyecta por el parámetro `notifier` existente, sin condicionales por tipo. |
| 4. SQL e integridad referencial | `docs/database/queries_parcial2.sql`, `docs/database/database.sql` | Las 4 consultas requeridas (a, b, c, d) más el schema con `ON DELETE CASCADE` en `comments` e `history`. |
| 5. Agregación SQLAlchemy | `app/repositories/sqlalchemy.py` | `SqlAlchemyTicketRepository.count_by_status()` con `select(TicketORM.status, func.count()).group_by(...)`; no cambia `TicketRepository`; pruebas con SQLite en memoria + `StaticPool`. |

## Resultados de ejecución

Ejecutar `uv run pytest -q` y pegar aquí la salida real antes de entregar,
por ejemplo:

```
uv run pytest -q
....................
20 passed in 0.35s
```

## Limitaciones conocidas

- `SqlAlchemyTicketRepository.next_id()` no aplica: el id lo genera
  PostgreSQL/SQLite mediante autoincrement al hacer `add()`.
- Las pruebas del ejercicio 4 (SQL puro) requieren una instancia real de
  PostgreSQL con datos de prueba cargados; no se automatizan con pytest.

## Link del repositorio

https://github.com/ebarriosl9-ai/helpdesk-edu-parcial2.git
