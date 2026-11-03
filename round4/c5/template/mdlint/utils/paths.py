import os

SKIP = {".git", "node_modules", ".venv"}


def markdown_files(targets):
    for t in targets:
        if os.path.isfile(t):
            yield t
            continue
        for root, dirs, files in os.walk(t):
            dirs[:] = sorted(d for d in dirs if d not in SKIP)
            for f in sorted(files):
                if f.endswith((".md", ".markdown")):
                    yield os.path.join(root, f)
