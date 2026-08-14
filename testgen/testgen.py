#!/usr/bin/env python3
"""testgen — build a prompt that makes an LLM write automated tests for any app.

The tool does not call a model. It reads whatever machine-readable description
of your app you already have (an OpenAPI document, a GraphQL schema, a Postman
collection, or a page of prose), turns it into a compact, unambiguous summary,
and assembles it with test-design guidance and framework conventions into a
single prompt you can paste into any assistant.

    python testgen.py --spec openapi.yaml --framework pytest --out prompt.md

Run `python testgen.py --list` to see the available targets, frameworks, and
focus areas.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

TEMPLATES = Path(__file__).resolve().parent / "templates"

TARGETS = {
    "rest": "REST / HTTP API",
    "graphql": "GraphQL API",
    "grpc": "gRPC service",
    "web": "Web application (browser end-to-end)",
    "mobile": "Mobile application (iOS / Android)",
    "cli": "Command-line tool",
}

FRAMEWORKS = {
    "pytest": ("pytest-requests", "pytest + requests (Python)"),
    "restassured": ("restassured-junit5", "REST Assured + JUnit 5 (Java)"),
    "postman": ("postman-newman", "Postman collection + Newman"),
    "playwright-ts": ("playwright-ts", "Playwright Test (TypeScript)"),
    "playwright-py": ("playwright-python", "Playwright for Python (pytest)"),
    "karate": ("karate", "Karate DSL"),
    "jest": ("jest-supertest", "Jest + Supertest (Node / TypeScript)"),
}

FOCUS_AREAS = {
    "security": "Authorization, injection, token handling, disclosure",
    "performance": "Latency budgets, payload size, concurrency, caching",
    "accessibility": "WCAG 2.2 AA on the critical journeys",
    "contract": "Schema, status codes, headers, serialization edges",
    "data-integrity": "Read-your-writes, atomicity, concurrency, round-trips",
}

DEPTHS = ("smoke", "standard", "exhaustive")

# Framework suggestions when the user does not pick one.
DEFAULT_FRAMEWORK = {
    "rest": "pytest",
    "graphql": "pytest",
    "grpc": "pytest",
    "web": "playwright-ts",
    "mobile": "pytest",
    "cli": "pytest",
}


class TestgenError(Exception):
    """A problem with the user's input, reported without a traceback."""


# --------------------------------------------------------------------------
# Template loading and rendering
# --------------------------------------------------------------------------


def read_template(*parts: str) -> str:
    path = TEMPLATES.joinpath(*parts)
    if not path.is_file():
        raise TestgenError(f"missing template: {path}")
    return path.read_text(encoding="utf-8").rstrip() + "\n"


def render(template: str, context: dict[str, str]) -> str:
    """Substitute {{KEY}} placeholders, refusing to emit an unfilled one."""
    out = re.sub(
        r"\{\{(\w+)\}\}",
        lambda m: context.get(m.group(1), m.group(0)),
        template,
    )
    leftover = sorted(set(re.findall(r"\{\{(\w+)\}\}", out)))
    if leftover:
        raise TestgenError(f"template placeholders were not filled: {', '.join(leftover)}")
    return re.sub(r"\n{3,}", "\n\n", out)


# --------------------------------------------------------------------------
# Spec loading
# --------------------------------------------------------------------------


def load_document(source: str) -> tuple[Any, str]:
    """Return (parsed document or raw text, raw text) for a path or URL."""
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=30) as response:  # noqa: S310
            raw = response.read().decode("utf-8")
    else:
        path = Path(source).expanduser()
        if not path.is_file():
            raise TestgenError(f"spec not found: {source}")
        raw = path.read_text(encoding="utf-8")

    try:
        return json.loads(raw), raw
    except json.JSONDecodeError:
        pass

    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return None, raw

    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None, raw
    return (parsed if isinstance(parsed, dict) else None), raw


def detect_kind(doc: Any, raw: str) -> str:
    """Classify a spec so the right summariser and target can be chosen."""
    if isinstance(doc, dict):
        if "openapi" in doc or "swagger" in doc:
            return "openapi"
        if "info" in doc and "item" in doc:
            return "postman"
        if isinstance(doc.get("data"), dict) and "__schema" in doc["data"]:
            return "graphql-introspection"
        if "__schema" in doc:
            return "graphql-introspection"
    if re.search(r"^\s*type\s+(Query|Mutation)\b", raw, re.MULTILINE):
        return "graphql-sdl"
    if re.search(r"^\s*(service|message)\s+\w+\s*\{", raw, re.MULTILINE):
        return "protobuf"
    return "text"


# --------------------------------------------------------------------------
# OpenAPI / Swagger summarising
# --------------------------------------------------------------------------

HTTP_METHODS = ("get", "post", "put", "patch", "delete", "head", "options", "trace")

CONSTRAINT_KEYS = (
    ("enum", "enum"),
    ("minimum", "min"),
    ("maximum", "max"),
    ("exclusiveMinimum", "exclusiveMin"),
    ("exclusiveMaximum", "exclusiveMax"),
    ("minLength", "minLength"),
    ("maxLength", "maxLength"),
    ("minItems", "minItems"),
    ("maxItems", "maxItems"),
    ("pattern", "pattern"),
    ("default", "default"),
)


class OpenApiSummariser:
    """Flatten an OpenAPI 3 or Swagger 2 document into reviewable markdown.

    The point is to give the model every constraint it needs to derive boundary
    cases — lengths, ranges, enums, required-ness — without pasting a 5000-line
    document that buries them.
    """

    def __init__(self, doc: dict[str, Any]) -> None:
        self.doc = doc
        self.swagger2 = "swagger" in doc and "openapi" not in doc

    # -- $ref handling ----------------------------------------------------

    def deref(self, node: Any, seen: frozenset[str] = frozenset()) -> Any:
        """Resolve a local $ref, guarding against reference cycles."""
        while isinstance(node, dict) and "$ref" in node:
            ref = node["$ref"]
            if not isinstance(ref, str) or not ref.startswith("#/") or ref in seen:
                return {}
            target: Any = self.doc
            for part in ref[2:].split("/"):
                part = part.replace("~1", "/").replace("~0", "~")
                if not isinstance(target, dict) or part not in target:
                    return {}
                target = target[part]
            seen = seen | {ref}
            node = target
        return node

    @staticmethod
    def ref_name(node: Any) -> str | None:
        if isinstance(node, dict) and isinstance(node.get("$ref"), str):
            return node["$ref"].rsplit("/", 1)[-1]
        return None

    # -- schema rendering -------------------------------------------------

    def type_of(self, schema: dict[str, Any]) -> str:
        for key in ("oneOf", "anyOf", "allOf"):
            if key in schema:
                names = [self.ref_name(s) or self.type_of(self.deref(s)) for s in schema[key]]
                joiner = " & " if key == "allOf" else " | "
                return joiner.join(n for n in names if n) or "object"
        type_name = schema.get("type")
        if isinstance(type_name, list):
            type_name = "|".join(str(t) for t in type_name)
        if type_name == "array":
            items = schema.get("items", {})
            inner = self.ref_name(items) or self.type_of(self.deref(items))
            return f"array<{inner}>"
        if not type_name:
            return "object" if "properties" in schema else "any"
        fmt = schema.get("format")
        return f"{type_name}({fmt})" if fmt else str(type_name)

    def constraints_of(self, schema: dict[str, Any]) -> str:
        bits = []
        for key, label in CONSTRAINT_KEYS:
            if key not in schema:
                continue
            value = schema[key]
            if key == "enum" and isinstance(value, list):
                bits.append(f"enum: {', '.join(json.dumps(v) for v in value)}")
            else:
                bits.append(f"{label}: {json.dumps(value) if not isinstance(value, str) else value}")
        if schema.get("nullable"):
            bits.append("nullable")
        if schema.get("readOnly"):
            bits.append("readOnly")
        if schema.get("writeOnly"):
            bits.append("writeOnly")
        return " · ".join(bits)

    def fields(self, schema: Any, depth: int = 0, prefix: str = "") -> list[str]:
        """Render a schema's leaf fields as bullet lines, two levels deep."""
        schema = self.deref(schema)
        if not isinstance(schema, dict):
            return []

        merged: dict[str, Any] = {}
        required: list[str] = list(schema.get("required") or [])
        for part in schema.get("allOf") or []:
            part = self.deref(part)
            merged.update(part.get("properties") or {})
            required.extend(part.get("required") or [])
        merged.update(schema.get("properties") or {})

        if not merged and schema.get("type") == "array":
            return self.fields(schema.get("items", {}), depth, prefix)
        if not merged:
            return []

        lines: list[str] = []
        for name, raw_child in merged.items():
            child = self.deref(raw_child)
            if not isinstance(child, dict):
                continue
            label = f"{prefix}{name}"
            parts = [f"`{label}` {self.ref_name(raw_child) or self.type_of(child)}"]
            if name in required:
                parts.append("**required**")
            constraints = self.constraints_of(child)
            if constraints:
                parts.append(constraints)
            description = str(child.get("description") or "").strip().splitlines()
            if description:
                parts.append(description[0][:120])
            lines.append("- " + " — ".join(parts))

            if depth < 1:
                nested = child if child.get("type") != "array" else self.deref(child.get("items", {}))
                if isinstance(nested, dict) and (nested.get("properties") or nested.get("allOf")):
                    lines.extend(self.fields(nested, depth + 1, f"{label}."))
        return lines

    # -- document sections ------------------------------------------------

    def servers(self) -> list[str]:
        if self.swagger2:
            host = self.doc.get("host")
            if not host:
                return []
            base = self.doc.get("basePath", "")
            schemes = self.doc.get("schemes") or ["https"]
            return [f"{scheme}://{host}{base}" for scheme in schemes]
        return [
            str(s.get("url"))
            for s in (self.doc.get("servers") or [])
            if isinstance(s, dict) and s.get("url")
        ]

    def security_schemes(self) -> list[str]:
        container = (
            self.doc.get("securityDefinitions")
            if self.swagger2
            else (self.doc.get("components") or {}).get("securitySchemes")
        )
        lines = []
        for name, scheme in (container or {}).items():
            scheme = self.deref(scheme)
            if not isinstance(scheme, dict):
                continue
            kind = scheme.get("type", "?")
            detail = []
            if scheme.get("scheme"):
                detail.append(str(scheme["scheme"]))
            if scheme.get("in"):
                detail.append(f"in {scheme['in']}")
            if scheme.get("name"):
                detail.append(f"as `{scheme['name']}`")
            if scheme.get("bearerFormat"):
                detail.append(str(scheme["bearerFormat"]))
            suffix = f" ({', '.join(detail)})" if detail else ""
            lines.append(f"- `{name}` — {kind}{suffix}")
        return lines

    def operations(self) -> list[tuple[str, str, dict[str, Any], list[Any]]]:
        out = []
        for path, item in (self.doc.get("paths") or {}).items():
            item = self.deref(item)
            if not isinstance(item, dict):
                continue
            shared = item.get("parameters") or []
            for method in HTTP_METHODS:
                operation = item.get(method)
                if isinstance(operation, dict):
                    out.append((method.upper(), str(path), operation, shared))
        return out

    def parameters(self, operation: dict[str, Any], shared: list[Any]) -> list[str]:
        lines = []
        for raw in list(shared) + list(operation.get("parameters") or []):
            param = self.deref(raw)
            if not isinstance(param, dict) or not param.get("name"):
                continue
            schema = self.deref(param.get("schema") or {}) or {
                k: v for k, v in param.items() if k in {"type", "format", "enum", "items"}
            }
            parts = [f"`{param['name']}` in {param.get('in', '?')}", self.type_of(schema)]
            if param.get("required"):
                parts.append("**required**")
            constraints = self.constraints_of(schema)
            if constraints:
                parts.append(constraints)
            description = str(param.get("description") or "").strip().splitlines()
            if description:
                parts.append(description[0][:120])
            lines.append("- " + " — ".join(parts))
        return lines

    def request_body(self, operation: dict[str, Any]) -> list[str]:
        if self.swagger2:
            for raw in operation.get("parameters") or []:
                param = self.deref(raw)
                if isinstance(param, dict) and param.get("in") == "body":
                    required = " (required)" if param.get("required") else ""
                    body = self.fields(param.get("schema") or {})
                    return [f"**Request body**{required}:", *body] if body else []
            return []

        body = self.deref(operation.get("requestBody") or {})
        if not isinstance(body, dict) or not body.get("content"):
            return []
        required = " (required)" if body.get("required") else ""
        lines = []
        for media_type, media in body["content"].items():
            media = self.deref(media)
            if not isinstance(media, dict):
                continue
            schema_name = self.ref_name(media.get("schema")) or ""
            heading = f"**Request body** `{media_type}`{required}"
            if schema_name:
                heading += f" → `{schema_name}`"
            lines.append(heading + ":")
            lines.extend(self.fields(media.get("schema") or {}) or ["- (schema not described)"])
        return lines

    def responses(self, operation: dict[str, Any]) -> list[str]:
        lines = []
        for code, raw in (operation.get("responses") or {}).items():
            response = self.deref(raw)
            if not isinstance(response, dict):
                continue
            description = str(response.get("description") or "").strip().splitlines()
            summary = description[0] if description else ""
            schema_name = ""
            if self.swagger2:
                schema_name = self.ref_name(response.get("schema")) or ""
            else:
                for media in (response.get("content") or {}).values():
                    media = self.deref(media)
                    if isinstance(media, dict):
                        schema_name = self.ref_name(media.get("schema")) or ""
                        if schema_name:
                            break
            suffix = f" → `{schema_name}`" if schema_name else ""
            lines.append(f"- `{code}` — {summary}{suffix}".rstrip())
        return lines

    def summarise(self) -> str:
        info = self.doc.get("info") or {}
        out: list[str] = []

        title = info.get("title")
        if title:
            version = info.get("version")
            out.append(f"**Spec:** {title}" + (f" v{version}" if version else ""))
        description = str(info.get("description") or "").strip()
        if description:
            out.append(description[:600])

        servers = self.servers()
        if servers:
            out.append("**Servers:** " + ", ".join(f"`{s}`" for s in servers))

        schemes = self.security_schemes()
        if schemes:
            out.append("**Security schemes:**\n" + "\n".join(schemes))

        operations = self.operations()
        if not operations:
            raise TestgenError("the OpenAPI document declares no operations under `paths`")

        out.append(f"**Operations:** {len(operations)}")

        table = ["| Method | Path | Operation | Summary |", "|--------|------|-----------|---------|"]
        for method, path, operation, _ in operations:
            summary = str(operation.get("summary") or operation.get("description") or "")
            summary = summary.strip().splitlines()[0][:80] if summary.strip() else ""
            table.append(
                f"| `{method}` | `{path}` | {operation.get('operationId', '')} | {summary} |"
            )
        out.append("\n".join(table))

        out.append("### Operation detail")
        default_security = self.doc.get("security")
        for method, path, operation, shared in operations:
            chunks = [f"#### `{method} {path}`"]
            summary = str(operation.get("summary") or "").strip()
            if summary:
                chunks.append(summary)
            operation_description = str(operation.get("description") or "").strip()
            if operation_description and operation_description != summary:
                chunks.append(operation_description[:400])

            security = operation.get("security", default_security)
            if security is not None:
                names = sorted({name for entry in security or [] for name in entry})
                chunks.append(f"*Security:* {', '.join(f'`{n}`' for n in names) or 'none (public)'}")

            parameters = self.parameters(operation, shared)
            if parameters:
                chunks.append("**Parameters:**\n" + "\n".join(parameters))

            body = self.request_body(operation)
            if body:
                chunks.append(body[0] + "\n" + "\n".join(body[1:]))

            responses = self.responses(operation)
            if responses:
                chunks.append("**Responses:**\n" + "\n".join(responses))

            out.append("\n\n".join(chunks))

        return "\n\n".join(out).strip()


# --------------------------------------------------------------------------
# Other spec formats
# --------------------------------------------------------------------------


def summarise_graphql_sdl(raw: str) -> str:
    """Keep the schema verbatim but lead with an index of its entry points."""
    entry_points: list[str] = []
    for root in ("Query", "Mutation", "Subscription"):
        block = re.search(
            rf"^\s*(?:extend\s+)?type\s+{root}\b[^{{]*\{{(.*?)^\s*\}}",
            raw,
            re.MULTILINE | re.DOTALL,
        )
        if not block:
            continue
        fields = [
            line.strip()
            for line in block.group(1).splitlines()
            if line.strip() and not line.strip().startswith(("#", '"'))
        ]
        if fields:
            entry_points.append(f"**{root}** ({len(fields)} fields):")
            entry_points.extend(f"- `{f}`" for f in fields)
    header = "\n".join(entry_points) if entry_points else "_No root type found._"
    return f"{header}\n\n**Full schema:**\n\n```graphql\n{raw.strip()}\n```"


def summarise_postman(doc: dict[str, Any]) -> str:
    """Walk a Postman collection's folder tree into a flat request table."""
    rows: list[str] = []
    detail: list[str] = []

    def walk(items: list[Any], folder: str = "") -> None:
        for item in items or []:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", ""))
            if "item" in item:
                walk(item["item"], f"{folder}{name} / ")
                continue
            request = item.get("request")
            if isinstance(request, str):
                request = {"method": "GET", "url": request}
            if not isinstance(request, dict):
                continue
            method = str(request.get("method", "GET"))
            url = request.get("url")
            if isinstance(url, dict):
                url = url.get("raw") or "/".join(str(p) for p in (url.get("path") or []))
            rows.append(f"| `{method}` | `{url}` | {folder}{name} |")

            body = request.get("body") or {}
            if isinstance(body, dict) and body.get("mode") == "raw" and body.get("raw"):
                detail.append(f"#### `{method}` {folder}{name}\n\n```\n{str(body['raw'])[:800]}\n```")

    walk(doc.get("item") or [])
    if not rows:
        raise TestgenError("the Postman collection contains no requests")

    info = doc.get("info") or {}
    out = [f"**Collection:** {info.get('name', 'unnamed')}", f"**Requests:** {len(rows)}\n"]
    out += ["| Method | URL | Name |", "|--------|-----|------|", *rows]
    if detail:
        out.append("\n### Request bodies\n")
        out.extend(detail)
    return "\n".join(out)


def summarise_spec(source: str) -> tuple[str, str, dict[str, str]]:
    """Return (kind, markdown summary, metadata inferred from the spec)."""
    doc, raw = load_document(source)
    kind = detect_kind(doc, raw)
    meta: dict[str, str] = {}

    if kind == "openapi":
        summariser = OpenApiSummariser(doc)
        summary = summariser.summarise()
        info = doc.get("info") or {}
        if info.get("title"):
            meta["app_name"] = str(info["title"])
        servers = summariser.servers()
        if servers:
            meta["base_url"] = servers[0]
        schemes = summariser.security_schemes()
        if schemes:
            meta["auth"] = "; ".join(s.lstrip("- ") for s in schemes)
    elif kind in ("graphql-sdl", "graphql-introspection"):
        if kind == "graphql-introspection":
            raise TestgenError(
                "introspection JSON is not supported directly — convert it to SDL first "
                "(for example with `graphql-json-to-sdl`) and pass the .graphql file"
            )
        summary = summarise_graphql_sdl(raw)
    elif kind == "postman":
        summary = summarise_postman(doc)
        meta["app_name"] = str((doc.get("info") or {}).get("name") or "")
    elif kind == "protobuf":
        summary = f"**Service definition:**\n\n```protobuf\n{raw.strip()}\n```"
    else:
        summary = raw.strip()
        if not summary:
            raise TestgenError(f"spec is empty: {source}")

    return kind, summary, {k: v for k, v in meta.items() if v}


KIND_TO_TARGET = {
    "openapi": "rest",
    "postman": "rest",
    "graphql-sdl": "graphql",
    "graphql-introspection": "graphql",
    "protobuf": "grpc",
}


# --------------------------------------------------------------------------
# Prompt assembly
# --------------------------------------------------------------------------


def build_prompt(args: argparse.Namespace) -> str:
    summary = ""
    kind = "text"
    meta: dict[str, str] = {}

    if args.spec:
        kind, summary, meta = summarise_spec(args.spec)
    elif args.describe:
        summary = args.describe.strip()
    else:
        raise TestgenError("give me something to work from: --spec PATH_OR_URL or --describe TEXT")

    target = args.target or KIND_TO_TARGET.get(kind) or "rest"
    if target not in TARGETS:
        raise TestgenError(f"unknown target '{target}' (choose from: {', '.join(TARGETS)})")

    framework = args.framework or DEFAULT_FRAMEWORK[target]
    if framework not in FRAMEWORKS:
        raise TestgenError(f"unknown framework '{framework}' (choose from: {', '.join(FRAMEWORKS)})")

    if args.depth not in DEPTHS:
        raise TestgenError(f"unknown depth '{args.depth}' (choose from: {', '.join(DEPTHS)})")

    for name in args.focus:
        if name not in FOCUS_AREAS:
            raise TestgenError(f"unknown focus '{name}' (choose from: {', '.join(FOCUS_AREAS)})")

    env_notes = ""
    if args.notes:
        env_notes = f"## Environment notes\n\n{args.notes.strip()}\n"

    context = {
        "APP_NAME": args.name or meta.get("app_name") or "(not stated — infer from the spec)",
        "BASE_URL": args.base_url or meta.get("base_url") or "(not stated — parameterise it)",
        "AUTH": args.auth or meta.get("auth") or "(not stated — ask before assuming)",
        "ENV_NOTES": env_notes,
        "SPEC_SUMMARY": summary,
    }

    sections = [
        render(read_template("targets", f"{target}.md"), context),
        read_template("_shared", "techniques.md"),
        read_template("_shared", f"depth-{args.depth}.md"),
    ]
    sections += [read_template("focus", f"{name}.md") for name in args.focus]
    sections.append(read_template("frameworks", f"{FRAMEWORKS[framework][0]}.md"))
    sections.append(read_template("_shared", "output-contract.md"))

    return "\n\n---\n\n".join(section.strip() for section in sections) + "\n"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def print_catalogue() -> None:
    for heading, table in (
        ("Targets (--target)", TARGETS),
        ("Focus areas (--focus, repeatable)", FOCUS_AREAS),
    ):
        print(f"\n{heading}\n" + "-" * len(heading))
        for key, description in table.items():
            print(f"  {key:<16} {description}")

    print("\nFrameworks (--framework)\n" + "-" * 23)
    for key, (_, description) in FRAMEWORKS.items():
        print(f"  {key:<16} {description}")

    print("\nDepths (--depth)\n" + "-" * 16)
    for key in DEPTHS:
        print(f"  {key}")
    print()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="testgen",
        description="Build a prompt that makes an LLM write automated tests for any app.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  testgen.py --spec openapi.yaml --framework pytest --out prompt.md\n"
            "  testgen.py --spec https://example.com/openapi.json --depth exhaustive "
            "--focus security --focus contract\n"
            "  testgen.py --target web --describe 'Checkout flow: cart, address, payment' \\\n"
            "             --base-url https://shop.example.com --framework playwright-ts\n"
        ),
    )
    parser.add_argument("--spec", help="path or URL to an OpenAPI, GraphQL SDL, Postman, or text spec")
    parser.add_argument("--describe", help="free-text description, when there is no spec file")
    parser.add_argument("--target", choices=sorted(TARGETS), help="kind of app (inferred from the spec)")
    parser.add_argument("--framework", choices=sorted(FRAMEWORKS), help="test framework to generate for")
    parser.add_argument("--depth", choices=DEPTHS, default="standard", help="coverage depth (default: standard)")
    parser.add_argument(
        "--focus",
        action="append",
        default=[],
        choices=sorted(FOCUS_AREAS),
        help="add a focus area (repeatable)",
    )
    parser.add_argument("--name", help="application name")
    parser.add_argument("--base-url", help="base URL, endpoint, or invocation")
    parser.add_argument("--auth", help="how authentication works")
    parser.add_argument("--notes", help="environment notes: test accounts, rate limits, quirks")
    parser.add_argument("--out", "-o", help="write the prompt here instead of stdout")
    parser.add_argument("--list", action="store_true", help="list targets, frameworks, and focus areas")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.list:
        print_catalogue()
        return 0

    try:
        prompt = build_prompt(args)
    except TestgenError as error:
        print(f"testgen: {error}", file=sys.stderr)
        return 2

    if args.out:
        path = Path(args.out).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(prompt, encoding="utf-8")
        words = len(prompt.split())
        print(f"wrote {path} ({len(prompt):,} chars, ~{words * 4 // 3:,} tokens)", file=sys.stderr)
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
