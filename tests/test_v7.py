"""V7 integration and failure injection with local clients, never providers."""
import asyncio
import hashlib
import json
from dataclasses import replace

import pytest
from runtime_contracts.llm import ConversationContext, ResponseFunctionCall, ResponseTurn, AssistantResponse

from research_agent.advances import record_advance, recover, RecoveryRequired, atomic_bytes
from research_agent.continuity import active_foundations, OperationalObserver, AGENDA_TEMPLATE
from research_agent.external_review import knowledge, packet, parse_report, feedback
from research_agent.recording import encoded
from research_agent.workspace import Workspace
from test_continuous import make, execute, text, call, events
from support import review_turn


def create(path, content):
    return dict(path=path, action='create', content=content, expected_sha256=None, operations=None)


def edit(space, path, old, new):
    return dict(path=path, action='edit', content=None, expected_sha256=space.read_version(path)[1],
                operations=[dict(kind='replace', target=old, content=new)])


def test_batch_versions_and_preflight_rejection(tmp_path):
    space = Workspace(tmp_path / 'state')
    space.write_file('agenda.md', 'pendiente')
    changes = [edit(space, 'agenda.md', 'pendiente', 'resuelto'), create('comparacion.md', 'fundamento')]
    bad = [changes[0], create('materiales/prohibido.md', 'x')]
    with pytest.raises(ValueError):
        record_advance(space, tmp_path / 'runs', bad, 'avance', [])
    assert space.read_version('agenda.md')[0] == b'pendiente'
    result = record_advance(space, tmp_path / 'runs', changes, 'avance', ['fuente'])
    assert len(result['files']) == 2
    assert result['files'][0]['previous_sha256'] == hashlib.sha256(b'pendiente').hexdigest()
    assert space.read_version('agenda.md')[0] == b'resuelto'
    assert json.loads(next((tmp_path / 'runs/transacciones').glob('*.json')).read_bytes())['status'] == 'committed'


def test_batch_rejects_case_duplicates_and_stale_versions(tmp_path):
    space = Workspace(tmp_path / 'state')
    with pytest.raises(ValueError, match='duplicate_path'):
        record_advance(space, tmp_path / 'runs', [create('uno.md', 'a'), create('UNO.md', 'b')], 'x', [])
    space.write_file('uno.md', 'a')
    change = edit(space, 'uno.md', 'a', 'b')
    space.write_file('uno.md', 'c')
    with pytest.raises(ValueError, match='version_conflict'):
        record_advance(space, tmp_path / 'runs', [create('dos.md', 'x'), change], 'x', [])
    assert not space.path('dos.md').exists()


def test_publication_failure_restores_and_recovery_preserves_external_edits(tmp_path, monkeypatch):
    space = Workspace(tmp_path / 'state')
    space.write_file('uno.md', 'a')
    original = space.publish
    def fail(path, *args, **kwargs):
        if path == 'dos.md':
            raise OSError('injected')
        return original(path, *args, **kwargs)
    monkeypatch.setattr(space, 'publish', fail)
    with pytest.raises(OSError):
        record_advance(space, tmp_path / 'runs', [edit(space, 'uno.md', 'a', 'b'), create('dos.md', 'x')], 'x', [])
    assert space.read_version('uno.md')[0] == b'a'
    journal = tmp_path / 'runs/transacciones/crash.json'
    data = dict(workspace=str(space.root.resolve()), status='pending',
                changes=[dict(path='uno.md', before='a', after='b')])
    atomic_bytes(journal, encoded(data))
    space.path('uno.md').write_bytes(b'b')
    recover(space, tmp_path / 'runs')
    assert space.read_version('uno.md')[0] == b'a'
    atomic_bytes(journal, encoded(data))
    space.path('uno.md').write_bytes(b'external')
    with pytest.raises(RecoveryRequired):
        recover(space, tmp_path / 'runs')
    assert space.read_version('uno.md')[0] == b'external'


def test_rollback_failure_is_fatal_to_dispatcher(tmp_path, monkeypatch):
    agent, _ = make(tmp_path, [])
    import research_agent.advances as advances
    def fail(*args, **kwargs):
        raise OSError('injected')
    monkeypatch.setattr(agent.workspace, 'publish', fail)
    monkeypatch.setattr(advances, 'restore', fail)
    agent.recorder.start('test', {'run_id': 'test'})
    with pytest.raises(RecoveryRequired):
        asyncio.run(agent.tools.execute(ResponseFunctionCall('x', 'record_research_advance', {
            'changes': [create('new.md', 'x')], 'reason': 'x', 'source_refs': []})))


def test_batch_dispatch_receipts_and_applied_capture_failure(tmp_path, monkeypatch):
    agent, _ = make(tmp_path, [])
    agent.recorder.start('test', {'run_id': 'test'})
    def fail(*args):
        raise OSError('capture')
    monkeypatch.setattr(agent.recorder, 'artifact', fail)
    result = asyncio.run(agent.tools.execute(ResponseFunctionCall('x', 'record_research_advance', {
        'changes': [create('one.md', 'x'), create('two.md', 'y')], 'reason': 'x', 'source_refs': []})))
    assert result.payload['applied'] and not result.payload['ok']
    assert len(result.payload['mutation']['files']) == 2
    assert agent.tools.summary().files_written == ('one.md', 'two.md')
    assert len(events(agent, 'lab.file.written')) == 2


def test_active_foundations_ids_missing_and_utf8_limits(tmp_path):
    space = Workspace(tmp_path / 'state')
    space.write_file('empresas/X/modelo.md', '### H1\n' + '€' * 9000)
    agenda = '# Agenda\n## Investigación activa\nempresas/X/modelo.md#H1 y ausente.md\n## Otra\nignorada.md'
    refs = active_foundations(space, agenda)
    assert refs[0]['partial'] and refs[0]['sha256']
    assert sum(len(r.get('text', '').encode('utf-8')) for r in refs) <= 8192
    assert refs[1]['error'] == 'FileNotFoundError'
    assert active_foundations(space, 'agenda heredada') == []


def test_observer_deduplicates_and_resets_only_writes(tmp_path):
    space = Workspace(tmp_path / 'state')
    space.write_file('x.md', 'a')
    obs = OperationalObserver()
    for _ in range(10):
        obs.research_call()
    payload = {'ok': True, 'material_ref': 'materiales/one.json'}
    for _ in range(3):
        obs.observe('fetch', {'x': 1}, payload, True, space)
    obs.observe('read', {}, {'ok': True, 'value': {'path': 'x.md', 'sha256': 'v'}}, False, space)
    assert {n['kind'] for n in obs.drain()} == {'repeated_query', 'persistence_interval'}
    assert not obs.drain()
    for _ in range(2):
        obs.observe('edit', {'path': 'x.md'}, {'ok': False, 'message': 'version_conflict'}, False, space)
    assert obs.drain()[0]['sha256'] == space.read_version('x.md')[1]
    obs.observe('write', {}, {'ok': True}, False, space, mutation=True)
    assert obs.since_write == 0 and not obs.persistence_notified


def test_review_packet_and_feedback_bounded_with_omissions(tmp_path):
    space = Workspace(tmp_path / 'state')
    space.write_file('agenda.md', AGENDA_TEMPLATE)
    for i in range(20):
        space.write_file(f'f{i}.md', '€' * 20000)
    snap = knowledge(space)
    value = packet(space, 'mandato', {}, snap, {}, [])
    assert len(encoded(value)) <= 65536 and value['omitted']['documents'] > 0
    assert value['documents'][0]['path'] == 'agenda.md'
    report = {'progress': 'x' * 10000, 'findings': [], 'blockers': ['x' * 9000], 'recommendations': []}
    assert len(encoded(feedback(parse_report(json.dumps(report))))) <= 8192


def test_external_review_separate_midpoint_and_final_and_totals(tmp_path):
    agent, request = make(tmp_path, [text()] * 4)
    request = replace(request, continuous=replace(request.continuous, max_llm_calls=4))
    result = execute(agent, request)
    assert result.llm_calls == 6 and result.llm_calls_by_phase['external_review'] == 2
    assert result.llm_calls == sum(result.llm_calls_by_phase.values())
    assert result.stop_reason == 'call_limit' and result.status == 'interrupted'
    assert len(agent.client.review_requests) == 2
    for entry in agent.client.review_requests:
        assert not entry['tools'] and not entry['allow_tools']
        assert len(entry['input_items']) == 1
        assert 'review_packet' in entry['input_items'][0].payload
    assert (agent.recorder.current / 'revision-externa/final.json').exists()
    assert (agent.recorder.current / 'respuesta.md').read_text(encoding='utf-8') == 'avance'


@pytest.mark.parametrize('response', [text('invalid'), call('write_file', path='bad.md', content='bad'), TimeoutError()])
def test_failed_reviewer_does_not_execute_or_stop_research(tmp_path, response):
    agent, request = make(tmp_path, [])
    class Client:
        async def respond(self, **kwargs):
            if 'review_packet' in getattr(kwargs['input_items'][0], 'payload', {}):
                if isinstance(response, Exception):
                    raise response
                return response
            return text('research')
    agent.client = Client()
    result = execute(agent, request)
    assert result.stop_reason == 'call_limit' and result.llm_calls_by_phase['research'] == 3
    assert len(events(agent, 'lab.external_review.failed')) == 2
    assert not agent.workspace.path('bad.md').exists()


def test_cancellation_in_reviewer_has_no_final_review(tmp_path):
    agent, request = make(tmp_path, [])
    class Client:
        async def respond(self, **kwargs):
            if 'review_packet' in getattr(kwargs['input_items'][0], 'payload', {}):
                raise asyncio.CancelledError()
            return text()
    agent.client = Client()
    with pytest.raises(asyncio.CancelledError):
        execute(agent, request)
    assert not (agent.recorder.current / 'revision-externa/final-input.json').exists()
    assert json.loads((agent.recorder.current / 'resultado.json').read_bytes())['status'] == 'cancelled'


def test_advance_renew_review_correct_and_continue_managed_session(tmp_path):
    agent, request = make(tmp_path, [])
    agent.recorder.experiment = tmp_path
    instruction = tmp_path / 'deliberacion.md'
    instruction.write_text('Instrucción local simulada; no proveedor.', encoding='utf-8')
    request = replace(request, instructions=(instruction,), continuous=replace(request.continuous,
        max_llm_calls=7, max_context_bytes=120000, consolidation_threshold_bytes=50000))
    class Client:
        step = 0
        reviewed = False
        corrected = False
        historical = False
        async def respond(self, **kwargs):
            contexts = [x.payload for x in kwargs['input_items'] if isinstance(x, ConversationContext)]
            if any('review_packet' in x for x in contexts):
                self.reviewed = True
                value = json.dumps({'progress': 'Comparación parcial', 'blockers': [],
                    'findings': [{'status': 'comprobado', 'detail': 'Pendiente obsoleto en H1',
                                  'references': ['empresas/X/modelo.md#H1']}], 'recommendations': ['Corregir pendiente']})
                return text(value)
            if any(x.get('external_review_feedback', {}).get('historical_versions') for x in contexts):
                self.historical = True
            phase = next(x['execution_capabilities']['phase'] for x in reversed(contexts)
                         if 'execution_capabilities' in x)
            if phase != 'research':
                return text('Conservado')
            self.step += 1
            if self.step == 1:
                agenda = '# Agenda\n## Investigación activa\nResultado: comparar. Criterio: evidencia suficiente o bloqueo fundado.\nempresas/X/modelo.md#H1\n'
                return call('record_research_advance', changes=[
                    edit(agent.workspace, 'agenda.md', 'Investigar la pregunta pendiente.', agenda),
                    create('empresas/X/modelo.md', '### H1\nPendiente antiguo\n')], reason='Avance', source_refs=[])
            if self.step == 2:
                return text('Material para renovar. ' * 3000)
            if self.reviewed and not self.corrected:
                assert any('external_review_feedback' in x for x in contexts)
                self.corrected = True
                return call('record_research_advance', changes=[
                    edit(agent.workspace, 'empresas/X/modelo.md', 'Pendiente antiguo', 'Resuelto; insuficiencia fundada'),
                    edit(agent.workspace, 'agenda.md', 'Resultado: comparar.', 'Resultado reformulado: delimitar bloqueo; motivo: corpus insuficiente.')],
                    reason='Aceptar hallazgo y reformular con motivo', source_refs=[])
            return text('Continuar fundamento')
    client = Client()
    agent.client = client
    result = execute(agent, request)
    assert result.stop_reason == 'call_limit' and client.corrected
    assert all(event['run_id'] == result.run_id for event in agent.recorder.events)
    assert events(agent, 'lab.context.renewed')
    assert b'Resuelto' in agent.workspace.read_version('empresas/X/modelo.md')[0]
    resumed = execute(agent, replace(request, continuous=replace(request.continuous, max_llm_calls=1)))
    assert resumed.stop_reason == 'call_limit' and client.historical
    assert len(agent.tools.summary().files_written) == 0


def test_expired_deadline_has_no_external_review(tmp_path, monkeypatch):
    import research_agent.continuous as continuous
    now = [0.0]
    monkeypatch.setattr(continuous, 'monotonic', lambda: now[0])
    agent, request = make(tmp_path, [])
    class Client:
        async def respond(self, **kwargs):
            now[0] = 10.0
            return text()
    agent.client = Client()
    request = replace(request, continuous=replace(request.continuous, timeout_seconds=1))
    result = execute(agent, request)
    assert result.stop_reason == 'time_limit'
    assert result.llm_calls_by_phase['external_review'] == 0
