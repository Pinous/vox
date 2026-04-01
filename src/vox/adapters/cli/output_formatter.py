import json
import sys
from dataclasses import asdict
from typing import Any


def format_output(data: Any, fields: str | None, fmt: str | None) -> str:
    output_format = _resolve_format(fmt)
    as_dict = asdict(data) if hasattr(data, "__dataclass_fields__") else data
    filtered = _filter_fields(as_dict, fields)
    if output_format == "json":
        return json.dumps(filtered, indent=2)
    return _format_table(filtered)


def _resolve_format(fmt: str | None) -> str:
    if fmt:
        return fmt
    return "json" if not sys.stdout.isatty() else "table"


def _filter_fields(data: dict, fields: str | None) -> dict:
    if not fields:
        return data
    keys = {f.strip() for f in fields.split(",")}
    return {k: v for k, v in data.items() if k in keys}


def _format_table(data: dict) -> str:
    if not data:
        return ""
    max_key = max(len(str(k)) for k in data)
    lines = [f"  {str(k).ljust(max_key)}  {v}" for k, v in data.items()]
    return "\n".join(lines)
