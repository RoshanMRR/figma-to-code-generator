"""
main.py
CLI entry point for the Figma-to-Code generator.

Usage:
    python main.py design.json --format html --mode rule-based
    python main.py design.json --format react-tailwind --mode llm
"""

import argparse
import json
import sys

from generator.figma_parser import parse_figma_export
from generator.rule_based_codegen import generate_html, generate_css
from generator.llm_codegen import LLMCodeGenerator


def main():
    parser = argparse.ArgumentParser(description="Figma-to-Code Generator")
    parser.add_argument("input_file", help="Path to a Figma export JSON file")
    parser.add_argument(
        "--format", choices=["html", "react", "react-tailwind"], default="html"
    )
    parser.add_argument(
        "--mode", choices=["rule-based", "llm"], default="rule-based",
        help="rule-based: deterministic, no API needed. llm: semantic, needs ANTHROPIC_API_KEY",
    )
    parser.add_argument("--output", default="output", help="Output file prefix")
    args = parser.parse_args()

    with open(args.input_file, "r") as f:
        figma_json = json.load(f)

    root = parse_figma_export(figma_json)
    print(f"Parsed design root: '{root.name}' ({len(root.children)} top-level children)")

    if args.mode == "rule-based":
        html = generate_html(root)
        css = generate_css(root)
        with open(f"{args.output}.html", "w") as f:
            f.write(html)
        with open(f"{args.output}.css", "w") as f:
            f.write(css)
        print(f"Wrote {args.output}.html and {args.output}.css")
    else:
        generator = LLMCodeGenerator()
        code = generator.generate(root, output_format=args.format)
        if code is None:
            sys.exit(1)
        ext = "jsx" if args.format != "html" else "html"
        with open(f"{args.output}.{ext}", "w") as f:
            f.write(code)
        print(f"Wrote {args.output}.{ext}")


if __name__ == "__main__":
    main()
