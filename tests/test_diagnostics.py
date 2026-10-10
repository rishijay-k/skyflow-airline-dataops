import importlib.util
from pathlib import Path
from unittest.mock import Mock

import pytest

spec = importlib.util.spec_from_file_location('diagnose', Path(__file__).resolve().parents[1] / 'src/agent/diagnose.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def snapshot():
    return {'errors': {}, 'streaming': [{'total_streamed_events': 20, 'unique_events': 20,
            'events_last_5_minutes': 20}], 'batch': [{'pipeline_name': 'batch', 'status': 'SUCCESS'}]}


def test_healthy_metrics_are_not_claimed_as_end_to_end_verification():
    findings = module.diagnose(snapshot())
    assert findings[0]['code'] == 'NO_FLAGS'
    assert 'does not verify' in findings[0]['action']


@pytest.mark.parametrize('expected,severity', [(False, 'INFO'), (True, 'WARN')])
def test_idle_is_only_warning_when_streaming_expected(expected, severity):
    data = snapshot()
    data['streaming'][0]['events_last_5_minutes'] = 0
    assert module.diagnose(data, expected)[0]['severity'] == severity


def test_duplicates_flag_evidence_without_claiming_root_cause():
    data = snapshot()
    data['streaming'][0]['unique_events'] = 19
    assert module.diagnose(data)[0]['code'] == 'DUPLICATE_OR_NULL_IDS'


def test_failed_batch_is_error():
    data = snapshot()
    data['batch'][0]['status'] = 'FAILED'
    assert module.diagnose(data)[0]['severity'] == 'ERROR'


def test_empty_batch_is_unknown():
    data = snapshot()
    data['batch'] = []
    assert module.diagnose(data)[0]['severity'] == 'UNKNOWN'


def test_partial_collection_keeps_available_data_and_redacts_error():
    client = Mock()
    job = Mock()
    job.result.return_value = [{'status': 'SUCCESS'}]
    client.query.side_effect = [RuntimeError('secret error text'), job]
    data = module.collect(client)
    assert data['streaming'] is None
    assert data['batch'] == [{'status': 'SUCCESS'}]
    assert data['errors'] == {'streaming': 'RuntimeError'}
    for call in client.query.call_args_list:
        assert call.kwargs['location'] == 'asia-south1'
        assert call.kwargs['job_config'].maximum_bytes_billed == 104857600
    assert module.diagnose(data)[0]['severity'] == 'UNKNOWN'


def test_demo_requires_no_cloud_credentials(capsys):
    assert module.main(['--demo']) == 0
    assert 'not_connected' in capsys.readouterr().out


def report():
    return {'mode': 'demo', 'snapshot': {'collected_at': 'test'}, 'findings': []}


def response(data=None):
    import json
    return Mock(status_code=200, json=Mock(return_value={'status': 'completed', 'output': [
        {'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(data or {
            'summary': 'Synthetic demo', 'hypotheses': [], 'suggested_checks': [], 'limitations': ['No live evidence']})}]}]}))


def test_openai_request_is_bounded_without_tools():
    post = Mock(return_value=response())
    result = module.explain(report(), 'fake-test-key', 'test-model', post)
    assert result['summary'] == 'Synthetic demo'
    request = post.call_args.kwargs
    assert request['json']['store'] is False
    assert 'tools' not in request['json']
    assert request['json']['max_output_tokens'] == 1000
    assert request['allow_redirects'] is False
    assert 'fake-test-key' not in request['json']['input']


@pytest.mark.parametrize('code', [401, 429, 500])
def test_openai_errors_do_not_expose_response_body(code):
    post = Mock(return_value=Mock(status_code=code))
    with pytest.raises(RuntimeError, match=f'OpenAI HTTP {code}'):
        module.explain(report(), 'fake-test-key', 'test-model', post)


def test_incomplete_ai_response_is_rejected():
    post = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'status': 'incomplete'})))
    with pytest.raises(RuntimeError, match='incomplete'):
        module.explain(report(), 'fake-test-key', 'test-model', post)


def test_invalid_ai_schema_is_rejected():
    post = Mock(return_value=response({'unexpected': 'value'}))
    with pytest.raises(ValueError, match='structure'):
        module.explain(report(), 'fake-test-key', 'test-model', post)


def test_ai_requires_key_before_any_query(monkeypatch):
    from dotenv import load_dotenv
    import dotenv
    monkeypatch.setattr(dotenv, 'load_dotenv', Mock())
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    assert module.main(['--ai']) == 2
