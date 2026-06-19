"""
test_generator.py
Unit tests for the Figma parser and rule-based code generator.
Run with: pytest tests/
"""

import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generator.figma_parser import parse_figma_export, parse_node, _rgba_to_hex
from generator.rule_based_codegen import generate_html, generate_css

EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_design.json")


def load_sample():
    with open(EXAMPLE_PATH) as f:
        return json.load(f)


def test_rgba_to_hex_conversion():
    assert _rgba_to_hex({"r": 1, "g": 1, "b": 1}) == "#ffffff"
    assert _rgba_to_hex({"r": 0, "g": 0, "b": 0}) == "#000000"


def test_parse_figma_export_returns_root_node():
    data = load_sample()
    root = parse_figma_export(data)
    assert root.name == "Login Card"
    assert root.node_type == "FRAME"
    assert root.width == 360
    assert root.height == 240


def test_parsed_tree_preserves_children():
    data = load_sample()
    root = parse_figma_export(data)
    child_names = [c.name for c in root.children]
    assert "Title" in child_names
    assert "Email Input" in child_names
    assert "Login Button" in child_names


def test_text_node_extracts_characters():
    data = load_sample()
    root = parse_figma_export(data)
    title_node = next(c for c in root.children if c.name == "Title")
    assert title_node.text_content == "Welcome Back"
    assert title_node.font_size == 24


def test_nested_children_parsed_correctly():
    data = load_sample()
    root = parse_figma_export(data)
    button = next(c for c in root.children if c.name == "Login Button")
    assert len(button.children) == 1
    assert button.children[0].text_content == "Log In"


def test_generate_html_contains_expected_classes():
    data = load_sample()
    root = parse_figma_export(data)
    html = generate_html(root)
    assert "login-card" in html
    assert "Welcome Back" in html
    assert "<!DOCTYPE html>" in html


def test_generate_css_contains_positioning_and_colors():
    data = load_sample()
    root = parse_figma_export(data)
    css = generate_css(root)
    assert "position: absolute;" in css
    assert "#ffffff" in css
    assert "border-radius: 12px;" in css
