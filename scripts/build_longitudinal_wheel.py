"""Overlay only the two approved shared-source changes on the approved private wheel."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--finmate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    expected = "70cd4a370e1ca4690631f104291a7cc3281acbf6972e43b3c14cb18fe7662e4f"
    if hashlib.sha256(args.base.read_bytes()).hexdigest() != expected:
        raise ValueError("Unapproved base wheel")
    args.output.mkdir(parents=True, exist_ok=False)
    stage = args.output / "source"
    subprocess.run([sys.executable, "-m", "wheel", "unpack", str(args.base), "-d", str(stage)], check=True)
    root = stage / "findata-0.1.0"
    changes = ["findata/read/historical.py", "infra/adapters/tavily_web_search.py"]
    hashes = {}
    source_hashes = {}
    for name in changes:
        source = args.finmate / name
        content = source.read_bytes()
        source_hashes[name] = hashlib.sha256(content).hexdigest()
        if name == "infra/adapters/tavily_web_search.py":
            # develop owns its existing Engine contracts. The approved laboratory
            # wheel owns runtime_contracts; keep that import boundary in the overlay.
            content = content.replace(b"from engine.core.errors import", b"from runtime_contracts.errors import")
            content = content.replace(b"from engine.ports.web_search import", b"from runtime_contracts.search import")
        (root / name).write_bytes(content)
        hashes[name] = hashlib.sha256(content).hexdigest()
    subprocess.run([sys.executable, "-m", "wheel", "pack", str(root), "-d", str(args.output)], check=True)
    wheel = args.output / args.base.name
    # Read the archive as well as hashing it: ensure both overlays were packaged.
    with zipfile.ZipFile(wheel) as archive:
        assert all(hashlib.sha256(archive.read(name)).hexdigest() == hashes[name] for name in changes)
    revision = subprocess.check_output(["git", "-C", str(args.finmate), "rev-parse", "HEAD"], text=True).strip()
    record = {"base_sha256": expected, "finmate_revision": revision,
              "source_sha256": source_hashes, "overlay_sha256": hashes,
              "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
              "note": "Only listed overlays; Tavily Engine imports normalized to approved runtime_contracts for the lab wheel; unrelated dirty files excluded."}
    (args.output / "provenance.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
