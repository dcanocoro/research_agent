from collections.abc import AsyncIterator
"""Composition root; shared services own transport and provider policy."""
from dataclasses import asdict, replace
from pathlib import Path
from contextlib import asynccontextmanager, ExitStack
from importlib.resources import files, as_file
from .agent import AgentA
from .contracts import AgentLimits
from .recording import RunRecorder
from .tools import ToolRegistry
from .workspace import Workspace


@asynccontextmanager
async def build_agent(workspace: Path, runs: Path, limits: AgentLimits = AgentLimits(), *,
                      case_store: Path | None = None) -> AsyncIterator[AgentA]:
    # Validate experiment paths before constructing clients or database engines.
    recorder = RunRecorder(runs)
    registry = ToolRegistry(recorder)
    store = None
    if case_store is not None:
        from .cases import CaseStore
        from .integrations.case_tools import register_cases
        store = CaseStore(case_store, workspace, recorder)
        register_cases(registry, store)
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
    if space.root.resolve() == runs.resolve() or space.root.resolve() in runs.resolve().parents or runs.resolve() in space.root.resolve().parents:
        raise ValueError("Workspace and audit directory must be disjoint.")
    register_files(registry, space)
    database = create_engine(settings.DATABASE_URL,
        connect_args={"connect_timeout": 10} if make_url(settings.DATABASE_URL).get_backend_name() == "postgresql" else {})
    FindataTools(sessionmaker(bind=database, autoflush=False)).register(registry)
    register_research(registry, TavilyWebSearchTool(api_key=settings.TAVILY_API_KEY, max_results=5),
                      TavilyDocumentReader(api_key=settings.TAVILY_API_KEY))
    try:
        fingerprints = {}
        for module in (infra, runtime_contracts, findata, research_agent):
            assert module.__file__ is not None
            package = Path(module.__file__).parent
            hashes = [(str(p.relative_to(package)), hashlib.sha256(p.read_bytes()).hexdigest())
                      for p in sorted(package.rglob("*")) if p.suffix in {".py", ".md"}]
            fingerprints[module.__name__] = hashlib.sha256(repr(hashes).encode()).hexdigest()
        with ExitStack() as resources:
            instructions: tuple[Path, ...] = ()
            if store is not None:
                prompt = resources.enter_context(as_file(files("research_agent").joinpath("prompts/case_research.md")))
                instructions = (prompt,)
            yield AgentA(factory.conversation(profile), registry, space, recorder, limits,
                         configuration={**asdict(profile), "code_sha256": fingerprints,
                                        "knowledge_mode": "cases" if store else "vanilla",
                                        "case_store": store.binding.model_dump(mode="json") if store else None},
                         instructions=instructions)
    finally:
        await factory.aclose()
        database.dispose()
