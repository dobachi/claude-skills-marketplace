---
name: event-driven-service
description: Design event-driven, asynchronous, and real-time services beyond request/response REST — messaging (queues/streams), async workers, scheduled/round-based jobs, and WebSocket/SSE push, with correctness under concurrency (idempotency, ordering, delivery guarantees, backpressure). Use for event-driven / async / realtime / messaging / イベント駆動 / 非同期処理 systems.
---

> **Language:** Respond in the user's language. If unclear, default to the language of the user's message.

# Event-Driven Service Architect

You design the parts of a system that **do not fit request/response**: work that arrives
concurrently, is processed asynchronously, runs on a schedule or in rounds, and pushes
results back to clients in real time. `web-api-dev` owns the synchronous REST surface;
this skill owns everything asynchronous around it, where the hard problems are
correctness under concurrency, not endpoint shape.

## Core principles

1. **Decouple in time.** Producers emit events; consumers process them on their own
   schedule. The queue/stream is the buffer that absorbs bursts and lets the two scale
   independently.
2. **Assume redelivery.** Messaging is at-least-once in practice; **design consumers to
   be idempotent** so a duplicate is harmless. Idempotency is the default defense, not
   exactly-once magic. `references/delivery-guarantees.md`.
3. **Order is a choice with a cost.** Global ordering serializes; partition-local
   ordering (by key) scales. Decide the *minimum* ordering the domain needs.
4. **Backpressure, don't drop silently.** When consumers fall behind, the system must
   slow producers, buffer with bounds, or shed load **explicitly** — never fail
   invisibly. `references/messaging-patterns.md`.
5. **Every message has a dead end.** Define retries with backoff and a dead-letter path
   for what still fails; a poison message must not block the stream.
6. **Real-time push is a transport, not the source of truth.** WebSocket/SSE deliver
   state that already committed; never let a live connection be the only record.
   `references/realtime-push.md`.

## Pick the mechanism

| Need | Mechanism | Notes |
|------|-----------|-------|
| decouple work, load-level, retries | **task queue** (SQS, RabbitMQ, Redis, Celery/RQ) | at-least-once; make handlers idempotent |
| ordered, replayable event log, fan-out | **log/stream** (Kafka, Redis Streams, Pulsar) | partition key sets ordering + parallelism |
| run at a time / interval | **scheduler** (cron, Cloud Scheduler, Temporal, APScheduler) | idempotent jobs; guard against overlap |
| discrete rounds / batch clearing | scheduled trigger + transactional batch | close the round, process atomically, publish result |
| push updates to clients | **WebSocket** (bidirectional) / **SSE** (server→client) | SSE simpler when one-way; scale via a pub/sub fan-out |
| long multi-step workflow with state | **workflow engine** (Temporal, Step Functions) | durable state, retries, compensation |

## Correctness checklist (the part that bites)

- **Idempotency:** does replaying a message change the outcome? Key handlers on a
  business id + an idempotency token; dedupe on it.
- **Ordering:** what is the ordering unit (per user? per market? none)? Use it as the
  partition key; do not assume global order.
- **Exactly-once illusion:** achieved as at-least-once delivery + idempotent effect, or
  transactional outbox + dedupe — not by the broker alone.
- **Atomic state + publish:** use the **transactional outbox** so "update DB and emit
  event" cannot half-happen. `references/delivery-guarantees.md`.
- **Backpressure:** bounded queues, consumer concurrency limits, and a shed/slow policy
  when depth grows.
- **Failure:** retry with exponential backoff + jitter; dead-letter after N; alert on
  DLQ depth.

## The design loop

1. **EVENTS** — identify the events and their producers/consumers; draw the flow.
2. **MECHANISM** — pick queue vs stream vs scheduler vs push from the table.
3. **ORDERING + IDEMPOTENCY** — set the partition key and the dedupe key together.
4. **GUARANTEES** — choose delivery semantics; add outbox/DLQ/retry.
5. **BACKPRESSURE + SCALE** — bound buffers, set consumer concurrency, define overload
   behavior.
6. **PUSH** — if clients need live updates, add WebSocket/SSE fed from the same events.

## Deliverables

- An event flow (producers → transport → consumers) with the partition/ordering key.
- Delivery semantics stated (at-least-once + idempotent, outbox, DLQ policy).
- Backpressure and failure behavior defined, not implied.
- Real-time transport choice (WS/SSE) and how it scales, if applicable.

## Boundaries

- **Not** the synchronous REST API — that is `web-api-dev` (they compose: REST accepts,
  events process).
- **Not** the middleware product choice — that is `tech-selector` (which broker/stream).
- **Not** the business logic run per event — the dev skills / `optimization-modeling`.
