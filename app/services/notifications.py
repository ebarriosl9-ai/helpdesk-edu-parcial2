"""Notificadores de eventos del dominio.

Notifier es el contrato (puerto) que TicketService usa para avisar sobre
eventos como asignaciones. Las implementaciones concretas deciden el canal.
"""

from __future__ import annotations

from typing import Any, Protocol


class Notifier(Protocol):
    def notify(self, event: str, payload: dict[str, Any]) -> None: ...


class RecordingNotifier:
    """Notificador de pruebas: guarda cada evento en memoria."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def notify(self, event: str, payload: dict[str, Any]) -> None:
        self.events.append((event, payload))


class WebhookNotifier:
    """Implementación del contrato Notifier que simula un webhook.

    No hace HTTP real ni imprime nada: solo almacena los payloads
    recibidos en `sent_payloads`, para poder inspeccionarlos en pruebas.
    """

    def __init__(self, url: str = "https://example.test/webhook") -> None:
        self.url = url
        self.sent_payloads: list[dict[str, Any]] = []

    def notify(self, event: str, payload: dict[str, Any]) -> None:
        self.sent_payloads.append({"event": event, "url": self.url, **payload})
