# AI-Powered Figma-to-Code Generator

Converts a Figma design export (JSON) into frontend code. Includes two
generation modes: a deterministic rule-based generator (no API key
needed) and an LLM-powered generator (Claude) that produces semantic,
responsive markup instead of rigid absolute-positioned divs.

## Why two modes?

The rule-based generator mirrors the design 1:1 — every node becomes an
absolutely-positioned `<div>` at its exact x/y coordinates. It's fast,
free, and deterministic, but the output isn't responsive and doesn't
reflect real-world frontend structure.

The LLM generator is given the same parsed node tree and asked to infer
*semantic* structure — recognizing that a row of elements is a nav bar,
that a tree of boxes is a card component, and so on — then outputs
clean HTML5/React using Flexbox/Grid instead of absolute positioning.
This is the part of the project that's actually AI-powered, and the
part that demonstrates the gap between "convert pixels" and "understand
intent."

## Architecture

```
main.py                          # CLI entry point
generator/
  figma_parser.py                # Parses raw Figma JSON into a DesignNode tree
  rule_based_codegen.py          # Deterministic HTML/CSS generator (no API)
  llm_codegen.py                 # Claude-powered semantic code generator
examples/
  sample_design.json             # Sample Figma export (login card) for testing
tests/
  test_generator.py              # Unit tests for parser + rule-based codegen
```

## Setup

```bash
git clone https://github.com/<your-username>/figma-to-code-generator.git
cd figma-to-code-generator
pip install -r requirements.txt
```

To use the LLM-based generator, set your API key:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

## Usage

**Rule-based mode** (no API key needed, works offline):

```bash
python main.py examples/sample_design.json --format html --mode rule-based --output result
```

This produces `result.html` and `result.css`.

**LLM mode** (semantic, responsive output):

```bash
python main.py examples/sample_design.json --format react-tailwind --mode llm --output result
```

This produces `result.jsx` using Tailwind utility classes and inferred
semantic structure.

### Getting a Figma export

This tool expects a JSON export shaped like the Figma REST API's
`GET /v1/files/:key` response. You can:
- Use the [Figma REST API](https://www.figma.com/developers/api) directly
  with a personal access token, or
- Use the included `examples/sample_design.json` to try the tool without
  any Figma account at all

## How it works

1. **Parse** — `figma_parser.py` walks the raw, deeply-nested Figma JSON
   and extracts only what matters for code generation: layout bounds,
   fill colors (converted from Figma's 0–1 float RGBA to hex), typography,
   corner radius, and text content — discarding plugin metadata and
   Figma-internal fields.
2. **Generate** — the simplified `DesignNode` tree is handed to either
   the rule-based generator (direct 1:1 mapping) or the LLM generator
   (semantic reconstruction), depending on the mode selected.
3. **Output** — valid HTML/CSS or a React component is written to disk.

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

## Possible extensions

- Support for Figma's auto-layout properties (map directly to Flexbox)
- Component deduplication (detect repeated patterns, e.g. button styles,
  and generate reusable components instead of one-off markup)
- Direct integration with the Figma REST API (fetch by file key, no
  manual JSON export needed)
- Vue/Svelte output targets

## License

MIT — see [LICENSE](LICENSE).
