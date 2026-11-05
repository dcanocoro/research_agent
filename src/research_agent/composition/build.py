from collections.abc import AsyncIterator
"""Composition root; shared services own transport and provider policy."""
from dataclasses import asdict, replace
from pathlib import Path
from contextlib import asynccontextmanager
from research_agent.experiments.store import disjoint
from research_agent.agent import AgentA
from research_agent.contracts import AgentLimits
from research_agent.observability.recording import RunRecorder
from research_agent.core.tools import ToolRegistry
from research_agent.storage.workspace import Workspace


@asynccontextmanager
async def build_agent(workspace: Path, runs: Path, limits: AgentLimits = AgentLimits(), *,
                      experiment: Path | None = None, run_name: str = "intervencion",
                      simulation: Path | None = None, python_enabled: bool = False,
                      knowledge_agent: str | None = None) -> AsyncIterator[AgentA]:
    from research_agent.composition.configuration import knowledge_mode
    mode = knowledge_mode(experiment, knowledge_agent)
    # Validate experiment paths and frozen interface before constructing clients.
    if experiment is not None:
        from research_agent.experiments.configuration import validate_state_configuration
        validate_state_configuration(experiment)
    disjoint(workspace, runs)
    disjoint(workspace, Path(__file__).parents[1])
    disjoint(runs, Path(__file__).parents[1])
    python_config: dict = {"enabled": False}
    if python_enabled:
        from research_agent.capabilities.python.tools import python_configuration
        python_config = python_configuration()
    recorder = RunRecorder(runs, experiment=experiment, run_name=run_name)
    registry = ToolRegistry(recorder)
    from findata.settings import settings
    from sqlalchemy import create_engine
    from sqlalchemy.engine import make_url
    from sqlalchemy.orm import sessionmaker
    from infra.llm_factory import LLMFactory, configured_profile
    from infra.adapters.tavily_web_search import TavilyWebSearchTool
    from infra.adapters.tavily_documents import TavilyDocumentReader
    from research_agent.capabilities.state.files import register_files
    from research_agent.capabilities.findata.tools import FindataTools
    from research_agent.capabilities.web.tools import register_research
    import hashlib
    import infra
    import runtime_contracts
    import findata
    import research_agent
    factory = LLMFactory(settings)
    profile = replace(configured_profile(settings, "planner"), name="lab")
    space = Workspace(workspace)
    register_files(registry, space, writable=mode == "off")
    if python_enabled:
        from research_agent.capabilities.python.tools import register_python
        register_python(registry, space, python_config)
    database = None
    historical = {}
    search = TavilyWebSearchTool(api_key=settings.TAVILY_API_KEY, max_results=5)
    if simulation is None:
        database = create_engine(settings.DATABASE_URL,
            connect_args={"connect_timeout": 10} if make_url(settings.DATABASE_URL).get_backend_name() == "postgresql" else {})
        FindataTools(sessionmaker(bind=database, autoflush=False)).register(registry)
        register_research(registry, search, TavilyDocumentReader(api_key=settings.TAVILY_API_KEY))
    else:
        from research_agent.capabilities.simulation.state import Simulator
        from research_agent.capabilities.simulation.tools import register_simulation
        disjoint(simulation, workspace)
        disjoint(simulation, runs)
        simulator = Simulator(simulation)
        register_simulation(registry, simulator, search)
        historical = {"simulation": simulator.config, "simulated_date": str(simulator.today)}
    try:
        fingerprints = {}
        for module in (infra, runtime_contracts, findata, research_agent):
            assert module.__file__ is not None
            package = Path(module.__file__).parent
            hashes = [(str(p.relative_to(package)), hashlib.sha256(p.read_bytes()).hexdigest())
                      for p in sorted(package.rglob("*")) if p.suffix in {".py", ".md"}]
            fingerprints[module.__name__] = hashlib.sha256(repr(hashes).encode()).hexdigest()
        agent = AgentA(factory.conversation(profile), registry, space, recorder, limits,
                     configuration={**asdict(profile), "code_sha256": fingerprints, "state_mode": "files",
                                    "python_operators": python_config, "state_tools_contract": "state-tools-e1", **historical})
        if mode != "off":
            from research_agent.extensions.knowledge_agent.delegation import attach
            attach(agent, lambda: factory.conversation(profile), mode)
        yield agent
    finally:
        await factory.aclose()
        if database is not None:
            database.dispose()
