"""
rule_based_codegen.py
Deterministic HTML/CSS generator that converts a DesignNode tree
directly into markup using absolute positioning. This works without
any AI/API calls and serves as a reliable fallback or baseline to
compare against the LLM-based generator.
"""

from .figma_parser import DesignNode


def _node_to_html(node: DesignNode, indent: int = 0) -> str:
    pad = "  " * indent
    tag = "p" if node.node_type == "TEXT" else "div"
    class_name = node.name.lower().replace(" ", "-")

    inner = node.text_content or ""
    children_html = "\n".join(_node_to_html(c, indent + 1) for c in node.children)

    if children_html:
        inner = f"\n{children_html}\n{pad}"

    return f'{pad}<{tag} class="{class_name}">{inner}</{tag}>'


def _node_to_css(node: DesignNode, rules: list) -> None:
    class_name = node.name.lower().replace(" ", "-")
    declarations = [
        "position: absolute;",
        f"left: {node.x}px;",
        f"top: {node.y}px;",
        f"width: {node.width}px;",
        f"height: {node.height}px;",
    ]
    if node.fill_color:
        prop = "color" if node.node_type == "TEXT" else "background-color"
        declarations.append(f"{prop}: {node.fill_color};")
    if node.font_size:
        declarations.append(f"font-size: {node.font_size}px;")
    if node.font_weight:
        declarations.append(f"font-weight: {node.font_weight};")
    if node.corner_radius:
        declarations.append(f"border-radius: {node.corner_radius}px;")

    rule = f".{class_name} {{\n  " + "\n  ".join(declarations) + "\n}"
    rules.append(rule)

    for child in node.children:
        _node_to_css(child, rules)


def generate_html(root: DesignNode) -> str:
    """Generates a complete HTML document with inline-linked CSS."""
    body = _node_to_html(root)
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        '  <meta charset="UTF-8">\n'
        f"  <title>{root.name}</title>\n"
        '  <link rel="stylesheet" href="styles.css">\n'
        "</head>\n<body>\n"
        f"{body}\n"
        "</body>\n</html>"
    )


def generate_css(root: DesignNode) -> str:
    """Generates a CSS stylesheet matching the generated HTML's classes."""
    rules: list = []
    _node_to_css(root, rules)
    return "\n\n".join(rules)
