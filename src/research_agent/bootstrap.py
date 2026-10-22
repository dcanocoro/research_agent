from collections.abc import AsyncIterator
"""Composition root; shared services own transport and provider policy."""
from dataclasses import asdict, replace
from pathlib import Path
from contextlib import asynccontextmanager
from .experiments import ExperimentConfig, disjoint
from .agent import AgentA
from .contracts import AgentLimits
from .recording import RunRecorder
from .tools import ToolRegistry
from .workspace import Workspace


@asynccontextmanager
async def build_agent(workspace: Path, runs: Path, limits: AgentLimits = AgentLimits(), *,
                      experiment: Path | None = None, run_name: str = "intervencion",
                      knowledge_mode: str = "markdown", tool_profile: str = "live",
                      document_paths: tuple[str, ...] = (), document_limit: int | None = None,
                      profile_overrides: dict | None = None) -> AsyncIterator[AgentA]:
    # Validate experiment paths before constructing clients or database engines.
    disjoint(workspace, runs)
    disjoint(workspace, Path(__file__).parent)
    disjoint(runs, Path(__file__).parent)
    mode = ExperimentConfig(knowledge_mode, tool_profile)
    if knowledge_mode == "argumentative" and experiment is None:
        raise ValueError("Argumentative mode requires an experiment")
    if experiment is not None and (experiment / "experimento.json").exists():
        if ExperimentConfig.load(experiment) != mode:
            raise ValueError("Composition must match the fixed experiment configuration")
    recorder = RunRecorder(runs, experiment=experiment, run_name=run_name)
    registry = ToolRegistry(recorder)
    from findata.settings import settings
    from infra.llm_factory import LLMFactory, configured_profile
    from .integrations.file_tools import register_files
    import hashlib
    import infra
    import runtime_contracts
    import findata
    import research_agent
    factory = LLMFactory(settings)
    if profile_overrides:
        from infra.llm_profiles import LLMProfile
        profile = LLMProfile(name="lab", **profile_overrides)
    else:
        profile = replace(configured_profile(settings, "planner"), name="lab")
    space = Workspace(workspace, closed_corpus=tool_profile == "closed-corpus",
                      document_paths=document_paths, document_limit=document_limit)
    register_files(registry, space)
    database = None
    try:
        if tool_profile == "live":
            from sqlalchemy import create_engine
            from sqlalchemy.engine import make_url
            from sqlalchemy.orm import sessionmaker
            from infra.adapters.tavily_web_search import TavilyWebSearchTool
            from infra.adapters.tavily_documents import TavilyDocumentReader
            from .integrations.findata_tools import FindataTools
            from .integrations.research_tools import register_research
            database = create_engine(settings.DATABASE_URL,
                connect_args={"connect_timeout": 10} if make_url(settings.DATABASE_URL).get_backend_name() == "postgresql" else {})
            FindataTools(sessionmaker(bind=database, autoflush=False)).register(registry)
            register_research(registry, TavilyWebSearchTool(api_key=settings.TAVILY_API_KEY, max_results=5),
                              TavilyDocumentReader(api_key=settings.TAVILY_API_KEY))
        if knowledge_mode == "argumentative":
            from .knowledge import KnowledgeStore, register_knowledge
            assert experiment is not None
            path = experiment / "conocimiento/expediente.sqlite"
            disjoint(path.parent, workspace)
            disjoint(path.parent, runs)
            disjoint(path.parent, Path(__file__).parent)
            register_knowledge(registry, KnowledgeStore(path, space))
        fingerprints = {}
        for module in (infra, runtime_contracts, findata, research_agent):
            assert module.__file__ is not None
            package = Path(module.__file__).parent
            hashes = [(str(p.relative_to(package)), hashlib.sha256(p.read_bytes()).hexdigest())
                      for p in sorted(package.rglob("*")) if p.suffix in {".py", ".md"}]
            fingerprints[module.__name__] = hashlib.sha256(repr(hashes).encode()).hexdigest()
        yield AgentA(factory.conversation(profile), registry, space, recorder, limits,
                     configuration={**asdict(profile), "code_sha256": fingerprints, "state_mode": knowledge_mode,
                                    "tool_profile": tool_profile, "document_paths": document_paths, "document_limit": document_limit})
    finally:
        await factory.aclose()
        if database is not None:
            database.dispose()
