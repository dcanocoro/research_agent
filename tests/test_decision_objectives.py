"""Decision-oriented direction, bounded recovery and atomic agenda validation."""
from dataclasses import replace
import json
import pytest

from research_agent.advances import record_advance
from research_agent.continuity import assessment_context
from research_agent.objectives import Objective, parse_evaluation, encode
from research_agent.objective_review import feedback
from research_agent.contracts import ContinuousConfig
from test_v8 import setup, report, objective, Client, saved
from test_continuous import execute, call, text, events


def decision_report():
    value = report()
    value['decision_review'] = {'decision_useful': False, 'blockers': [
        {'id': 'B1', 'criterion_id': 'revenue', 'kind': 'interpretacion',
         'missing': 'Conectar ingresos con escenario', 'decision_impact': 'Impide juzgar atractivo',
         'references': ['evaluacion.md#J1']}], 'resolved_blockers': [],
         'adaptation_assessment': 'Sin revisión anterior; hay evidencia para desarrollar escenarios.'}
    return value


def test_agenda_limit_is_utf8_and_batch_rejection_is_atomic(tmp_path):
    agent, _ = setup(tmp_path)
    space = agent.workspace
    space.write_file('agenda.md', 'é' * 4096)
    before = space.read_version('agenda.md')[1]
    with pytest.raises(ValueError, match='agenda_limit'):
        space.write_file('agenda.md', 'é' * 4097)
    with pytest.raises(ValueError, match='agenda_limit'):
        record_advance(space, tmp_path / 'journals', [
            dict(path='other.md', action='create', content='Must not appear', expected_sha256=None, operations=None),
            dict(path='agenda.md', action='edit', content=None, expected_sha256=before,
                 operations=[dict(kind='replace', target='é' * 4096, content='é' * 4097)])], 'batch', [])
    assert space.read_version('agenda.md')[1] == before and not space.path('other.md').exists()


@pytest.mark.parametrize('path', ['../outside.md', '/absolute.md', 'C:/secret.md', 'materiales/source.md', 'x.txt'])
def test_assessment_path_rejects_escape_and_original_materials(path):
    with pytest.raises(ValueError):
        objective(assessment_path=path)


def test_new_objective_hash_and_old_definition_roundtrip():
    old = objective()
    assert 'assessment_path' not in old.definition()
    value = objective(assessment_path='evaluacion.md')
    assert Objective.from_dict(value.definition()) == value and value.sha256 != old.sha256


def test_decision_review_contract_and_bounded_feedback():
    value = decision_report()
    assert parse_evaluation(json.dumps(value), objective()) == value
    bounded = feedback(value, {'metrics': {}, 'interventions': [], 'reopened': []}, 'ref')
    assert bounded['decision_review']['blockers'][0]['kind'] == 'interpretacion'
    value['decision_review']['decision_useful'] = True
    with pytest.raises(ValueError):
        parse_evaluation(json.dumps(value), objective())
    value['decision_review']['decision_useful'] = False
    value['decision_review']['blockers'][0]['missing'] *= 1000
    bounded = feedback(value, {'metrics': {}, 'interventions': [], 'reopened': []}, 'ref')
    assert len(encode(bounded)) <= 8192 and bounded['partial']


def test_assessment_refresh_after_write_and_recovery_after_renewal(tmp_path):
    agent, request = setup(tmp_path, config=ContinuousConfig(max_llm_calls=6,
        max_context_bytes=524288, consolidation_threshold_bytes=100000), reports=[decision_report()])
    request = replace(request, objective=objective(assessment_path='evaluacion.md'))
    class Workflow(Client):
        research = 0
        recovered = False
        async def respond(self, **kwargs):
            if 'objective_evaluation_packet' in getattr(kwargs['input_items'][0], 'payload', {}):
                return await super().respond(**kwargs)
            contexts = [getattr(x, 'payload', {}) or {} for x in kwargs['input_items']]
            if not any(t.name == 'calculate' for t in kwargs['tools']):
                return text('Conservado')
            self.research += 1
            assert 'resolver un impedimento material' in kwargs['system']
            if self.research == 1:
                return call('write_file', path='evaluacion.md', content='Juicio provisional #J1. Escenario pendiente.')
            assert any('Juicio provisional' in c.get('active_assessment', {}).get('text', '') for c in contexts)
            if self.research == 2:
                return text('material ' * 18000)
            self.recovered = True
            return text('Continuar con el escenario')
    agent.client = Workflow([decision_report()])
    result = execute(agent, request)
    assert result.stop_reason == 'call_limit' and agent.client.recovered
    assert events(agent, 'lab.context.renewed')
    assert saved(agent)[0]['report']['decision_review']['blockers'][0]['id'] == 'B1'
    from research_campaigns.evidence import inspect_run
    assert inspect_run(tmp_path, agent.recorder.current)['objective_summary']['decision_useful'] is False
    agent.workspace.write_file('evaluacion.md', 'é' * 20000)
    view = assessment_context(agent.workspace, 'evaluacion.md')
    assert len(encode(view)) <= 4096 and view['partial']


def test_decision_objective_requires_decision_review_from_evaluator(tmp_path):
    agent, request = setup(tmp_path, calls=1, reports=[report()])
    result = execute(agent, replace(request, objective=objective(assessment_path='evaluacion.md')))
    assert result.stop_reason == 'call_limit' and saved(agent)[0]['status'] == 'failed'


def test_partial_review_survives_failed_attempt_and_is_given_to_next_evaluator(tmp_path):
    partial = decision_report()
    partial['criteria'][1]['status'] = 'no_evaluable'
    agent, request = setup(tmp_path, calls=61, reports=[partial, text('invalid'), decision_report()])
    result = execute(agent, replace(request, objective=objective(assessment_path='evaluacion.md')))
    assert result.stop_reason == 'call_limit'
    third = agent.client.evaluations[2]['input_items'][0].payload['objective_evaluation_packet']
    assert third['previous_evaluation']['status'] == 'partial'
    assert third['previous_evaluation']['decision_review']['blockers'][0]['id'] == 'B1'
    assert saved(agent)[2]['metrics']['delta_distance'] is None


def test_partial_review_recovers_without_inventing_a_complete_distance(tmp_path):
    from research_agent.experiments import prepare_experiment
    from research_agent.objective_review import previous_state
    root = tmp_path / 'managed'
    prompts = prepare_experiment(root, new=True, deliberative=True)
    partial = decision_report()
    partial['criteria'][1]['status'] = 'no_evaluable'
    agent, request = setup(root, calls=1, reports=[partial])
    agent.recorder.experiment = root
    obj = objective(assessment_path='evaluacion.md')
    execute(agent, replace(request, instructions=prompts, objective=obj))
    agent.recorder.current = None
    state = previous_state(agent.recorder, obj)
    assert state.last_valid is None and state.last_valid_reference is None
    assert state.last_review_feedback['historical'] and state.last_review_feedback['status'] == 'partial'


def test_evaluator_packet_can_include_full_assessment_without_enlarging_seed_view(tmp_path):
    from research_agent.objective_review import packet
    from research_agent.external_review import knowledge
    agent, _ = setup(tmp_path)
    content = 'Juicio y fundamentos. ' * 400
    agent.workspace.write_file('evaluacion.md', content)
    obj = objective(assessment_path='evaluacion.md')
    view = assessment_context(agent.workspace, obj.assessment_path)
    assert view['partial'] and len(encode(view)) <= 4096
    data = packet(agent.workspace, obj, knowledge(agent.workspace), None, {}, [])
    assert data['documents'][0]['path'] == 'evaluacion.md'
    assert data['documents'][0]['text'] == content and not data['documents'][0]['partial']
    assert len(encode(data)) <= 65536
