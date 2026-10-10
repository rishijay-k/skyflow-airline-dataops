"""Offline behavior tests: no credentials, cloud calls or pipeline execution."""
import importlib.util
import json
import subprocess
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from google.cloud import bigquery, pubsub_v1

ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    spec = importlib.util.spec_from_file_location(Path(relative).stem, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def cloud_mocks(monkeypatch):
    bq, subscriber = Mock(), Mock()
    monkeypatch.setattr(bigquery, 'Client', Mock(return_value=bq))
    monkeypatch.setattr(pubsub_v1, 'SubscriberClient', Mock(return_value=subscriber))
    return bq, subscriber


def test_generated_event_contract():
    generator = load('src/generator/generate_flight_events.py')
    events = [generator.create_event() for _ in range(1000)]
    assert len({e['event_id'] for e in events}) == 1000
    for event in events:
        assert event['origin_airport'] != event['destination_airport']
        assert event['event_type'] in generator.EVENT_TYPES
        assert datetime.fromisoformat(event['event_timestamp']).utcoffset().total_seconds() == 0
        assert (5 <= event['delay_minutes'] <= 180) if event['event_type'] == 'DEPARTURE_DELAYED' else event['delay_minutes'] == 0


def test_generator_writes_1000_valid_json_lines(tmp_path, monkeypatch):
    generator = load('src/generator/generate_flight_events.py')
    target = tmp_path / 'data' / 'events.jsonl'
    monkeypatch.setattr(generator, 'OUTPUT_FILE', target)
    generator.main()
    rows = [json.loads(line) for line in target.read_text().splitlines()]
    assert len(rows) == 1000
    assert all(row['event_id'] for row in rows)


HEALTHY = dict(raw_rows=1000, clean_rows=1000, unique_event_ids=1000,
               missing_critical_values=0, same_origin_destination=0, negative_delays=0,
               status_mismatches=0, invalid_event_types=0, airport_metric_rows=10,
               route_metric_rows=90)


@pytest.mark.parametrize('field,value', [(None, None), ('raw_rows', 0),
    ('clean_rows', 999), ('unique_event_ids', 999), ('missing_critical_values', 1),
    ('same_origin_destination', 1), ('negative_delays', 1), ('status_mismatches', 1),
    ('invalid_event_types', 1), ('airport_metric_rows', 9), ('route_metric_rows', 0)])
def test_quality_gate_exit_status(field, value, cloud_mocks):
    module = load('src/quality/run_data_quality.py')
    metrics = HEALTHY.copy()
    if field:
        metrics[field] = value
    cloud_mocks[0].query.return_value.result.return_value = [SimpleNamespace(**metrics)]
    with pytest.raises(SystemExit) as error:
        module.main()
    assert error.value.code == (1 if field else 0)


@pytest.mark.parametrize('failure', [None, 'missing', 'json', 'rejected', 'exception'])
def test_stream_ack_only_after_successful_write(failure, cloud_mocks):
    module = load('src/streaming/stream_to_bigquery.py')
    event = load('src/generator/generate_flight_events.py').create_event()
    bq = cloud_mocks[0]
    bq.insert_rows_json.return_value = []
    if failure == 'missing':
        del event['event_id']
    if failure == 'rejected':
        bq.insert_rows_json.return_value = [{'errors': [{'reason': 'invalid'}]}]
    if failure == 'exception':
        bq.insert_rows_json.side_effect = RuntimeError('simulated outage')
    message = Mock(data=b'not json' if failure == 'json' else json.dumps(event).encode(), message_id='message-123')
    def verify_ack():
        bq.insert_rows_json.assert_called_once()
    message.ack.side_effect = verify_ack
    module.callback(message)
    if failure:
        message.nack.assert_called_once()
        message.ack.assert_not_called()
        assert module.received_count == 0
        if failure in ('missing', 'json'):
            bq.insert_rows_json.assert_not_called()
    else:
        message.ack.assert_called_once()
        message.nack.assert_not_called()
        assert module.received_count == 1
        args, kwargs = bq.insert_rows_json.call_args
        assert args[0] == 'skyflow-511113.skyflow_raw.flight_events_streaming'
        assert args[1][0]['pubsub_message_id'] == 'message-123'
        assert kwargs['row_ids'] == [event['event_id']]


@pytest.mark.parametrize('failed', [False, True])
def test_batch_observability_logs_outcome(failed, monkeypatch, cloud_mocks):
    module = load('src/monitoring/run_observed_batch.py')
    runner = Mock(side_effect=subprocess.CalledProcessError(1, 'batch') if failed else None)
    monkeypatch.setattr(module.subprocess, 'run', runner)
    monkeypatch.setattr(module, 'get_record_count', Mock(return_value=1000))
    bq = cloud_mocks[0]
    bq.insert_rows_json.return_value = []
    if failed:
        with pytest.raises(SystemExit) as error:
            module.main()
        assert error.value.code == 1
    else:
        module.main()
    row = bq.insert_rows_json.call_args.args[1][0]
    assert row['status'] == ('FAILED' if failed else 'SUCCESS')
    assert row['records_processed'] == (0 if failed else 1000)
    assert bool(row['error_message']) == failed
    assert row['duration_seconds'] >= 0


@pytest.mark.parametrize('outcome,count,expected', [
    ('complete', 20, 0), ('timeout', 0, 1), ('timeout', 19, 1),
    ('timeout', 20, 1), ('interrupt', 0, 130), ('complete', 19, 1),
])
def test_stream_process_exit_and_cleanup(outcome, count, expected, monkeypatch, cloud_mocks, capsys):
    # Exercise the script entry point as well as main, with no real waiting or cloud calls.
    import runpy
    import threading
    subscriber = cloud_mocks[1]
    event = Mock()
    def wait(timeout):
        # The callback's module globals are the running script's globals.
        callback = subscriber.subscribe.call_args.kwargs['callback']
        callback.__globals__['received_count'] = count
        if outcome == 'interrupt':
            raise KeyboardInterrupt
        return outcome == 'complete'
    event.wait.side_effect = wait
    monkeypatch.setattr(threading, 'Event', Mock(return_value=event))
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(ROOT / 'src/streaming/stream_to_bigquery.py'), run_name='__main__')
    assert error.value.code == expected
    subscriber.subscribe.return_value.cancel.assert_called_once()
    subscriber.subscribe.return_value.result.assert_called_once()
    subscriber.close.assert_called_once()
    output = capsys.readouterr().out
    assert ('BIGQUERY: SUCCESS' in output) == (expected == 0)
