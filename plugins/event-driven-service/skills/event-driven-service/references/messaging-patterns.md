# Messaging patterns

## Queue vs log — the first decision

| | **Task queue** (RabbitMQ, SQS, Redis) | **Log / stream** (Kafka, Pulsar, Redis Streams) |
|---|---|---|
| Consumption | message removed when acked | offset-based; retained, replayable |
| Fan-out | one consumer per message (work sharing) | many independent consumers, each own offset |
| Ordering | weak/none across consumers | ordered **within a partition** |
| Replay | no (gone once acked) | yes (rewind offset) |
| Use for | distribute work, RPC-ish jobs | event sourcing, audit, multi-consumer fan-out, replay |

Choose a queue to *distribute work*; choose a log to *distribute events* many parties
consume and may replay.

## Delivery topologies

- **Point-to-point:** one producer, one logical consumer group sharing the load.
- **Publish/subscribe:** one event, N independent subscribers (log, or queue with
  per-subscriber queues / an exchange fan-out).
- **Competing consumers:** scale a consumer group horizontally; the transport shards
  work across instances (queue: prefetch; log: partitions ≥ consumers).
- **Request/reply over messaging:** correlation id + reply queue; prefer sync REST
  unless you specifically need the decoupling.

## Ordering and partitioning

- Ordering exists **only within a partition/key**. Pick the partition key as the
  smallest unit that must stay ordered (e.g. per account, per market) — that key also
  caps parallelism for that unit.
- Global ordering means one partition means no horizontal scaling. Almost never worth it;
  find the real ordering requirement.
- Rebalancing (log consumer groups) reorders across partitions during scaling — handlers
  must tolerate it.

## Backpressure and overload

- **Bounded buffers everywhere.** An unbounded queue just moves the failure to OOM.
- **Consumer concurrency limits** (prefetch / max in-flight) so one consumer cannot pull
  more than it can process.
- **Overload policy — choose explicitly:** slow the producer (blocking/credits), buffer
  to a bound then reject, or shed/sample load. Silent drop is a bug; document the choice.
- **Monitor depth and lag** (queue depth, consumer lag) as the primary health signal;
  alert before the buffer bound.

## Retries, DLQ, poison messages

- **Retry** with exponential backoff **+ jitter** (avoid thundering herds). Cap attempts.
- **Dead-letter queue** for messages that exhaust retries; alert on DLQ depth and have a
  reprocess/repair path. A poison message must be routed aside, never block its partition.
- Distinguish **retryable** (transient: timeout, 503) from **non-retryable** (bad
  payload) — send non-retryable straight to DLQ; do not burn retries on it.

## Schema and evolution

- Version event schemas; prefer additive, backward-compatible changes (a consumer on an
  old schema must still parse). Use a schema registry for streams shared across teams.
- Include an event `type` + `version` + a stable `id` (for idempotency/dedupe) in every
  envelope.
