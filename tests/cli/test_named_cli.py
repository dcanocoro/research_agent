"""Repository inputs and the short CLI, without provider calls."""
import argparse
from contextlib import asynccontextmanager
from pathlib import Path

import pytest

from research_agent.cli.main import main
from research_agent.cli.main import resolve_inputs
from support.continuous import make, text


@pytest.mark.parametrize('name', ['regimenes', 'progreso', 'multiagente'])
def test_named_selection_uses_repository_inputs(name, tmp_path):
    args = argparse.Namespace(experiment=tmp_path/'out', name=Path(name), message=None,
        mandate=None, instructions=[], max_tools=None, continuous_timeout_seconds=None,
        objective=None, knowledge_agent=None, continuous=True, max_calls=100,
        run_name=None, continuing=False)
    resolve_inputs(argparse.ArgumentParser(), args)
    assert args.mandate.is_file() and args.message.startswith('Investiga')
    assert args.continuous_timeout_seconds == 86400 and args.max_tools is None
    assert args.run_name == 'inicial'
    assert (args.knowledge_agent == 'prepared') == (name == 'multiagente')
    assert (args.objective is not None) == (name == 'progreso')
    assert not args.experiment.exists()


def test_named_create_and_continue_without_message_or_run_name(tmp_path, monkeypatch):
    requests = []

    @asynccontextmanager
    async def build(workspace, runs, limits, **kwargs):
        agent, _ = make(workspace.parent, [text('avance')])
        original = agent.run

        async def capture(request):
            requests.append(request)
            return await original(request)

        agent.run = capture
        yield agent

    monkeypatch.setattr('research_agent.cli.main.build_agent', build)
    output = tmp_path/'out'
    for operation in ('--new', '--continue'):
        assert main(['--name', 'regimenes', '--output', str(output), operation,
                     '--continuous', '--max-calls', '1']) == 0
    assert len(requests) == 2
    assert all(r.continuous.max_tool_calls is None for r in requests)
    assert all(r.continuous.timeout_seconds == 86400 for r in requests)


def test_missing_named_inputs_fail_before_output_or_clients(tmp_path, monkeypatch):
    monkeypatch.setattr('research_agent.cli.main.build_agent', lambda *a, **k: pytest.fail('client built'))
    output = tmp_path/'out'
    with pytest.raises(SystemExit) as error:
        main(['--name', str(tmp_path/'missing'), '--output', str(output), '--new', '--continuous'])
    assert error.value.code == 2 and not output.exists()
