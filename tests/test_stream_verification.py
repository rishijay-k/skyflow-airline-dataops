"""Regressions for false-positive streaming acceptance."""
import importlib.util
from pathlib import Path

import pytest

path = Path(__file__).resolve().parents[1] / "scripts/verify_streaming_pipeline.py"
spec = importlib.util.spec_from_file_location("verify_stream", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize("expected,rows,passed", [
    ({"a": "m1"}, [{"event_id": "a", "pubsub_message_id": "m1"}], True),
    ({"a": "m1"}, [{"event_id": "other", "pubsub_message_id": "m2"}], False),
    ({"a": "m1", "b": "m2"}, [{"event_id": "a", "pubsub_message_id": "m1"}], False),
    ({"a": "m1"}, [{"event_id": "a", "pubsub_message_id": None}], False),
    ({"a": "m1"}, [{"event_id": "a", "pubsub_message_id": "wrong"}], False),
    ({"a": "m1"}, [{"event_id": "a", "pubsub_message_id": "m1"}] * 2, False),
    ({}, [], False),
])
def test_exact_event_acceptance(expected, rows, passed):
    assert module.inspect_rows(expected, rows)["passed"] is passed
