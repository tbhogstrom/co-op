import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

from pipeline import build_parser, get_execution_order


def test_parser_accepts_all_flag():
    parser = build_parser()
    args = parser.parse_args(["--all"])
    assert args.all is True


def test_parser_accepts_source_flag():
    parser = build_parser()
    args = parser.parse_args(["--source", "redfin"])
    assert args.source == "redfin"


def test_parser_accepts_validate_flag():
    parser = build_parser()
    args = parser.parse_args(["--validate"])
    assert args.validate is True


def test_parser_accepts_geocode_flag():
    parser = build_parser()
    args = parser.parse_args(["--geocode"])
    assert args.geocode is True


def test_execution_order():
    order = get_execution_order()
    assert order.index("assessor") < order.index("redfin")
    assert order.index("redfin") < order.index("portlandmaps")
    assert order.index("portlandmaps") < order.index("distressed")
