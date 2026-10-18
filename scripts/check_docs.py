"""Check Markdown local links and heading anchors without network access."""
from pathlib import Path
import re
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]\n]*\]\((<[^>]+>|[^)\s]+)\s*(?:\"[^\"]*\")?\)")


def prose(text: str) -> str:
    return re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", text, flags=re.MULTILINE | re.DOTALL)


def anchors(text: str) -> set[str]:
    result = set(re.findall(r'<(?:a|span)\s+[^>]*id=[\"\x27]([^\"\x27]+)', text))
    counts: dict[str, int] = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", prose(text), flags=re.MULTILINE):
        heading = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", heading)
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        number = counts.get(slug, 0)
        result.add(slug if not number else f"{slug}-{number}")
        counts[slug] = number + 1
    return result


def main() -> int:
    files = [ROOT / "README.md", ROOT / "AGENTS.md", *sorted((ROOT / "docs").rglob("*.md"))]
    errors = []
    checked = 0
    for path in files:
        text = prose(path.read_text(encoding="utf-8-sig"))
        for match in LINK.finditer(text):
            target = unquote(match.group(1).strip("<>"))
            if re.match(r"^[a-zA-Z][\w+.-]*:", target):
                continue
            checked += 1
            name, _, fragment = target.partition("#")
            destination = (path.parent / name).resolve() if name else path
            if not destination.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing {target}")
            elif fragment and destination.suffix.lower() == ".md":
                if fragment not in anchors(destination.read_text(encoding="utf-8-sig")):
                    errors.append(f"{path.relative_to(ROOT)}: missing anchor {target}")
    for error in errors:
        print(error)
    print(f"{len(files)} Markdown files; {checked} local links; {len(errors)} errors")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
