"""
figma_parser.py
Parses a Figma file export (as returned by the Figma REST API's
`GET /v1/files/:key` endpoint, or a locally saved JSON export) into a
simplified, code-generation-friendly node tree.

Figma's raw export is deeply nested and includes many fields irrelevant
to code generation (plugin data, component metadata, etc). This module
extracts only what's needed: layout, dimensions, colors, typography,
and text content.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class DesignNode:
    """A simplified representation of a single Figma node."""
    name: str
    node_type: str  # FRAME, TEXT, RECTANGLE, GROUP, COMPONENT, etc.
    x: float
    y: float
    width: float
    height: float
    fill_color: Optional[str] = None
    text_content: Optional[str] = None
    font_size: Optional[float] = None
    font_weight: Optional[int] = None
    corner_radius: Optional[float] = None
    children: List["DesignNode"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.node_type,
            "bounds": {"x": self.x, "y": self.y, "width": self.width, "height": self.height},
            "fill": self.fill_color,
            "text": self.text_content,
            "font_size": self.font_size,
            "font_weight": self.font_weight,
            "corner_radius": self.corner_radius,
            "children": [c.to_dict() for c in self.children],
        }


def _rgba_to_hex(color: Dict[str, float]) -> str:
    """Converts Figma's 0-1 float RGBA format to a #RRGGBB hex string."""
    r = round(color.get("r", 0) * 255)
    g = round(color.get("g", 0) * 255)
    b = round(color.get("b", 0) * 255)
    return f"#{r:02x}{g:02x}{b:02x}"


def _extract_fill(node: Dict[str, Any]) -> Optional[str]:
    fills = node.get("fills", [])
    for fill in fills:
        if fill.get("type") == "SOLID" and fill.get("visible", True):
            return _rgba_to_hex(fill["color"])
    return None


def parse_node(raw: Dict[str, Any]) -> DesignNode:
    """Recursively converts a raw Figma JSON node into a DesignNode."""
    bbox = raw.get("absoluteBoundingBox", {"x": 0, "y": 0, "width": 0, "height": 0})

    style = raw.get("style", {})
    node = DesignNode(
        name=raw.get("name", "Unnamed"),
        node_type=raw.get("type", "UNKNOWN"),
        x=bbox.get("x", 0),
        y=bbox.get("y", 0),
        width=bbox.get("width", 0),
        height=bbox.get("height", 0),
        fill_color=_extract_fill(raw),
        text_content=raw.get("characters") if raw.get("type") == "TEXT" else None,
        font_size=style.get("fontSize"),
        font_weight=style.get("fontWeight"),
        corner_radius=raw.get("cornerRadius"),
    )

    for child in raw.get("children", []):
        node.children.append(parse_node(child))

    return node


def parse_figma_export(figma_json: Dict[str, Any]) -> DesignNode:
    """
    Entry point: takes a full Figma file export dict and returns the
    root DesignNode of the first page/canvas.
    """
    document = figma_json.get("document", figma_json)
    pages = document.get("children", [document])
    root_page = pages[0] if pages else document
    return parse_node(root_page)
