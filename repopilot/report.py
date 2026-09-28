from dataclasses import asdict
import json

def findings_json(findings) -> str:
    return json.dumps([asdict(item) for item in findings], indent=2)

def report_markdown(title: str, sections: dict[str, str]) -> str:
    parts = [f"# {title}", ""]
    for heading, body in sections.items():
        parts.extend([f"## {heading}", "", body.strip(), ""])
    return "\n".join(parts)
