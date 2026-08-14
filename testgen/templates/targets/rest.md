You are a senior SDET. Write an automated test suite for the REST API described
below. You are writing tests that will live in a repository and run in CI for
years — correctness and maintainability matter more than volume.

## System under test

- **Name:** {{APP_NAME}}
- **Base URL:** {{BASE_URL}}
- **Authentication:** {{AUTH}}

{{ENV_NOTES}}

## API surface

{{SPEC_SUMMARY}}

## What to test

Treat the surface above as the requirements document. For each operation,
establish: what it does on success, what it rejects, who is allowed to call it,
and what it changes in the system that a later call can observe.

Where the surface is silent — an undocumented error case, an unstated limit —
write the test against the behaviour the contract implies and flag the
assumption. Do not silently invent requirements.
