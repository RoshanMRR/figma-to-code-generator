"""
llm_codegen.py
Uses an LLM (Anthropic Claude) to convert the parsed design node tree
into clean, semantic, responsive frontend code — going beyond the
rule-based generator's absolute positioning to produce production-
quality HTML/CSS or React + Tailwind output.

This is the key differentiator from the rule-based approach: the LLM
infers semantic structure (e.g. recognizing a row of icons + text as a
nav bar) rather than blindly mirroring x/y coordinates.
"""

import os
import json
from typing import Optional

from .figma_parser import DesignNode

SYSTEM_PROMPT = """You are a frontend engineer converting a parsed Figma \
design (given as a JSON node tree with positions, sizes, colors, and \
text) into clean, production-quality frontend code.

Rules:
- Prefer semantic HTML5 elements (nav, header, main, section, button) \
over generic divs where the structure implies them.
- Use Flexbox/Grid for layout instead of absolute positioning wherever \
the node arrangement suggests a row/column pattern.
- Use the exact colors, font sizes, and text content provided.
- Output ONLY valid code for the requested format, no explanation.
"""


class LLMCodeGenerator:
    """Generates semantic frontend code from a DesignNode tree via Claude."""

    def __init__(self, model: str = "claude-sonnet-4-6", max_tokens: int = 4000):
        self.model = model
        self.max_tokens = max_tokens
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self._client = None

        if self.api_key:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                print("anthropic package not installed; run `pip install anthropic`.")

    def generate(self, root: DesignNode, output_format: str = "html") -> Optional[str]:
        """
        Generates code in the requested format ('html', 'react', or
        'react-tailwind'). Returns None if no API client is configured.
        """
        if not self._client:
            print(
                "No ANTHROPIC_API_KEY set — LLM code generation unavailable. "
                "Use rule_based_codegen.py for an offline fallback."
            )
            return None

        format_instructions = {
            "html": "Output a single HTML file with an embedded <style> block.",
            "react": "Output a single functional React component (JSX) with inline styles.",
            "react-tailwind": "Output a single functional React component using Tailwind utility classes.",
        }

        user_prompt = (
            f"{format_instructions.get(output_format, format_instructions['html'])}\n\n"
            f"Design node tree:\n{json.dumps(root.to_dict(), indent=2)}"
        )

        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text
