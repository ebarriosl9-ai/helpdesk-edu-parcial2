-- Ejercicio 4 (Serie II): SQL e integridad referencial
-- Ejecutar contra PostgreSQL, con el schema de database.sql ya cargado
-- y datos de prueba (usuarios y tickets) insertados previamente.

-- a) Tickets abiertos con el nombre del solicitante (JOIN)
SELECT t.id, t.title, u.name AS requester_name
FROM tickets t
JOIN users u ON u.id = t.requester_id
WHERE t.status = 'open';

-- b) Conteo de tickets por técnico asignado, agrupado por id y nombre,
--    excluyendo conteos cero (HAVING) y ordenado descendente.
SELECT u.id AS technician_id, u.name AS technician_name, COUNT(t.id) AS ticket_count
FROM users u
JOIN tickets t ON t.assignee_id = u.id
GROUP BY u.id, u.name
HAVING COUNT(t.id) > 0
ORDER BY ticket_count DESC;

-- c) Tickets sin comentarios (NOT EXISTS)
SELECT t.id, t.title
FROM tickets t
WHERE NOT EXISTS (
    SELECT 1 FROM comments c WHERE c.ticket_id = t.id
);

-- Alternativa equivalente con LEFT JOIN:
-- SELECT t.id, t.title
-- FROM tickets t
-- LEFT JOIN comments c ON c.ticket_id = t.id
-- WHERE c.id IS NULL;

-- d) Demostración de ON DELETE CASCADE sobre el historial, dentro de una
--    transacción que se revierte (BEGIN / ROLLBACK).
--    Sustituya :ticket_id por el id de un ticket con historial existente.

BEGIN;

-- Conteo inicial: debe ser mayor que cero.
SELECT COUNT(*) AS conteo_inicial FROM history WHERE ticket_id = :ticket_id;

-- Al borrar el ticket, el ON DELETE CASCADE de la FK borra también su historial.
DELETE FROM tickets WHERE id = :ticket_id;

-- Conteo tras el DELETE: debe ser cero.
SELECT COUNT(*) AS conteo_tras_delete FROM history WHERE ticket_id = :ticket_id;

ROLLBACK;

-- Conteo tras el ROLLBACK: debe volver a coincidir con el conteo inicial,
-- porque la transacción completa (DELETE incluido) se revirtió.
SELECT COUNT(*) AS conteo_tras_rollback FROM history WHERE ticket_id = :ticket_id;
