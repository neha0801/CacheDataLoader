"""Tests for the prompt builder itself.

Run with: python -m pytest testgen/tests -q
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import testgen  # noqa: E402

EXAMPLE_SPEC = Path(__file__).resolve().parents[1] / "examples" / "bookstore-openapi.yaml"


def build(**kwargs) -> str:
    """Build a prompt from CLI-style arguments."""
    argv: list[str] = []
    for key, value in kwargs.items():
        flag = "--" + key.replace("_", "-")
        if isinstance(value, list):
            for item in value:
                argv += [flag, item]
        else:
            argv += [flag, str(value)]
    return testgen.build_prompt(testgen.parse_args(argv))


# -- rendering ------------------------------------------------------------


def test_render_fills_placeholders():
    assert testgen.render("a {{X}} b", {"X": "1"}) == "a 1 b"


def test_render_rejects_unfilled_placeholder():
    with pytest.raises(testgen.TestgenError, match="MISSING"):
        testgen.render("{{MISSING}}", {})


def test_every_template_placeholder_is_supplied():
    """A new placeholder in a target template must not silently ship unfilled."""
    for path in (testgen.TEMPLATES / "targets").glob("*.md"):
        target = path.stem
        prompt = build(spec=str(EXAMPLE_SPEC), target=target)
        assert "{{" not in prompt, f"{target} left a placeholder unfilled"


# -- catalogue integrity --------------------------------------------------


def test_every_catalogue_entry_has_a_template():
    for name in testgen.TARGETS:
        assert (testgen.TEMPLATES / "targets" / f"{name}.md").is_file()
    for _, (filename, _) in testgen.FRAMEWORKS.items():
        assert (testgen.TEMPLATES / "frameworks" / f"{filename}.md").is_file()
    for name in testgen.FOCUS_AREAS:
        assert (testgen.TEMPLATES / "focus" / f"{name}.md").is_file()
    for name in testgen.DEPTHS:
        assert (testgen.TEMPLATES / "_shared" / f"depth-{name}.md").is_file()


def test_default_framework_covers_every_target():
    assert set(testgen.DEFAULT_FRAMEWORK) == set(testgen.TARGETS)
    assert set(testgen.DEFAULT_FRAMEWORK.values()) <= set(testgen.FRAMEWORKS)


# -- OpenAPI summarising --------------------------------------------------


def test_openapi_summary_carries_constraints_and_operations():
    prompt = build(spec=str(EXAMPLE_SPEC))

    # Every operation reaches the prompt.
    for path in ("GET /books", "POST /books", "PATCH /books/{bookId}", "POST /books/{bookId}/loans"):
        assert f"`{path}`" in prompt

    # Boundaries survive the flattening — this is what the cases are derived from.
    assert "max: 100" in prompt
    assert "maxLength: 300" in prompt
    assert r"pattern: ^\d{13}$" in prompt
    assert 'enum: "available", "on_loan", "withdrawn"' in prompt

    # $refs are resolved rather than passed through.
    assert "$ref" not in prompt
    assert "**required**" in prompt

    # Per-operation security overrides the document default.
    assert "none (public)" in prompt


def test_metadata_is_inferred_from_the_spec():
    prompt = build(spec=str(EXAMPLE_SPEC))
    assert "Bookstore API" in prompt
    assert "https://api.bookstore.example.com/v1" in prompt
    assert "bearer" in prompt


def test_explicit_flags_override_inferred_metadata():
    prompt = build(spec=str(EXAMPLE_SPEC), name="Custom", base_url="http://localhost:8080")
    assert "**Name:** Custom" in prompt
    assert "http://localhost:8080" in prompt


def test_swagger2_document(tmp_path: Path):
    spec = tmp_path / "swagger.json"
    spec.write_text(
        json.dumps(
            {
                "swagger": "2.0",
                "info": {"title": "Legacy", "version": "1.0"},
                "host": "legacy.example.com",
                "basePath": "/api",
                "schemes": ["https"],
                "paths": {
                    "/things": {
                        "post": {
                            "operationId": "createThing",
                            "parameters": [
                                {
                                    "in": "body",
                                    "name": "body",
                                    "required": True,
                                    "schema": {"$ref": "#/definitions/Thing"},
                                }
                            ],
                            "responses": {"201": {"description": "created"}},
                        }
                    }
                },
                "definitions": {
                    "Thing": {
                        "type": "object",
                        "required": ["label"],
                        "properties": {"label": {"type": "string", "maxLength": 40}},
                    }
                },
            }
        )
    )
    prompt = build(spec=str(spec))
    assert "https://legacy.example.com/api" in prompt
    assert "maxLength: 40" in prompt


def test_circular_ref_does_not_hang(tmp_path: Path):
    spec = tmp_path / "cycle.json"
    spec.write_text(
        json.dumps(
            {
                "openapi": "3.0.0",
                "info": {"title": "Cycle", "version": "1"},
                "paths": {
                    "/node": {
                        "get": {
                            "responses": {
                                "200": {
                                    "description": "ok",
                                    "content": {
                                        "application/json": {
                                            "schema": {"$ref": "#/components/schemas/Node"}
                                        }
                                    },
                                }
                            }
                        }
                    }
                },
                "components": {
                    "schemas": {
                        "Node": {
                            "type": "object",
                            "properties": {"child": {"$ref": "#/components/schemas/Node"}},
                        }
                    }
                },
            }
        )
    )
    assert "GET /node" in build(spec=str(spec))


# -- other spec formats ---------------------------------------------------


def test_graphql_sdl_is_detected_and_indexed(tmp_path: Path):
    spec = tmp_path / "schema.graphql"
    spec.write_text(
        "type Query {\n  book(id: ID!): Book\n}\n"
        "type Mutation {\n  borrow(id: ID!): Loan!\n}\n"
        "type Book { id: ID! title: String! }\n"
        "type Loan { id: ID! }\n"
    )
    prompt = build(spec=str(spec))
    assert "GraphQL" in prompt
    assert "**Query** (1 fields)" in prompt
    assert "partial success" in prompt.lower()


def test_postman_collection_is_detected(tmp_path: Path):
    spec = tmp_path / "collection.json"
    spec.write_text(
        json.dumps(
            {
                "info": {"name": "Suite", "schema": "v2.1.0"},
                "item": [
                    {
                        "name": "Books",
                        "item": [
                            {
                                "name": "list",
                                "request": {
                                    "method": "GET",
                                    "url": {"raw": "https://x.example.com/books"},
                                },
                            }
                        ],
                    }
                ],
            }
        )
    )
    prompt = build(spec=str(spec))
    assert "Books / list" in prompt
    assert "REST" in prompt


def test_free_text_description_needs_an_explicit_target():
    prompt = build(target="web", describe="A checkout flow", base_url="https://shop.example.com")
    assert "A checkout flow" in prompt
    assert "getByRole" in prompt  # the default web framework block


# -- assembly -------------------------------------------------------------


def test_sections_are_assembled_in_order():
    prompt = build(spec=str(EXAMPLE_SPEC), depth="exhaustive", focus=["security", "contract"])
    order = [
        "senior SDET",
        "Test design techniques",
        "Coverage depth: EXHAUSTIVE",
        "Additional focus: SECURITY",
        "Additional focus: CONTRACT",
        "Target framework",
        "How to answer",
    ]
    positions = [prompt.index(section) for section in order]
    assert positions == sorted(positions)


def test_focus_is_absent_unless_requested():
    assert "Additional focus" not in build(spec=str(EXAMPLE_SPEC))


def test_depth_default_is_standard():
    assert "Coverage depth: STANDARD" in build(spec=str(EXAMPLE_SPEC))


# -- errors ---------------------------------------------------------------


def test_missing_input_is_an_error():
    with pytest.raises(testgen.TestgenError, match="--spec"):
        build()


def test_missing_spec_file_is_an_error():
    with pytest.raises(testgen.TestgenError, match="not found"):
        build(spec="/nonexistent/spec.yaml")


def test_openapi_without_operations_is_an_error(tmp_path: Path):
    spec = tmp_path / "empty.json"
    spec.write_text(json.dumps({"openapi": "3.0.0", "info": {"title": "E"}, "paths": {}}))
    with pytest.raises(testgen.TestgenError, match="no operations"):
        build(spec=str(spec))


def test_cli_reports_error_without_traceback(capsys):
    assert testgen.main([]) == 2
    assert "testgen:" in capsys.readouterr().err


def test_cli_writes_output_file(tmp_path: Path):
    out = tmp_path / "nested" / "prompt.md"
    assert testgen.main(["--spec", str(EXAMPLE_SPEC), "--out", str(out)]) == 0
    assert "senior SDET" in out.read_text()


def test_cli_list_exits_clean(capsys):
    assert testgen.main(["--list"]) == 0
    assert "Frameworks" in capsys.readouterr().out
