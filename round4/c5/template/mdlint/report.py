import json


def render(problems, fmt="text"):
    if fmt == "json":
        return json.dumps(problems, ensure_ascii=False)
    return "\n".join(f"{p['file']}:{p['line']}: {p['rule']} {p['message']}" for p in problems)
