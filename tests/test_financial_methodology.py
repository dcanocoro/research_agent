"""Mechanical integration only: scripted clients do not validate financial reasoning."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from research_agent.experiments import prepare_experiment


CONTROL = Path(__file__).resolve().parents[1] / "campaigns/analisis-financiero-v1/control"


def test_frozen_control_and_default_replacement(tmp_path):
    provenance = json.loads((CONTROL.parent / "control-provenance.json").read_text(encoding="utf-8"))
    frozen = prepare_experiment(tmp_path / "control", new=True, deliberative=True, instructions_dir=CONTROL)
    current = prepare_experiment(tmp_path / "new", new=True, deliberative=True)
    assert len(frozen) == len(current) == 3
    for path in frozen:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == provenance["sha256"][path.name]
    assert all(a.read_text(encoding="utf-8") != b.read_text(encoding="utf-8") for a, b in zip(frozen, current))
    assert prepare_experiment(tmp_path / "control", new=False, deliberative=True) == frozen
    assert not (tmp_path / "new/estado/empresas").exists()


@pytest.mark.parametrize("problem", ["missing", "extra", "directory", "invalid_utf8", "empty", "baseline"])
def test_bad_bundle_leaves_no_experiment(tmp_path, problem):
    bundle = tmp_path / "bundle"
    shutil.copytree(CONTROL, bundle)
    if problem == "missing":
        (bundle / "agente.md").unlink()
    elif problem == "extra":
        (bundle / "override.md").write_text("ambiguous")
    elif problem == "directory":
        (bundle / "agente.md").unlink()
        (bundle / "agente.md").mkdir()
    elif problem == "invalid_utf8":
        (bundle / "agente.md").write_bytes(b"\xff")
    elif problem == "empty":
        (bundle / "agente.md").write_text(" ")
    with pytest.raises((ValueError, OSError)):
        prepare_experiment(tmp_path / "exp", new=True, deliberative=problem != "baseline", instructions_dir=bundle)
    assert not (tmp_path / "exp").exists()


def test_bundle_cannot_override_continuation_or_additive_instructions(tmp_path):
    root = tmp_path / "exp"
    prepare_experiment(root, new=True, deliberative=True)
    with pytest.raises(ValueError, match="new experiment"):
        prepare_experiment(root, new=False, deliberative=True, instructions_dir=CONTROL)
    with pytest.raises(ValueError, match="additive"):
        prepare_experiment(tmp_path / "other", new=True, deliberative=True,
                           instructions_dir=CONTROL, instructions=(CONTROL / "agente.md",))


@pytest.mark.parametrize("failure", [False, True])
def test_company_recovery_dependency_update_in_fresh_processes(tmp_path, failure):
    root = tmp_path / "exp"
    prepare_experiment(root, new=True, deliberative=True)
    # Each subprocess has a new client and history. The prescribed actions test transport,
    # material references and persistence, never the model's ability to choose those actions.
    code = r'''
import asyncio, json, sys
from pathlib import Path
from research_agent.agent import AgentA
from research_agent.contracts import AgentLimits, AgentRequest
from research_agent.experiments import prepare_experiment
from research_agent.workspace import Workspace
from research_agent.recording import RunRecorder
from research_agent.tools import ToolRegistry
from research_agent.integrations.file_tools import register_files
from runtime_contracts.llm import AssistantResponse, ConversationContext, ResponseFunctionCall, ResponseTurn
root=Path(sys.argv[1]); first=sys.argv[2]=='first'; failure=sys.argv[3]=='True'
space=Workspace(root/'estado'); rec=RunRecorder(root/'ejecuciones',experiment=root)
tools=ToolRegistry(rec); register_files(tools,space)
model='empresas/ACME/modelo.md'; valuation='empresas/ACME/valoracion.md'
evaluation='empresas/ACME/evaluacion.md'
actions=([('calculate',dict(operation='multiply',left=2,right=10,source_refs=['fixture:eps','fixture:multiple'])),
          ('write_file',dict(path=model,content='### H1\nEstado: provisional; EPS supuesto 2 USD.')),
          ('write_file',dict(path=valuation,content='dynamic')),
          ('write_file',dict(path=evaluation,content='Depende de empresas/ACME/valoracion.md#V1; precio ausente.')),
          ('write_file',dict(path='indice.md',content='empresas/ACME/evaluacion.md; '+model+'; '+valuation)),
          ('write_file',dict(path='agenda.md',content='Contrastar H1; afecta a '+valuation+'#V1'))] if first else
         [('read_file',dict(path=model)),('read_file',dict(path=valuation)),
          ('read_file',dict(path=evaluation)),('search_files',dict(query=model+'#H1')),
          ('write_file',dict(path=model,content='### H1\nEstado: revisada; EPS supuesto 1 USD. Antes 2; nueva evidencia fixture:update.')),
          ('write_file',dict(path=valuation,content='### V1\nPendiente de revision tras '+model+'#H1; cifra anterior 20 USD superada.')),
          ('write_file',dict(path=evaluation,content='Revision pendiente: atractivo anterior superado por cambio H1; depende de '+valuation+'#V1.')),
          ('write_file',dict(path='agenda.md',content='Revisar V1 por cambio H1; '+valuation+'#V1'))])
if not first and not failure:
    actions += [
        ('calculate',dict(operation='multiply',left=1,right=10,source_refs=['fixture:update','fixture:multiple'])),
        ('write_file',dict(path=valuation,content='revised')),
        ('write_file',dict(path=evaluation,content='Revision: escenario 10 USD por accion, antes 20; depende de '+valuation+'#V1. Precio compatible ausente; no inferir compra.')),
        ('write_file',dict(path='agenda.md',content='H1 y V1 revisadas; pendiente precio comparable para '+evaluation))]
class Fake:
    count=0
    async def respond(self,**kwargs):
        if self.count==0 and not first:
            items=kwargs['input_items']
            assert not any(getattr(x,'content',None)=='Initial research' for x in items)
            assert any(isinstance(x,ConversationContext) and model in x.payload.get('memory_index',{}).get('text','') for x in items)
            assert any(isinstance(x,ConversationContext) and 'H1' in x.payload.get('deliberative_agenda',{}).get('text','') for x in items)
            assert any('fixture:update: EPS supuesto pasa de 2 a 1 USD' in getattr(x,'content','') for x in items)
        if self.count<len(actions):
            name,args=actions[self.count]; args=dict(args); self.count+=1
            if args.get('content')=='dynamic':
                ref=next(space.path('materiales').glob('*.json')).relative_to(space.root).as_posix()
                assert json.loads(rec.read_artifact(ref)['text'])['result']==20
                args['content']='### V1\n20 USD por accion; depende de '+model+'#H1; fuente '+ref
            if args.get('content')=='revised':
                results=[(f,json.loads(rec.read_artifact(f.relative_to(space.root).as_posix())['text']))
                         for f in space.path('materiales').glob('*.json')]
                file,result=next((f,r) for f,r in results if r['result']==10)
                ref=file.relative_to(space.root).as_posix()
                args['content']='### V1\n10 USD por accion; antes 20, revisado por fixture:update; depende de '+model+'#H1; fuente '+ref
            call=ResponseFunctionCall(str(self.count),name,args)
            return ResponseTurn([call],'',call)
        if failure and not first: raise RuntimeError('Controlled interruption after durable progress')
        return ResponseTurn([AssistantResponse('Saved')],'Saved',None)
paths=prepare_experiment(root,new=False,deliberative=True)
agent=AgentA(Fake(),tools,space,rec,AgentLimits(max_llm_calls=20),instructions=paths)
result=asyncio.run(agent.run(AgentRequest('Initial research' if first else 'Continua. fixture:update: EPS supuesto pasa de 2 a 1 USD; conserva multiplo ilustrativo 10.','state','fresh',mandate='Research only')))
assert result.status==('failed' if failure and not first else 'completed'),result
assert not result.state.capture_errors
if not first:
    assert ('Pendiente' if failure else '10 USD') in space.read_file(valuation)['text']
    assert ('pendiente' if failure else '10 USD') in space.read_file(evaluation)['text']
    assert 'revisada' in space.read_file(model)['text']
    assert space.search_files(model+'#H1')['matches']
    manifest=json.loads((rec.current/'manifiesto.json').read_text(encoding='utf-8'))
    for path in paths:
        assert manifest['prompts'][str(path)]['text']==path.read_text(encoding='utf-8')
'''
    for stage in ("first", "second"):
        result = subprocess.run([sys.executable, "-c", code, str(root), stage, str(failure)],
                                capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
    assert len(list((root / "ejecuciones").glob("*/manifiesto.json"))) == 2
    assert len(list((root / "estado/materiales").glob("*.json"))) == (1 if failure else 2)
