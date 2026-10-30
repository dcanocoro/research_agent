from collections.abc import AsyncIterator
"""Composition root; shared services own transport and provider policy."""
from dataclasses import asdict, replace
from pathlib import Path
from contextlib import asynccontextmanager
from .experiments import disjoint
from .agent import AgentA
from .contracts import AgentLimits
from .recording import RunRecorder
from .tools import ToolRegistry
from .workspace import Workspace


@asynccontextmanager
async def build_agent(workspace: Path, runs: Path, limits: AgentLimits = AgentLimits(), *,
                      experiment: Path | None = None, run_name: str = "intervencion",
                      simulation: Path | None = None, python_enabled: bool = False,
                      state_tools: str = "legacy") -> AsyncIterator[AgentA]:
    if state_tools not in {"legacy", "v5"}:
        raise ValueError("Unknown state tools profile.")
    # Validate experiment paths before constructing clients or database engines.
    disjoint(workspace, runs)
    disjoint(workspace, Path(__file__).parent)
    disjoint(runs, Path(__file__).parent)
    python_config: dict = {"enabled": False}
    if python_enabled:
        from .integrations.python_tools import python_configuration
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
    from .integrations.file_tools import register_files
    from .integrations.findata_tools import FindataTools
    from .integrations.research_tools import register_research
    import hashlib
    import infra
    import runtime_contracts
    import findata
    import research_agent
    factory = LLMFactory(settings)
    profile = replace(configured_profile(settings, "planner"), name="lab")
    space = Workspace(workspace)
    register_files(registry, space, state_tools=state_tools)
    if python_enabled:
        from .integrations.python_tools import register_python
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
        from .simulation.state import Simulator
        from .simulation.tools import register_simulation
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
        yield AgentA(factory.conversation(profile), registry, space, recorder, limits,
                     configuration={**asdict(profile), "code_sha256": fingerprints, "state_mode": "files",
                                    "python_operators": python_config, "state_tools": state_tools, **historical})
    finally:
        await factory.aclose()
        if database is not None:
            database.dispose()
