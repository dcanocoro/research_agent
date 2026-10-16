from typing import Any
from ..tools import ToolRegistry


def register_research(registry: ToolRegistry, search: Any, reader: Any) -> None:
    async def search_web(query: str) -> Any:
        return await search.search_documents(query)

    async def read_document(url: str, question: str) -> Any:
        return await reader.read(url, query=question)

    string = {"type": "string", "minLength": 1, "maxLength": 4000}
    registry.register("search_web", "Discover sources; snippets are not full documents.", {"query": string}, search_web)
    registry.register("read_document", "Extract and preserve passages relevant to a question; extraction may be partial.",
                      {"url": string, "question": string}, read_document)
