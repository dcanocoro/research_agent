import argparse
from pathlib import Path
from research_agent.storage.workspace import Workspace
from research_agent.extensions.deliberation.context import validate_mandate

def resolve_inputs(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    """Resolve repository Markdown inputs before creating clients or output."""
    if args.experiment is None:
        parser.error("Indica --output con la carpeta de salida.")
    if args.name is None:
        if args.message is None or args.run_name is None:
            parser.error("Usa --name CARPETA --output DESTINO --new o --continue.")
        return
    if args.message is not None or args.mandate is not None or args.instructions:
        parser.error("Con --name, edita mandato.md y peticion.md en la carpeta del experimento.")
    if args.max_tools is not None or args.continuous_timeout_seconds is not None:
        parser.error("Con --name no se especifican max-tools ni timeout: se usan los valores predeterminados.")
    folder = args.name
    if not folder.is_dir():
        folder = Path(__file__).resolve().parents[3] / 'campaigns' / folder
    try:
        folder = folder.resolve(strict=True)
        args.mandate = folder / 'mandato.md'
        Workspace._check_links(args.mandate)
        validate_mandate(args.mandate.read_text(encoding='utf-8-sig'))
        request = folder / 'peticion.md'
        Workspace._check_links(request)
        args.message = request.read_text(encoding='utf-8-sig').strip()
        if not args.message:
            raise ValueError('peticion.md debe contener el encargo inicial.')
        if args.objective is None and (folder / 'objetivo.json').is_file():
            args.objective = folder / 'objetivo.json'
    except (OSError, ValueError) as exc:
        parser.error(f'No se puede cargar el experimento {folder}: {exc}')
    if folder.name == 'multiagente' and args.knowledge_agent is None:
        args.knowledge_agent = 'prepared'
    if folder.name == 'progreso':
        args.progress = True
    if args.continuous:
        args.continuous_timeout_seconds = 24 * 60 * 60
        if args.max_calls is None:
            args.max_calls = 100
    args.run_name = args.run_name or ('continuacion' if args.continuing else 'inicial')
