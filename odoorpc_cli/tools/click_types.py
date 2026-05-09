import json

import click


class JSON(click.ParamType):
    """Click parameter type that parses JSON strings into Python objects.

    Args:
        expected: Optional expected Python type as a string: "list" or "dict".
            If provided, the value is validated to be that type.
    """

    name = "json"

    def __init__(self, expected: str | None = None):
        if expected not in (None, "list", "dict"):
            raise ValueError("expected must be None, 'list' or 'dict'")
        self.expected = expected

    def convert(self, value, param, ctx):
        # If the value was already parsed (click may pass defaults), accept it
        if not isinstance(value, str):
            obj = value
        else:
            try:
                obj = json.loads(value)
            except Exception as exc:  # pragma: no cover - error path
                self.fail(f"Failed to parse JSON: {exc}", param, ctx)

        if self.expected == "list" and not isinstance(obj, list):
            self.fail("Value must be a JSON list", param, ctx)
        if self.expected == "dict" and not isinstance(obj, dict):
            self.fail("Value must be a JSON object", param, ctx)

        return obj

    def __repr__(self):
        return f"JSON(expected={self.expected!r})"
