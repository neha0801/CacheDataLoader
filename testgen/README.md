# testgen

Build a prompt that makes an LLM write automated tests for any app.

`testgen` is not a test generator and it does not call a model. It is the step
before that: it reads whatever machine-readable description of your app you
already have — an OpenAPI document, a GraphQL schema, a Postman collection, or a
page of prose — flattens it into a summary a model can actually use, and
assembles it with test-design guidance, a coverage depth, and your framework's
conventions into one prompt you paste into any assistant.

The reason to do this rather than paste the spec directly: "write tests for this
API" produces twenty happy-path cases and no boundary analysis. The output here
asks for a coverage plan first, then runnable code, then an explicit list of what
the model had to assume — and it hands the model the constraints (lengths,
ranges, enums, required-ness, auth per operation) that boundary cases are
actually derived from.

```console
$ python testgen.py --spec examples/bookstore-openapi.yaml \
                    --framework pytest --focus security --out prompt.md
wrote prompt.md (13,915 chars, ~2,950 tokens)
```

[`examples/bookstore-prompt.md`](examples/bookstore-prompt.md) is the committed
output of that command, generated from
[`examples/bookstore-openapi.yaml`](examples/bookstore-openapi.yaml).

## Install

Python 3.10+, no required dependencies. `PyYAML` is optional and only needed for
YAML specs; JSON works without it.

```console
$ pip install -r requirements.txt   # optional
$ python testgen.py --list
```

## Usage

```console
# REST API from an OpenAPI file
python testgen.py --spec openapi.yaml --framework pytest --out prompt.md

# From a live spec URL, going deep, with two focus areas
python testgen.py --spec https://api.example.com/openapi.json \
                  --depth exhaustive --focus security --focus contract

# A web app, with no spec file — just describe it
python testgen.py --target web --framework playwright-ts \
                  --describe 'Checkout: cart → address → payment → confirmation' \
                  --base-url https://shop.example.com

# A GraphQL schema, inferring the target from the file
python testgen.py --spec schema.graphql --framework jest
```

Then paste `prompt.md` into your assistant of choice.

| Flag | Meaning |
|------|---------|
| `--spec` | Path or URL to an OpenAPI / Swagger, GraphQL SDL, Postman collection, `.proto`, or plain-text spec. The format is detected, not declared. |
| `--describe` | Free-text description, when there is no spec file. |
| `--target` | `rest`, `graphql`, `grpc`, `web`, `mobile`, `cli`. Inferred from the spec when omitted. |
| `--framework` | `pytest`, `restassured`, `postman`, `playwright-ts`, `playwright-py`, `karate`, `jest`. |
| `--depth` | `smoke`, `standard` (default), `exhaustive`. |
| `--focus` | Repeatable: `security`, `performance`, `accessibility`, `contract`, `data-integrity`. |
| `--name` `--base-url` `--auth` | Override what was inferred from the spec. |
| `--notes` | Environment notes — test accounts, rate limits, quirks the model cannot know. |
| `--out` `-o` | Write to a file instead of stdout. |

## What the prompt asks for

Every generated prompt demands the same three-part answer, which is what makes
the output reviewable rather than a wall of code:

1. **A coverage plan** — a table of cases with ids, priority, and expected
   result, written *before* any code, with inferred requirements marked
   `(assumed)`.
2. **Runnable test code** — complete, with fixtures and cleanup, each case
   carrying its plan id so the two can be diffed.
3. **Notes for the human** — assumptions, gaps, defects found *in the spec*, and
   the exact commands to run the suite.

## How a prompt is assembled

```
targets/<target>.md        the role, the system under test, the flattened spec
_shared/techniques.md      equivalence classes, boundaries, state, authz matrix
_shared/depth-<depth>.md   how many cases, and which ones to drop
focus/<area>.md            zero or more add-on sections
frameworks/<framework>.md  idioms, fixtures, selectors, what to deliver
_shared/output-contract.md the three-part answer format
```

Sections are plain markdown with `{{PLACEHOLDER}}` slots. Adding a framework or
a focus area means dropping a file in the right directory and adding one line to
the table at the top of `testgen.py` — the test suite fails if a catalogue entry
has no template, or if a template has a placeholder nothing fills.

## Spec handling

OpenAPI 3 and Swagger 2 get real treatment rather than being pasted through:
local `$ref`s are resolved (with a cycle guard), `allOf` is merged, and each
operation is rendered with its parameters, request-body fields, and responses —
carrying `minLength`, `maximum`, `pattern`, `enum`, `required`, `nullable`, and
per-operation security overrides. Those constraints are the raw material for
boundary and negative cases, and they are exactly what gets lost when a 5000-line
spec is truncated into a context window.

GraphQL SDL is indexed by root type and then included verbatim. Postman
collections are walked into a flat request table with raw bodies. Anything
unrecognised is passed through as prose, which is a supported path, not a
failure.

## Tests

```console
$ pip install pytest
$ python -m pytest tests -q
22 passed
```

## Limitations

- The tool builds a prompt; it does not run the model, run the generated tests,
  or verify that they pass. Review the coverage plan before trusting the code.
- Remote `$ref`s (`$ref` to another file or URL) are not followed — bundle the
  spec first with something like `redocly bundle`.
- GraphQL introspection JSON is rejected with a pointer to convert it to SDL.
- Very large specs will still overflow a context window. Split by tag or path
  prefix and generate one prompt per area; the coverage plans concatenate fine.
