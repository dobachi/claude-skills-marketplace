# Real-time push to clients

Delivering updates to browsers/apps as they happen. The transport carries **already-
committed** state; it is never the system of record.

## WebSocket vs SSE vs polling

| | **WebSocket** | **SSE** (EventSource) | **Long/short polling** |
|---|---|---|---|
| Direction | bidirectional | server → client only | client pulls |
| Transport | ws:// upgrade | plain HTTP stream | HTTP |
| Reconnect/replay | manual | **built-in** (auto-reconnect, `Last-Event-ID`) | n/a |
| Proxies/simplicity | more setup | simplest, HTTP-native | simplest, least efficient |
| Use when | client also sends frequently (chat, live editing, bidding UI) | one-way feeds (tickers, notifications, progress) | fallback, low-frequency updates |

**Default:** SSE for one-way feeds (simpler, auto-reconnect, replay via `Last-Event-ID`);
WebSocket when the client streams to the server too; polling only as a fallback.

## Scaling fan-out

- A push server holds many long-lived connections; a single instance cannot hold them
  all. Put a **pub/sub backplane** (Redis pub/sub, Kafka, NATS) between the event source
  and the push instances so any instance can deliver to its connected clients.
- Track subscriptions by topic/user; fan an event only to interested connections.
- Connections are **stateful** — plan for sticky routing or a shared backplane, graceful
  drain on deploy, and connection limits per instance.

## Correctness at the edge

- **Push reflects committed state.** Emit to clients from the same events that came off
  the outbox/stream, after commit — not from an in-flight, uncommitted change.
- **Missed-while-disconnected:** clients reconnect and must catch up. Give events
  sequence ids; on reconnect the client sends its last id and the server replays the gap
  (SSE `Last-Event-ID`, or a since-cursor API). Without this, a dropped connection = lost
  updates.
- **Idempotent client apply:** the client may receive a duplicate after reconnect; apply
  by event id so re-delivery is harmless (same principle as `delivery-guarantees.md`).
- **Auth on the stream:** authenticate at connect and re-check on token expiry; a
  long-lived socket outlives a short-lived token.

## Backpressure toward slow clients

- A slow client must not balloon server memory. Bound the per-connection outbound buffer;
  on overflow, drop the connection (client reconnects and replays) rather than buffer
  unboundedly.
- For high-rate feeds, **coalesce/sample** (send latest state, not every tick) per client
  based on its drain rate.
