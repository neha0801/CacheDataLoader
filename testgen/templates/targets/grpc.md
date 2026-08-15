You are a senior SDET. Write an automated test suite for the gRPC service
described below.

## System under test

- **Name:** {{APP_NAME}}
- **Target:** {{BASE_URL}}
- **Authentication:** {{AUTH}}

{{ENV_NOTES}}

## Service definition

{{SPEC_SUMMARY}}

## What to test

- **Status codes** — assert the specific `grpc.StatusCode` (`INVALID_ARGUMENT`,
  `NOT_FOUND`, `PERMISSION_DENIED`, `FAILED_PRECONDITION`, `ALREADY_EXISTS`) and
  the status details, not merely that the call raised.
- **Proto3 defaults** — an unset scalar is indistinguishable from its zero
  value. Test that the service treats "field absent" and "field = 0 / empty
  string / false" as the spec says it should, and flag it if the spec is silent.
- **Streaming** — for each streaming method: zero messages, one message, many
  messages, a client that closes early, a server that ends the stream mid-flow,
  and back-pressure on a slow consumer.
- **Deadlines** — a call with an expired deadline returns
  `DEADLINE_EXCEEDED`, and the server stops work rather than completing it.
- **Cancellation** — a cancelled call leaves no partial side effect.
- **Metadata** — required headers present, absent, and malformed; trailing
  metadata on both success and error.
- **Message limits** — a payload at and just above the configured max size.
- **Compatibility** — unknown fields on the wire are preserved through a
  round-trip, so an older client and a newer server interoperate.
