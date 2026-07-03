# Delivery guarantees, idempotency, and the outbox

## The three semantics

| Semantics | Meaning | Reality |
|-----------|---------|---------|
| at-most-once | may lose, never duplicate | rarely what you want |
| **at-least-once** | never lose, may duplicate | the practical default; requires idempotent consumers |
| exactly-once | each effect once | **not** given by a broker alone — engineered (below) |

Design for **at-least-once + idempotent effects**. "Exactly-once" as advertised by a
broker usually means exactly-once *within that broker's processing*, not end-to-end
across your database and external calls.

## Idempotency (the core technique)

- Give every message a stable **idempotency key** (a business id, or a producer-assigned
  token). The consumer records processed keys and **skips duplicates**.
- Make the *effect* idempotent where possible: upsert instead of insert, set-absolute
  instead of increment, conditional writes (compare-and-set) instead of blind updates.
- Store the dedupe record and the effect in the **same transaction** so a crash cannot
  record "done" without doing it (or vice versa).

## Transactional outbox (atomic state + publish)

The classic bug: update the database, then publish an event — and crash in between,
leaving state and stream inconsistent. Fix:

1. In **one DB transaction**, write the state change **and** an `outbox` row describing
   the event.
2. A separate relay reads unsent outbox rows and publishes them (at-least-once), marking
   them sent.
3. Consumers dedupe on the event id.

This makes "changed state ⇒ event eventually published" atomic, without distributed
transactions. The mirror on the read side is the **inbox** pattern (record handled
message ids to dedupe).

## Consumer-side transactions

- Ack **after** the effect is durably committed, not before — acking first turns a crash
  into a lost message.
- If the handler calls an external system, that call is where exactly-once leaks; make it
  idempotent (idempotency key to the downstream) or reconcile.

## Ordering vs delivery

- At-least-once + retries can reorder (a retried message arrives after later ones).
  Handlers that need order must key on the partition and tolerate gaps/retries, or carry
  a sequence number and reorder/detect.

## Checklist

- [ ] Every event carries a stable id / idempotency key.
- [ ] Consumers dedupe on it; effects are idempotent (upsert/CAS).
- [ ] State change + event publish are atomic (outbox).
- [ ] Ack after commit; retries have backoff+jitter and a DLQ.
- [ ] Downstream external calls are idempotent or reconciled.
